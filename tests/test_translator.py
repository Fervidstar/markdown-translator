# tests/test_translator.py
import pytest
from unittest.mock import Mock, patch
from core.translator import Translator, TranslationResult
from core.slicer import Slice
from config.models import APIConfig, AppConfig
from api.client import APIClient


class TestTranslationResult:
    def test_result_creation(self):
        result = TranslationResult(
            slices=["translated"],
            errors=[(0, "API error")],
            total_duration=10.5
        )
        assert result.slices == ["translated"]
        assert len(result.errors) == 1
        assert result.success_count == 0
        assert result.error_count == 1


class TestTranslator:
    @pytest.fixture
    def sample_config(self):
        return AppConfig(
            api=APIConfig(
                base_url="https://test.api.com/v1",
                model="test-model"
            ),
            concurrency=1,
            prompt="Translate: {content}"
        )

    @pytest.fixture
    def translator(self, sample_config):
        return Translator(config=sample_config, api_key="test-key")

    @patch("core.translator.APIClient")
    @patch("core.translator.PromptBuilder")
    def test_translate_single_slice(self, mock_prompt_builder, mock_client_class, translator):
        mock_client = Mock()
        mock_client.translate.return_value = "Translated content"
        mock_client_class.return_value = mock_client

        mock_prompt_builder_instance = Mock()
        mock_prompt_builder_instance.build.return_value = "Prompt here"
        mock_prompt_builder.return_value = mock_prompt_builder_instance

        slices = [Slice(index=0, content="Original content")]
        result = translator.translate(slices)

        assert len(result.slices) == 1
        assert result.slices[0] == "Translated content"
        assert len(result.errors) == 0

    @patch("core.translator.APIClient")
    @patch("core.translator.PromptBuilder")
    def test_translate_with_error(self, mock_prompt_builder, mock_client_class, translator):
        mock_client = Mock()
        mock_client.translate.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client

        mock_prompt_builder_instance = Mock()
        mock_prompt_builder_instance.build.return_value = "Prompt"
        mock_prompt_builder.return_value = mock_prompt_builder_instance

        slices = [Slice(index=0, content="Original content")]
        result = translator.translate(slices)

        assert len(result.slices) == 1
        assert result.slices[0] == "Original content"  # Original preserved on error
        assert len(result.errors) == 1

    @patch("core.translator.APIClient")
    def test_concurrent_execution(self, mock_client_class, sample_config):
        # Test that concurrency setting is respected
        config = AppConfig(
            api=APIConfig(),
            concurrency=3,
            prompt="Translate: {content}"
        )
        translator = Translator(config=config, api_key="test-key")
        assert translator.concurrency == 3