from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
    QTableWidget, QTableWidgetItem, QPushButton,
    QFileDialog, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
import os
from datetime import datetime


class ProjectLoaderWindow(QDialog):
    def __init__(self, folder_path, load_callback, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Browse Saved Projects")
        self.resize(600, 400)
        self.folder_path = folder_path
        self.load_callback = load_callback

        self.layout = QVBoxLayout(self)

        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter saved projects...")
        self.search_input.textChanged.connect(self.filter_projects)
        search_layout.addWidget(self.search_input)
        self.layout.addLayout(search_layout)

        # Table of projects
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Project Name", "Last Modified"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.layout.addWidget(self.table)

        # Button row
        button_layout = QHBoxLayout()
        self.btn_open = QPushButton("Open Selected Project")
        self.btn_open.clicked.connect(self.load_selected_project)

        self.btn_browse = QPushButton("Browse for File...")
        self.btn_browse.clicked.connect(self.browse_for_file)

        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.close)

        button_layout.addWidget(self.btn_open)
        button_layout.addWidget(self.btn_browse)
        button_layout.addStretch()
        button_layout.addWidget(self.btn_close)

        self.layout.addLayout(button_layout)

        # Load table entries
        self.populate_projects()

    def populate_projects(self):
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

    def filter_projects(self, text):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            visible = text.lower() in item.text().lower()
            self.table.setRowHidden(row, not visible)

    def load_selected_project(self):
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "No Selection", "Please select a project to open.")
            return

        filename = self.table.item(selected, 0).text()
        path = os.path.join(self.folder_path, filename)
        self.load_callback(path)
        self.accept()

    def browse_for_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Project File", "", "JSON Files (*.json)")
        if file_path:
            self.load_callback(file_path)
            self.accept()
