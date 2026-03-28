# tests/test_assembler.py
import pytest
from core.assembler import Assembler


class TestAssembler:
    def test_assemble_empty_slices(self):
        assembler = Assembler()
        result = assembler.assemble([])
        assert result == ""

    def test_assemble_single_slice(self):
        assembler = Assembler()
        slices = ["# Title\n\nContent"]
        result = assembler.assemble(slices)
        assert result == "# Title\n\nContent"

    def test_assemble_multiple_slices(self):
        assembler = Assembler()
        slices = [
            "Preamble text\n\n",
            "# First Section\n\nContent 1\n\n",
            "# Second Section\n\nContent 2"
        ]
        result = assembler.assemble(slices)
        expected = "Preamble text\n\n# First Section\n\nContent 1\n\n# Second Section\n\nContent 2"
        assert result == expected

    def test_assemble_preserves_ordering(self):
        assembler = Assembler()
        slices = ["Third", "First", "Second"]
        result = assembler.assemble(slices)
        # Note: assembler just joins in order given
        assert result == "ThirdFirstSecond"

    def test_assemble_with_empty_strings(self):
        assembler = Assembler()
        slices = ["First", "", "Third"]
        result = assembler.assemble(slices)
        assert result == "FirstThird"