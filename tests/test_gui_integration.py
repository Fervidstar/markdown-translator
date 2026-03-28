"""Integration tests for GUI components."""
import sys

import pytest
from PyQt5.QtWidgets import QApplication


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_file_selector_io(qapp):
    """Test FileSelector can set and get paths."""
    from gui.widgets import FileSelector

    widget = FileSelector()
    # Test initial state
    assert widget.get_input_path() is None
    assert widget.get_output_path() is None


def test_log_viewer_append(qapp):
    """Test LogViewer can append messages."""
    from gui.widgets import LogViewer

    widget = LogViewer()
    widget.append_log("Test message")
    assert "Test message" in widget.log_text.toPlainText()


def test_config_panel_get_set(qapp):
    """Test ConfigPanel can get and set config."""
    from gui.widgets import ConfigPanel

    widget = ConfigPanel()
    widget.set_config({
        "api_key": "test-key",
        "base_url": "https://test.com",
        "model": "test-model",
        "concurrency": 4,
    })

    config = widget.get_config()
    assert config["api_key"] == "test-key"
    assert config["base_url"] == "https://test.com"
    assert config["model"] == "test-model"
    assert config["concurrency"] == 4
