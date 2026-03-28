"""Logging utilities."""

import logging
from typing import Optional


class LoggerSetup:
    """Setup and configure application logging."""

    def __init__(self, name: str = "md_translator"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Clear existing handlers
        self.logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(self._create_formatter())
        self.logger.addHandler(console_handler)

    def _create_formatter(self) -> logging.Formatter:
        """Create log formatter."""
        return logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%H:%M:%S"
        )

    def get_logger(self) -> logging.Logger:
        """Get configured logger with additional methods."""
        # Add specialized logging methods to the logger instance
        self.logger.log_slice_status = self._create_log_slice_status()
        self.logger.log_start = self._create_log_start()
        self.logger.log_complete = self._create_log_complete()
        return self.logger

    def _create_log_slice_status(self):
        """Create log_slice_status method."""
        def log_slice_status(
            slice_index: int,
            total: int,
            status: str,
            duration: float = None,
            error: str = None
        ):
            display_index = slice_index + 1
            duration_str = f" ({duration:.2f}s)" if duration is not None else ""

            if status == "success":
                self.logger.info(
                    f"[{display_index}/{total}] 切片处理成功{duration_str}"
                )
            elif status == "error":
                error_str = f" - {error}" if error else ""
                self.logger.error(
                    f"[{display_index}/{total}] 切片处理失败{duration_str}{error_str}"
                )
            elif status == "skipped":
                self.logger.warning(
                    f"[{display_index}/{total}] 切片已跳过 (保留原文)"
                )
        return log_slice_status

    def _create_log_start(self):
        """Create log_start method."""
        def log_start(input_file: str, output_file: str):
            self.logger.info(f"开始翻译：{input_file}")
            self.logger.info(f"输出文件：{output_file}")
        return log_start

    def _create_log_complete(self):
        """Create log_complete method."""
        def log_complete(total: int, success: int, errors: int, duration: float):
            self.logger.info(
                f"翻译完成 - 总计：{total}, 成功：{success}, 失败：{errors}, "
                f"耗时：{duration:.2f}s"
            )
        return log_complete


# Global logger instance
_logger_setup: Optional[LoggerSetup] = None


def get_logger() -> logging.Logger:
    """Get or create global logger instance."""
    global _logger_setup
    if _logger_setup is None:
        _logger_setup = LoggerSetup()
    return _logger_setup.get_logger()