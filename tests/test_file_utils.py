# tests/test_file_utils.py
import pytest
from pathlib import Path
from utils.file_utils import read_file, write_file, get_output_path


class TestReadFile:
    def test_read_existing_file(self, temp_text_file):
        content = read_file(temp_text_file)
        assert content == "Hello, World!"

    def test_read_nonexistent_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            read_file(str(tmp_path / "nonexistent.txt"))

    def test_read_non_utf8_file(self, temp_latin1_file):
        # Should handle or raise appropriate error
        with pytest.raises(UnicodeDecodeError):
            read_file(temp_latin1_file)


class TestWriteFile:
    def test_write_new_file(self, tmp_path):
        output_path = str(tmp_path / "output.txt")
        write_file(output_path, "Test content")
        assert Path(output_path).exists()
        assert Path(output_path).read_text(encoding="utf-8") == "Test content"

    def test_overwrite_existing_file(self, temp_text_file):
        write_file(temp_text_file, "New content")
        assert Path(temp_text_file).exists()
        assert Path(temp_text_file).read_text(encoding="utf-8") == "New content"


class TestGetOutputPath:
    def test_output_path_with_md_extension(self):
        output = get_output_path("input.md")
        assert output == "input_translated.md"

    def test_output_path_without_extension(self):
        output = get_output_path("input")
        assert output == "input_translated.md"

    def test_output_path_with_different_extension(self):
        output = get_output_path("input.txt")
        assert output == "input_translated.md"

    def test_output_path_with_directory(self):
        output = get_output_path("docs/input.md")
        # Normalize paths for cross-platform comparison
        assert Path(output) == Path("docs/input_translated.md")


@pytest.fixture
def temp_text_file(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("Hello, World!", encoding="utf-8")
    return str(file_path)


@pytest.fixture
def temp_latin1_file(tmp_path):
    file_path = tmp_path / "latin1.txt"
    # Write some Latin-1 encoded content
    with open(file_path, "wb") as f:
        f.write(b"\xe4\xf6\xfc")  # Latin-1 characters
    return str(file_path)