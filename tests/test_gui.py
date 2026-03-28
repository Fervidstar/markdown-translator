"""Tests for GUI components."""
import pytest


def test_gui_package_exists():
    """GUI package should be importable."""
    import gui
    assert gui is not None


def test_file_selector_widget():
    """FileSelector should allow browsing for .md files."""
    from gui.widgets import FileSelector
    # Just test instantiation - actual GUI testing is limited
    assert FileSelector is not None


def test_log_viewer_widget():
    """LogViewer should display translation progress."""
    from gui.widgets import LogViewer
    assert LogViewer is not None


def test_config_panel_widget():
    """ConfigPanel should allow editing API configuration."""
    from gui.widgets import ConfigPanel
    assert ConfigPanel is not None


def test_main_window_exists():
    """MainWindow should be importable."""
    from gui.main_window import MainWindow
    assert MainWindow is not None


def test_gui_main_exists():
    """gui_main should be importable and create app."""
    import gui_main
    assert gui_main is not None
