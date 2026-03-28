#!/usr/bin/env python3
"""
Markdown Document Translator

Translates Markdown documents using OpenAI Compatible API.
Slices document by level-1 headers and translates each slice.
"""

import sys
from pathlib import Path

from cli.parser import parse_args
from config.loader import ConfigLoader
from config.models import AppConfig
from core.slicer import MarkdownSlicer
from core.translator import Translator
from core.assembler import Assembler
from utils.file_utils import read_file, write_file, get_output_path
from utils.logger import get_logger, LoggerSetup


def main() -> int:
    """Main entry point."""
    args = parse_args()

    # Setup logging
    logger_setup = LoggerSetup()
    logger = logger_setup.get_logger()

    # Validate input file exists
    input_path = Path(args.input_file)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return 1

    # Load configuration
    config_loader = ConfigLoader(
        config_path=args.config,
        env_path=args.env
    )
    config = config_loader.load()
    api_key = config_loader.get_api_key()

    # Validate API key
    try:
        config_loader.validate_config(api_key)
    except ValueError as e:
        logger.error(str(e))
        return 1

    # Read input file
    try:
        content = read_file(str(input_path))
    except UnicodeDecodeError as e:
        logger.error(f"Failed to read file (must be UTF-8): {e}")
        logger.error("Please convert your file to UTF-8 encoding and try again.")
        return 1
    except Exception as e:
        logger.error(f"Failed to read input file: {e}")
        return 1

    # Generate output path
    output_path = get_output_path(str(input_path))
    logger.log_start(str(input_path), output_path) 

    # Slice document
    slicer = MarkdownSlicer(content, slicing_level=config.slicing_level)
    slices = slicer.slice()
    logger.info(f"文档已切分为 {len(slices)} 个部分")

    # Translate slices
    translator = Translator(config=config, api_key=api_key)
    result = translator.translate(slices)

    # Assemble result
    assembler = Assembler()
    translated_content = assembler.assemble(result.slices)

    # Write output
    try:
        write_file(output_path, translated_content)
        logger.info(f"输出已保存：{output_path}")
    except Exception as e:
        logger.error(f"Failed to write output file: {e}")
        return 1

    # Log summary
    logger.log_complete(
        total=len(slices),
        success=result.success_count,
        errors=result.error_count,
        duration=result.total_duration
    )

    # Return error code if any translations failed
    return 1 if result.error_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())