"""Custom widgets for the GUI."""
from pathlib import Path
from typing import Optional, Callable

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLineEdit,
    QPushButton, QLabel, QFileDialog, QGroupBox, QPlainTextEdit
)
from PyQt5.QtCore import pyqtSignal


class FileSelector(QWidget):
    """Widget for selecting input/output markdown files."""

    file_selected = pyqtSignal(str)  # Emits selected file path

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Input file row
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("输入文件:"))
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("选择 Markdown 文件...")
        self.input_edit.setReadOnly(True)
        input_layout.addWidget(self.input_edit)
        self.browse_btn = QPushButton("浏览...")
        input_layout.addWidget(self.browse_btn)
        layout.addLayout(input_layout)

        # Output file row
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("输出文件:"))
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("自动生成或手动指定...")
        self.output_edit.setReadOnly(True)
        output_layout.addWidget(self.output_edit)
        self.output_btn = QPushButton("浏览...")
        output_layout.addWidget(self.output_btn)
        layout.addLayout(output_layout)

        # Connect signals
        self.browse_btn.clicked.connect(self._browse_input)
        self.output_btn.clicked.connect(lambda: self._browse_output(force=True))

    def _browse_input(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "选择 Markdown 文件", "", "Markdown Files (*.md *.markdown);;All Files (*)"
        )
        if path:
            self.input_edit.setText(path)
            self.file_selected.emit(path)
            # Auto-set output path
            p = Path(path)
            self.output_edit.setText(str(p.parent / f"{p.stem}_translated.md"))

    def _browse_output(self, force: bool = True) -> None:
        if force or not self.output_edit.text():
            path, _ = QFileDialog.getSaveFileName(
                self, "保存翻译结果", self.output_edit.text() or "", "Markdown Files (*.md)"
            )
            if path:
                self.output_edit.setText(path)

    def get_input_path(self) -> Optional[str]:
        return self.input_edit.text() or None

    def get_output_path(self) -> Optional[str]:
        return self.output_edit.text() or None


class LogViewer(QWidget):
    """Widget for displaying translation logs and progress."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 0)

        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        layout.addWidget(QLabel("翻译进度:"))
        layout.addWidget(self.log_text)

    def append_log(self, message: str) -> None:
        """Append a message to the log."""
        self.log_text.appendPlainText(message)

    def set_progress(self, current: int, total: int, status: str) -> None:
        """Update progress display."""
        self.log_text.appendPlainText(f"[{current}/{total}] {status}")

    def clear(self) -> None:
        """Clear the log."""
        self.log_text.clear()


class ConfigPanel(QWidget):
    """Widget for configuring API settings."""

    config_changed = pyqtSignal(dict)  # Emits updated config dict

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        group = QGroupBox("API 配置")
        group_layout = QVBoxLayout()

        # API Key
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(QLabel("API Key:"))
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setPlaceholderText("sk-...")
        api_key_layout.addWidget(self.api_key_edit)
        group_layout.addLayout(api_key_layout)

        # Base URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Base URL:"))
        self.base_url_edit = QLineEdit()
        self.base_url_edit.setPlaceholderText("https://api.openai.com/v1")
        url_layout.addWidget(self.base_url_edit)
        group_layout.addLayout(url_layout)

        # Model and concurrency row
        row_layout = QHBoxLayout()
        row_layout.addWidget(QLabel("Model:"))
        self.model_edit = QLineEdit()
        self.model_edit.setPlaceholderText("gpt-3.5-turbo")
        row_layout.addWidget(self.model_edit)
        row_layout.addWidget(QLabel("并发数:"))
        self.concurrency_edit = QLineEdit()
        self.concurrency_edit.setPlaceholderText("1")
        row_layout.addWidget(self.concurrency_edit)
        group_layout.addLayout(row_layout)

        group.setLayout(group_layout)
        layout.addWidget(group)

    def get_config(self) -> dict:
        """Return current config as dict."""
        return {
            "api_key": self.api_key_edit.text(),
            "base_url": self.base_url_edit.text(),
            "model": self.model_edit.text(),
            "concurrency": int(self.concurrency_edit.text() or "1"),
        }

    def set_config(self, config: dict) -> None:
        """Set config values."""
        self.api_key_edit.setText(config.get("api_key", ""))
        self.base_url_edit.setText(config.get("base_url", ""))
        self.model_edit.setText(config.get("model", ""))
        self.concurrency_edit.setText(str(config.get("concurrency", 1)))
