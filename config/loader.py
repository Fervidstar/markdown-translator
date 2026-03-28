"""Configuration loader for YAML and environment variables."""

import os
from pathlib import Path
from typing import Optional

import yaml
from dotenv import dotenv_values

from .models import APIConfig, AppConfig


class ConfigLoader:
    """Load and manage application configuration."""

    def __init__(
        self,
        config_path: str = "config.yaml",
        env_path: str = ".env"
    ):
        self.config_path = Path(config_path)
        self.env_path = Path(env_path)

    def load(self) -> AppConfig:
        """Load configuration from YAML file with defaults."""
        config_data = self._load_yaml()
        return self._parse_config(config_data)

    def get_api_key(self) -> Optional[str]:
        """Load API key from environment file only."""
        if not self.env_path.exists():
            return None
        env_values = dotenv_values(self.env_path)
        return env_values.get("OPENAI_API_KEY")

    def validate_config(self, api_key: Optional[str]) -> None:
        """Validate that required configuration is present."""
        if api_key is None:
            raise ValueError(
                "API key is required. Set OPENAI_API_KEY in .env file "
                "or environment variable."
            )

    def _load_yaml(self) -> dict:
        """Load YAML configuration file."""
        if not self.config_path.exists():
            return {}

        with open(self.config_path, "r", encoding="utf-8") as f:
            content = yaml.safe_load(f)
            return content if content else {}

    def _parse_config(self, config_data: dict) -> AppConfig:
        """Parse YAML data into AppConfig model."""
        api_data = config_data.get("api", {})
        api_config = APIConfig(
            base_url=api_data.get("base_url", APIConfig.__dataclass_fields__["base_url"].default),
            model=api_data.get("model", APIConfig.__dataclass_fields__["model"].default),
            temperature=api_data.get("temperature", APIConfig.__dataclass_fields__["temperature"].default),
            max_tokens=api_data.get("max_tokens", APIConfig.__dataclass_fields__["max_tokens"].default),
        )

        return AppConfig(
            api=api_config,
            concurrency=config_data.get("concurrency", AppConfig.__dataclass_fields__["concurrency"].default),
            prompt=config_data.get("prompt", ""),
            slicing_level=config_data.get("slicing_level", AppConfig.__dataclass_fields__["slicing_level"].default),
        )