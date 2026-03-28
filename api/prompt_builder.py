"""Prompt builder for translation requests."""

from typing import Optional


class PromptBuilder:
    """Build prompts for Markdown translation."""

    DEFAULT_TEMPLATE = """请将以下 Markdown 内容翻译成中文，遵循以下规则：
1. 保持原 Markdown 结构不变（标题、列表、代码块等）。
2. 只翻译自然语言文本，不翻译代码块、链接文本、图片描述。
3. 代码块中的注释可以根据语境选择性翻译。

原文：
{content}"""

    def __init__(self, template: Optional[str] = None):
        """
        Initialize prompt builder.

        Args:
            template: Custom prompt template. Must contain {content} placeholder.
        """
        self.template = template if template else self.DEFAULT_TEMPLATE

    def build(self, content: str) -> str:
        """
        Build prompt with content.

        Args:
            content: Markdown content to translate.

        Returns:
            Complete prompt string.
        """
        return self.template.format(content=content)

    @classmethod
    def with_custom_rules(cls, rules: list) -> "PromptBuilder":
        """
        Create builder with custom translation rules.

        Args:
            rules: List of rule strings.

        Returns:
            PromptBuilder instance.
        """
        rules_text = "\n".join(f"{i}. {rule}" for i, rule in enumerate(rules, 1))
        template = f"""请将以下 Markdown 内容翻译成中文，遵循以下规则：
{rules_text}

原文：
{{content}}"""
        return cls(template=template)