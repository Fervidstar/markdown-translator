"""Command-line argument parser."""

import argparse


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        prog="md-translator",
        description="Translate Markdown documents using LLM APIs"
    )

    parser.add_argument(
        "input_file",
        help="Path to the input Markdown file"
    )

    parser.add_argument(
        "-c", "--config",
        default="config.yaml",
        help="Path to config.yaml (default: config.yaml)"
    )

    parser.add_argument(
        "-e", "--env",
        default=".env",
        help="Path to .env file (default: .env)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    return parser


def parse_args(args=None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = create_parser()
    return parser.parse_args(args)