"""Markdown document slicer based on level-1 headers."""

import re
from dataclasses import dataclass
from typing import List


# Pre-compiled patterns
_HEADER_PATTERN_L1 = re.compile(r'^# ', re.MULTILINE)
_HEADER_PATTERN_L2 = re.compile(r'^#{1,2} ', re.MULTILINE)


@dataclass
class Slice:
    """Represents a slice of Markdown content."""
    index: int
    content: str

    @property
    def is_header_only(self) -> bool:
        """Check if slice contains only a header with no substantial content."""
        # Remove the header line and check if anything meaningful remains
        lines = self.content.strip().split("\n")
        if len(lines) <= 1:
            return True
        # Check if there's content beyond whitespace
        content_lines = [l for l in lines[1:] if l.strip()]
        return len(content_lines) == 0


class MarkdownSlicer:
    """
    Slice Markdown documents by level-1 (or level-1+2) headers.

    Slicing rules:
    - Content from start to first header (exclusive) is first slice (preamble)
    - Each header and its content until next matching header is a slice
    - Level 1 (slicing_level=1): only '# ' headers
    - Level 2 (slicing_level=2): both '# ' and '## ' headers
    - Only matches ATX-style headers: '# ' or '## ' followed by space
    """

    def __init__(self, content: str, slicing_level: int = 1):
        if slicing_level not in (1, 2):
            raise ValueError("slicing_level must be 1 or 2")
        self.content = content
        self.slicing_level = slicing_level

    @property
    def _header_pattern(self):
        if self.slicing_level >= 2:
            return _HEADER_PATTERN_L2
        return _HEADER_PATTERN_L1

    def slice(self) -> List[Slice]:
        """
        Slice the document by configured header level(s).

        Returns:
            List of Slice objects in document order.
        """
        if not self.content:
            return [Slice(index=0, content="")]

        matches = list(self._header_pattern.finditer(self.content))

        if not matches:
            return [Slice(index=0, content=self.content)]

        slices = []
        slice_index = 0

        # Preamble: content before first header
        first_match_pos = matches[0].start()
        if first_match_pos > 0:
            preamble = self.content[:first_match_pos]
            if preamble.strip():
                slices.append(Slice(index=slice_index, content=preamble))
                slice_index += 1

        # Create slices for each header
        for i, match in enumerate(matches):
            start_pos = match.start()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(self.content)
            slice_content = self.content[start_pos:end_pos]
            slices.append(Slice(index=slice_index, content=slice_content))
            slice_index += 1

        return slices

    @staticmethod
    def count_headers(content: str, slicing_level: int = 1) -> int:
        """Count headers at the given level in content."""
        if slicing_level >= 2:
            return len(_HEADER_PATTERN_L2.findall(content))
        return len(_HEADER_PATTERN_L1.findall(content))