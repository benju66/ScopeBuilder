from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QTableWidget, QTableWidgetItem, QPushButton,
    QFileDialog, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
import os
from datetime import datetime


class TemplateLoaderWindow(QWidget):
    def __init__(self, folder_path, load_callback, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Browse Templates")
        self.resize(600, 400)
        self.folder_path = folder_path
        self.load_callback = load_callback

        self.layout = QVBoxLayout(self)

        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter templates...")
        self.search_input.textChanged.connect(self.filter_templates)
        search_layout.addWidget(self.search_input)
        self.layout.addLayout(search_layout)

        # Table of templates
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Template Name", "Last Modified"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.layout.addWidget(self.table)

        # Buttons
        button_layout = QHBoxLayout()
        self.btn_open = QPushButton("Open Selected Template")
        self.btn_open.clicked.connect(self.load_selected_template)

        self.btn_browse = QPushButton("Browse for File...")
        self.btn_browse.clicked.connect(self.browse_for_file)

        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.close)

        button_layout.addWidget(self.btn_open)
        button_layout.addWidget(self.btn_browse)
        button_layout.addStretch()
        button_layout.addWidget(self.btn_close)

        self.layout.addLayout(button_layout)

        # Populate list
        self.populate_templates()

    def populate_templates(self):
        self.table.setRowCount(0)
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

        for file in sorted(os.listdir(self.folder_path)):
            if file.endswith(".json"):
                full_path = os.path.join(self.folder_path, file)
                row = self.table.rowCount()
                self.table.insertRow(row)

                self.table.setItem(row, 0, QTableWidgetItem(file))
                self.table.setItem(row, 1, QTableWidgetItem(
                    self.format_date(os.path.getmtime(full_path)))
                )

    def format_date(self, timestamp):
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")

    def filter_templates(self, text):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            visible = text.lower() in item.text().lower()
            self.table.setRowHidden(row, not visible)

    def load_selected_template(self):
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "No Selection", "Please select a template to open.")
            return

        filename = self.table.item(selected, 0).text()
        path = os.path.join(self.folder_path, filename)
        self.load_callback(path)
        self.close()

    def browse_for_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Template File", "", "JSON Files (*.json)")
        if file_path:
            self.load_callback(file_path)
            self.close()
