# tests/test_cli.py
import pytest
from cli.parser import create_parser, parse_args


class TestArgumentParser:
    def test_valid_input_file(self):
        parser = create_parser()
        args = parser.parse_args(["input.md"])
        assert args.input_file == "input.md"

    def test_missing_input_file(self):
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_config_path_option(self):
        parser = create_parser()
        args = parser.parse_args(["-c", "custom.yaml", "input.md"])
        assert args.config == "custom.yaml"

    def test_env_path_option(self):
        parser = create_parser()
        args = parser.parse_args(["-e", ".env.prod", "input.md"])
        assert args.env == ".env.prod"

    def test_verbose_flag(self):
        parser = create_parser()
        args = parser.parse_args(["-v", "input.md"])
        assert args.verbose is True

    def test_default_values(self):
        parser = create_parser()
        args = parser.parse_args(["input.md"])
        assert args.config == "config.yaml"
        assert args.env == ".env"
        assert args.verbose is False