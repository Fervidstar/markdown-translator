"""File operation utilities."""

from pathlib import Path
from typing import Optional


def read_file(file_path: str, encoding: str = "utf-8") -> str:
    """
    Read content from a file.

    Args:
        file_path: Path to the file.
        encoding: File encoding (default: utf-8).

    Returns:
        File content as string.

    Raises:
        FileNotFoundError: If file does not exist.
        UnicodeDecodeError: If file cannot be decoded with specified encoding.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(path, "r", encoding=encoding) as f:
        return f.read()


def write_file(file_path: str, content: str, encoding: str = "utf-8") -> None:
    """
    Write content to a file.

    Args:
        file_path: Path to the file.
        content: Content to write.
        encoding: File encoding (default: utf-8).
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding=encoding) as f:
        f.write(content)


def get_output_path(input_path: str) -> str:
    """
    Generate output file path from input path.

    Args:
        input_path: Path to input file.

    Returns:
        Path for output file with _translated suffix.
    """
    path = Path(input_path)
    stem = path.stem  # filename without extension
    parent = path.parent  # directory
    return str(parent / f"{stem}_translated.md")