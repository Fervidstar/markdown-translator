#!/usr/bin/env python3
"""GUI entry point for md_translator."""
import sys

from PyQt5.QtWidgets import QApplication

from gui.main_window import MainWindow


def main() -> int:
    """Launch the GUI application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Markdown Translator")

    window = MainWindow()
    window.show()

    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())