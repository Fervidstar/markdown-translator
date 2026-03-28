"""Main window for the GUI application."""
from typing import Optional

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QStatusBar
)
from PyQt5.QtCore import Qt

from .widgets import FileSelector, LogViewer, ConfigPanel
from .workers import TranslationWorker
from .styles import DARK_STYLE
from config.loader import ConfigLoader


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.worker: Optional[TranslationWorker] = None
        self.config_loader = ConfigLoader()
        self._setup_ui()
        self._load_initial_config()

    def _setup_ui(self) -> None:
        """Initialize the UI components."""
        self.setWindowTitle("Markdown 翻译器")
        self.setMinimumSize(700, 600)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Title
        title = QLabel("Markdown 文档翻译器")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; padding: 8px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # File selector
        self.file_selector = FileSelector()
        layout.addWidget(self.file_selector)

        # Config panel
        self.config_panel = ConfigPanel()
        layout.addWidget(self.config_panel)

        # Log viewer
        self.log_viewer = LogViewer()
        layout.addWidget(self.log_viewer)

        # Buttons
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("开始翻译")
        self.start_btn.clicked.connect(self._on_start)
        button_layout.addWidget(self.start_btn)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self._on_cancel)
        self.cancel_btn.setEnabled(False)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")

        # Apply styles
        self.setStyleSheet(DARK_STYLE)

    def _load_initial_config(self) -> None:
        """Load existing config into the panel."""
        try:
            config = self.config_loader.load()
            api_key = self.config_loader.get_api_key()
            self.config_panel.set_config({
                "api_key": api_key or "",
                "base_url": config.api.base_url,
                "model": config.api.model,
                "concurrency": config.concurrency,
            })
        except Exception as e:
            self.log_viewer.append_log(f"加载配置失败: {e}")

    def _on_start(self) -> None:
        """Handle start button click."""
        input_path = self.file_selector.get_input_path()
        if not input_path:
            QMessageBox.warning(self, "错误", "请选择输入文件")
            return

        output_path = self.file_selector.get_output_path()
        if not output_path:
            QMessageBox.warning(self, "错误", "请指定输出文件")
            return

        # Get config from panel and save to .env
        config_dict = self.config_panel.get_config()
        if config_dict["api_key"]:
            self._save_api_key(config_dict["api_key"])

        # Update config file
        self._update_config_file(config_dict)

        # Disable start, enable cancel
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.status_bar.showMessage("翻译中...")

        # Clear log
        self.log_viewer.clear()
        self.log_viewer.append_log(f"开始翻译: {input_path}")
        self.log_viewer.append_log(f"输出到: {output_path}")

        # Start worker
        self.worker = TranslationWorker(
            input_path=input_path,
            output_path=output_path,
            config_loader=self.config_loader
        )
        self.worker.progress.connect(self._on_progress)
        self.worker.log_message.connect(self._on_log_message)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.status_bar.showMessage("正在取消...")

    def _on_progress(self, current: int, total: int, status: str) -> None:
        """Handle translation progress update."""
        self.log_viewer.set_progress(current, total, status)
        self.status_bar.showMessage(f"{current}/{total} - {status}")

    def _on_log_message(self, message: str) -> None:
        """Handle log message from worker."""
        self.log_viewer.append_log(message)

    def _on_finished(self, success: bool, message: str) -> None:
        """Handle translation completion."""
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)

        if success:
            self.status_bar.showMessage("翻译完成")
            QMessageBox.information(self, "完成", f"翻译完成！\n输出: {message}")
        else:
            self.status_bar.showMessage("翻译失败")
            QMessageBox.warning(self, "翻译完成", message)

        self.worker = None

    def _save_api_key(self, api_key: str) -> None:
        """Save API key to .env file."""
        env_path = self.config_loader.env_path
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")
        # Reload config loader
        self.config_loader = ConfigLoader()

    def _update_config_file(self, config: dict) -> None:
        """Update config.yaml with settings from panel."""
        import yaml
        config_path = self.config_loader.config_path

        # Load existing
        existing = {}
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                existing = yaml.safe_load(f) or {}

        # Update
        existing.setdefault("api", {})
        existing["api"]["base_url"] = config.get("base_url", "")
        existing["api"]["model"] = config.get("model", "")
        existing["concurrency"] = config.get("concurrency", 1)

        # Write back
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(existing, f, allow_unicode=True)

        # Reload
        self.config_loader = ConfigLoader()

    def closeEvent(self, event) -> None:
        """Handle window close."""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait()
        event.accept()
