# tests/test_prompt_builder.py
import pytest
from api.prompt_builder import PromptBuilder


class TestPromptBuilder:
    def test_default_prompt_template(self):
        builder = PromptBuilder()
        assert "{content}" in builder.template

    def test_custom_prompt_template(self):
        custom = "Custom template: {content}"
        builder = PromptBuilder(template=custom)
        assert builder.template == custom

    def test_build_prompt(self):
        builder = PromptBuilder()
        content = "This is test content"
        prompt = builder.build(content)
        assert "This is test content" in prompt
        assert "翻译" in prompt or "Translate" in prompt

    def test_build_prompt_preserves_content(self):
        builder = PromptBuilder()
        content = "# Header\n\n```code\n```\n\nText"
        prompt = builder.build(content)
        assert content in prompt

    def test_build_prompt_with_special_characters(self):
        builder = PromptBuilder()
        content = "Special: <>&\"'\n中文测试"
        prompt = builder.build(content)
        assert content in prompt