# tests/test_slicer.py
import pytest
from core.slicer import MarkdownSlicer, Slice


class TestSlice:
    def test_slice_creation(self):
        slice = Slice(index=0, content="# Title\n\nContent")
        assert slice.index == 0
        assert slice.content == "# Title\n\nContent"
        assert slice.is_header_only is False

    def test_slice_is_header_only(self):
        slice1 = Slice(index=0, content="# Title\n")
        assert slice1.is_header_only is True

        slice2 = Slice(index=0, content="# Title\n\nSome content")
        assert slice2.is_header_only is False


class TestMarkdownSlicer:
    def test_empty_document(self):
        slicer = MarkdownSlicer("")
        slices = slicer.slice()
        assert len(slices) == 1
        assert slices[0].content == ""

    def test_no_headers(self):
        content = "Some text without headers"
        slicer = MarkdownSlicer(content)
        slices = slicer.slice()
        assert len(slices) == 1
        assert slices[0].content == content

    def test_single_header(self):
        content = "# Title\n\nContent here"
        slicer = MarkdownSlicer(content)
        slices = slicer.slice()
        assert len(slices) == 1
        assert slices[0].content == content

    def test_multiple_headers(self):
        content = """Intro text

# First Section

Content 1

## Subsection

More content

# Second Section

Content 2"""
        slicer = MarkdownSlicer(content)
        slices = slicer.slice()
        assert len(slices) == 3
        assert slices[0].content == "Intro text\n\n"
        assert "# First Section" in slices[1].content
        assert "# Second Section" in slices[2].content

    def test_header_at_start(self):
        content = "# Title\n\nContent"
        slicer = MarkdownSlicer(content)
        slices = slicer.slice()
        # No preamble slice when document starts with header
        assert len(slices) == 1
        assert slices[0].content == content

    def test_subheaders_preserved(self):
        content = """# Main

## Sub 1

### Sub-sub

## Sub 2"""
        slicer = MarkdownSlicer(content)
        slices = slicer.slice()
        assert len(slices) == 1
        assert "## Sub 1" in slices[0].content
        assert "### Sub-sub" in slices[0].content
        assert "## Sub 2" in slices[0].content

    def test_code_blocks_preserved(self):
        content = """# Code Example

```python
def hello():
    print("Hello")
```

More text."""
        slicer = MarkdownSlicer(content)
        slices = slicer.slice()
        assert "```python" in slices[0].content
        assert "```" in slices[0].content

    def test_atx_header_only(self):
        """Only match ATX style headers (# with space), not setext."""
        content = """Title
=====

Some content

# Real Header

More content"""
        slicer = MarkdownSlicer(content)
        slices = slicer.slice()
        # setext header (=====) should not be treated as slice boundary
        assert slices[0].content == "Title\n=====\n\nSome content\n\n"


class TestMarkdownSlicerLevel2:
    def test_level2_splits_on_h2(self):
        content = """# H1

Para 1

## H1.1

Para 2

## H1.2

Para 3

# H2

Para 4"""
        slicer = MarkdownSlicer(content, slicing_level=2)
        slices = slicer.slice()
        # Content starts with # H1 — no preamble slice
        # Slice 0: # H1 + Para 1
        # Slice 1: ## H1.1 + Para 2
        # Slice 2: ## H1.2 + Para 3
        # Slice 3: # H2 + Para 4
        assert len(slices) == 4
        assert "# H1" in slices[0].content
        assert "## H1.1" in slices[1].content
        assert "## H1.2" in slices[2].content
        assert "# H2" in slices[3].content

    def test_level2_preamble(self):
        content = "Preamble\n\n# H1\n\nContent"
        slicer = MarkdownSlicer(content, slicing_level=2)
        slices = slicer.slice()
        assert len(slices) == 2
        assert slices[0].content.strip() == "Preamble"
        assert "# H1" in slices[1].content

    def test_level2_no_h2_acts_like_level1(self):
        content = "# H1\n\nContent\n\n# H2\n\nMore"
        slicer = MarkdownSlicer(content, slicing_level=2)
        slices = slicer.slice()
        # Content starts with header — no empty preamble
        # Slice 0: # H1 + Content
        # Slice 1: # H2 + More
        assert len(slices) == 2
        assert "# H1" in slices[0].content
        assert "# H2" in slices[1].content