"""GUI stylesheet definitions."""

DARK_STYLE = """
QMainWindow {
    background-color: #1e1e1e;
}
QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 10pt;
}
QPushButton {
    background-color: #0d47a1;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    min-width: 80px;
}
QPushButton:hover {
    background-color: #1565c0;
}
QPushButton:disabled {
    background-color: #424242;
    color: #757575;
}
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #424242;
    border-radius: 4px;
    padding: 4px;
}
QLabel {
    color: #e0e0e0;
}
QGroupBox {
    border: 1px solid #424242;
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 16px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
}
QProgressBar {
    border: 1px solid #424242;
    border-radius: 4px;
    text-align: center;
    background-color: #2d2d2d;
}
QProgressBar::chunk {
    background-color: #0d47a1;
}
QListWidget {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #424242;
    border-radius: 4px;
}
"""
