# tests/test_config_loader.py
import pytest
import os
import tempfile
from config.loader import ConfigLoader
from config.models import APIConfig, AppConfig


class TestAPIConfig:
    def test_default_values(self):
        config = APIConfig()
        assert config.base_url == "https://api.openai.com/v1"
        assert config.model == "gpt-3.5-turbo"
        assert config.temperature == 0.7
        assert config.max_tokens == 2048

    def test_custom_values(self):
        config = APIConfig(
            base_url="https://custom.api.com/v1",
            model="gpt-4",
            temperature=0.5,
            max_tokens=4096
        )
        assert config.base_url == "https://custom.api.com/v1"
        assert config.model == "gpt-4"
        assert config.temperature == 0.5
        assert config.max_tokens == 4096


class TestConfigLoader:
    def test_load_config_with_existing_file(self, temp_config_file):
        loader = ConfigLoader(config_path=temp_config_file)
        config = loader.load()
        assert config.api.base_url == "https://test.api.com/v1"
        assert config.api.model == "test-model"
        assert config.concurrency == 2

    def test_load_config_missing_file_uses_defaults(self, tmp_path):
        loader = ConfigLoader(config_path=str(tmp_path / "nonexistent.yaml"))
        config = loader.load()
        assert config.api.base_url == "https://api.openai.com/v1"
        assert config.concurrency == 1

    def test_load_env_variable(self, temp_env_file):
        loader = ConfigLoader(env_path=temp_env_file)
        api_key = loader.get_api_key()
        assert api_key == "test-api-key-123"

    def test_load_env_variable_missing(self, tmp_path):
        loader = ConfigLoader(env_path=str(tmp_path / "nonexistent.env"))
        api_key = loader.get_api_key()
        assert api_key is None

    def test_validate_api_key_required(self):
        loader = ConfigLoader()
        # Should raise error when API key is missing
        with pytest.raises(ValueError, match="API key is required"):
            loader.validate_config(api_key=None)


@pytest.fixture
def temp_config_file(tmp_path):
    content = """
api:
  base_url: "https://test.api.com/v1"
  model: "test-model"
  temperature: 0.5
  max_tokens: 4096
concurrency: 2
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(content)
    return str(config_file)


def test_load_slicing_level_default(tmp_path):
    nonexistent = tmp_path / "nonexistent.yaml"
    loader = ConfigLoader(config_path=str(nonexistent), env_path=str(tmp_path / ".env"))
    config = loader.load()
    assert config.slicing_level == 1

def test_load_slicing_level_from_yaml(tmp_path):
    yaml_content = "api:\n  base_url: http://test\n  model: test\nslicing_level: 2\n"
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml_content)
    loader = ConfigLoader(config_path=str(config_file), env_path=".env")
    config = loader.load()
    assert config.slicing_level == 2
