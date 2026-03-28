"""Assemble translated slices into final document."""

from typing import List


class Assembler:
    """Assemble translated slices into final Markdown document."""

    def assemble(self, slices: List[str]) -> str:
        """
        Assemble slices in order.

        Args:
            slices: List of translated slice contents.

        Returns:
            Assembled Markdown document.
        """
        return "\n\n".join(slices)