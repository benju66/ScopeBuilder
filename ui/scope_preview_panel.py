from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout, QMessageBox
)
from PyQt6.QtGui import QGuiApplication, QTextCursor
from logic.undo_redo import Command
from logic.undo_manager import undo_manager


class ScopePreviewPanel(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel("Live Scope Preview")
        layout.addWidget(self.label)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Selected scope items will appear here...")
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        layout.addWidget(self.text_edit)

        button_layout = QHBoxLayout()
        self.btn_copy = QPushButton("Copy to Clipboard")
        self.btn_copy.clicked.connect(self.copy_to_clipboard)
        button_layout.addStretch()
        button_layout.addWidget(self.btn_copy)
        layout.addLayout(button_layout)

    def update_preview(self, text):
        old_text = self.text_edit.toPlainText()
        new_text = text

        undo_manager.push(Command(
            do_func=lambda: self._set_text(new_text),
            undo_func=lambda: self._set_text(old_text),
            description="Update Preview"
        ))

    def append_line(self, line):
        old_text = self.text_edit.toPlainText()
        new_text = old_text + "\n" + line

        undo_manager.push(Command(
            do_func=lambda: self._set_text(new_text),
            undo_func=lambda: self._set_text(old_text),
            description="Append Line"
        ))

    def clear(self):
        old_text = self.text_edit.toPlainText()

        undo_manager.push(Command(
            do_func=lambda: self._set_text(""),
            undo_func=lambda: self._set_text(old_text),
            description="Clear Preview"
        ))

    def _set_text(self, text):
        self.text_edit.setPlainText(text)
        self.text_edit.moveCursor(QTextCursor.MoveOperation.Start)

    def get_preview_text(self):
        return self.text_edit.toPlainText()

    def copy_to_clipboard(self):
        text = self.get_preview_text()
        if text.strip():
            QGuiApplication.clipboard().setText(text)
            QMessageBox.information(self, "Copied", "Preview copied to clipboard.")
        else:
            QMessageBox.warning(self, "Empty", "Nothing to copy.")
