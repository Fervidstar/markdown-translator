"""Configuration data models."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class APIConfig:
    """API configuration settings."""
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 2048

    def __post_init__(self):
        """Validate configuration values."""
        if not self.base_url:
            raise ValueError("base_url cannot be empty")
        if not self.model:
            raise ValueError("model cannot be empty")
        if not 0 <= self.temperature <= 2:
            raise ValueError("temperature must be between 0 and 2")
        if self.max_tokens < 1:
            raise ValueError("max_tokens must be at least 1")


@dataclass
class AppConfig:
    """Application configuration settings."""
    api: APIConfig = field(default_factory=APIConfig)
    concurrency: int = 1
    prompt: str = ""
    slicing_level: int = 1

    def __post_init__(self):
        """Validate configuration values."""
        if self.concurrency < 1:
            raise ValueError("concurrency must be at least 1")
        if self.slicing_level not in (1, 2):
            raise ValueError("slicing_level must be 1 (h1 only) or 2 (h1 + h2)")