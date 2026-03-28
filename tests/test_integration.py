# tests/test_integration.py
"""Integration tests for the full translation workflow."""

import pytest
from pathlib import Path
from unittest.mock import patch, Mock

from config.loader import ConfigLoader
from core.slicer import MarkdownSlicer
from core.translator import Translator
from core.assembler import Assembler
from utils.file_utils import read_file, write_file, get_output_path


class TestIntegration:
    """Test the complete translation workflow."""

    @pytest.fixture
    def full_config(self, temp_config_file, temp_env_file):
        """Load full configuration."""
        loader = ConfigLoader(
            config_path=temp_config_file,
            env_path=temp_env_file
        )
        config = loader.load()
        api_key = loader.get_api_key()
        return config, api_key

    def test_full_workflow(self, full_config, sample_markdown):
        """Test complete workflow from slicing to assembly."""
        config, api_key = full_config

        # Slice
        slicer = MarkdownSlicer(sample_markdown)
        slices = slicer.slice()
        assert len(slices) == 4  # 4 headers in sample_markdown

        # Mock translation
        with patch("api.client.requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Translated"}}]
            }
            mock_post.return_value = mock_response

            # Translate
            translator = Translator(config=config, api_key=api_key)
            result = translator.translate(slices)

            assert len(result.slices) == len(slices)
            assert result.error_count == 0

            # Assemble
            assembler = Assembler()
            final_content = assembler.assemble(result.slices)

            assert "Translated" in final_content

    def test_error_handling_in_workflow(self, full_config, sample_markdown):
        """Test that errors are handled gracefully."""
        config, api_key = full_config

        slicer = MarkdownSlicer(sample_markdown)
        slices = slicer.slice()

        # Mock API failure
        with patch("api.client.requests.post") as mock_post:
            mock_post.side_effect = Exception("API unavailable")

            translator = Translator(config=config, api_key=api_key)
            result = translator.translate(slices)

            # Should preserve original content on error
            assert result.error_count > 0
            # Original content should be preserved
            for i, slice_content in enumerate(result.slices):
                if i < len(slices):
                    assert slice_content == slices[i].content