# tests/conftest.py
"""Pytest fixtures and configuration."""

import pytest
from pathlib import Path


@pytest.fixture
def sample_markdown():
    """Sample Markdown content for testing."""
    return """# Introduction

This is the introduction.

## Background

Some background information.

# Main Content

This is the main content.

```python
# Code block
def hello():
    print("Hello")
```

# Conclusion

Final thoughts."""


@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary config file."""
    content = """
api:
  base_url: "https://api.openai.com/v1"
  model: "gpt-3.5-turbo"
  temperature: 0.7
  max_tokens: 2048
concurrency: 1
prompt: |
  Translate: {content}
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(content, encoding="utf-8")
    return str(config_file)


@pytest.fixture
def temp_env_file(tmp_path):
    """Create a temporary .env file."""
    content = "OPENAI_API_KEY=test-key-12345\n"
    env_file = tmp_path / ".env"
    env_file.write_text(content, encoding="utf-8")
    return str(env_file)


@pytest.fixture
def temp_markdown_file(tmp_path):
    """Create a temporary Markdown file."""
    content = """# Test Document

This is test content.

## Section

More test content."""
    file_path = tmp_path / "test.md"
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)