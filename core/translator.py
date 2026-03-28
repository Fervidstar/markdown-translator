"""Translation orchestrator."""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Tuple, Optional

from .slicer import Slice
from api.client import APIClient, APIError
from api.prompt_builder import PromptBuilder
from config.models import AppConfig
from utils.logger import get_logger


@dataclass
class TranslationResult:
    """Result of translation process."""
    slices: List[str]
    errors: List[Tuple[int, str]]  # (slice_index, error_message)
    total_duration: float = 0.0

    @property
    def success_count(self) -> int:
        return len(self.slices) - len(self.errors)

    @property
    def error_count(self) -> int:
        return len(self.errors)


class Translator:
    """Orchestrate the translation process."""

    def __init__(self, config: AppConfig, api_key: str):
        self.config = config
        self.api_key = api_key
        self.concurrency = config.concurrency
        self.logger = get_logger()

    def translate(self, slices: List[Slice]) -> TranslationResult:
        """
        Translate all slices.

        Args:
            slices: List of slices to translate.

        Returns:
            TranslationResult with translated content and any errors.
        """
        start_time = time.time()
        results: List[Optional[str]] = [None] * len(slices)
        errors: List[Tuple[int, str]] = []

        if self.concurrency == 1:
            # Sequential processing
            for i, slice_obj in enumerate(slices):
                results[i], error = self._translate_slice(slice_obj, i, len(slices))
                if error:
                    errors.append((i, error))
        else:
            # Concurrent processing
            results, errors = self._translate_concurrent(slices)

        duration = time.time() - start_time

        # Replace None with original content for failed slices
        final_results = [
            results[i] if results[i] is not None else slices[i].content
            for i in range(len(slices))
        ]

        return TranslationResult(
            slices=final_results,
            errors=errors,
            total_duration=duration
        )

    def _translate_concurrent(
        self,
        slices: List[Slice]
    ) -> Tuple[List[Optional[str]], List[Tuple[int, str]]]:
        """Translate slices concurrently."""
        results: List[Optional[str]] = [None] * len(slices)
        errors: List[Tuple[int, str]] = []

        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            future_to_index = {
                executor.submit(self._translate_single, slice_obj): i
                for i, slice_obj in enumerate(slices)
            }

            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    results[index] = future.result()
                except Exception as e:
                    errors.append((index, str(e)))
                    self.logger.error(f"Slice {index + 1} failed: {e}")

        return results, errors

    def _translate_single(self, slice_obj: Slice) -> str:
        """Translate a single slice."""
        client = APIClient(config=self.config.api, api_key=self.api_key)
        builder = PromptBuilder(template=self.config.prompt)
        prompt = builder.build(slice_obj.content)
        return client.translate(slice_obj.content, prompt)

    def _translate_slice(
        self,
        slice_obj: Slice,
        index: int,
        total: int
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Translate a single slice with logging.

        Returns:
            Tuple of (translated_content or None, error_message or None)
        """
        start = time.time()
        try:
            result = self._translate_single(slice_obj)
            duration = time.time() - start
            self.logger.log_slice_status(index, total, "success", duration)
            return result, None

        except (APIError, Exception) as e:
            duration = time.time() - start
            error_msg = str(e)
            self.logger.log_slice_status(index, total, "error", duration, error_msg)
            return None, error_msg