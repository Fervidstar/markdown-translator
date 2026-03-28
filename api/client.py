"""API client for OpenAI Compatible endpoints."""

from typing import Optional

from openai import OpenAI
from openai import APIError as OpenAIAPIError
from openai import APITimeoutError, RateLimitError

from config.models import APIConfig


class APIError(Exception):
    """Exception raised for API-related errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.__str__())

    def __str__(self) -> str:
        if self.status_code:
            return f"API error ({self.status_code}): {self.message}"
        return f"API error: {self.message}"


class APIClient:
    """Client for OpenAI Compatible API endpoints."""

    def __init__(
        self,
        config: APIConfig,
        api_key: str,
        timeout: int = 30
    ):
        if not api_key:
            raise ValueError("API key is required")

        self.client = OpenAI(
            api_key=api_key,
            base_url=config.base_url.rstrip("/"),
            timeout=timeout
        )
        self.model = config.model
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens

    def translate(
        self,
        content: str,
        prompt: str,
        retry: bool = True
    ) -> str:
        """
        Send content for translation via API.

        Args:
            content: Content to translate.
            prompt: Prompt template with content already inserted.
            retry: Whether to retry on failure (default: True).

        Returns:
            Translated content.

        Raises:
            APIError: If the API request fails.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content.strip()

        except APITimeoutError:
            if retry:
                return self._retry_translate(content, prompt)
            raise APIError("Request timeout", status_code=408)

        except RateLimitError as e:
            if retry:
                return self._retry_translate(content, prompt)
            raise APIError(str(e), status_code=429)

        except OpenAIAPIError as e:
            status_code = getattr(e, "status_code", None)
            raise APIError(str(e), status_code=status_code)

    def _retry_translate(self, content: str, prompt: str) -> str:
        """Retry the translation once."""
        return self.translate(content, prompt, retry=False)