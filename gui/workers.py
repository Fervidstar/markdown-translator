"""Background worker threads for translation."""
from typing import Optional

from PyQt5.QtCore import QThread, pyqtSignal

from config.loader import ConfigLoader
from config.models import AppConfig
from core.slicer import MarkdownSlicer
from core.translator import Translator
from core.assembler import Assembler
from utils.file_utils import read_file, write_file


class TranslationWorker(QThread):
    """Background thread for running translation without blocking UI."""

    progress = pyqtSignal(int, int, str)  # current, total, status
    log_message = pyqtSignal(str)  # log message
    finished = pyqtSignal(bool, str)  # success, output_path or error

    def __init__(
        self,
        input_path: str,
        output_path: str,
        config_loader: ConfigLoader
    ):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.config_loader = config_loader
        self._is_cancelled = False

    def run(self) -> None:
        """Execute translation in background thread."""
        try:
            # Load config
            config = self.config_loader.load()
            api_key = self.config_loader.get_api_key()
            self.config_loader.validate_config(api_key)

            # Read input
            content = read_file(self.input_path)
            self.progress.emit(0, 1, "正在切片文档...")

            # Slice
            slicer = MarkdownSlicer(content)
            slices = slicer.slice()
            self.progress.emit(0, len(slices), f"文档已切分为 {len(slices)} 个部分")

            # Translate with progress callbacks
            translator = Translator(config=config, api_key=api_key)
            self.progress.emit(0, len(slices), "开始翻译...")

            result = translator.translate(slices)

            # Report progress for each slice
            for i in range(len(slices)):
                if self._is_cancelled:
                    self.finished.emit(False, "翻译已取消")
                    return
                self.progress.emit(i + 1, len(slices), f"已完成 {i + 1}/{len(slices)}")

            # Assemble
            self.progress.emit(len(slices), len(slices), "正在组装文档...")
            assembler = Assembler()
            translated_content = assembler.assemble(result.slices)

            # Write output
            write_file(self.output_path, translated_content)

            if result.error_count > 0:
                self.finished.emit(
                    False,
                    f"翻译完成但有 {result.error_count} 个错误，详见日志"
                )
            else:
                self.finished.emit(True, self.output_path)

        except Exception as e:
            self.log_message.emit(f"错误: {str(e)}")
            self.finished.emit(False, str(e))

    def cancel(self) -> None:
        """Request cancellation."""
        self._is_cancelled = True
