from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSplitter, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtCore import Qt

from ui.scope_tree_widget import ScopeTreeWidget
from ui.scope_preview_panel import ScopePreviewPanel
from ui.template_editor_dialog import TemplateEditorDialog
from ui.new_template_dialog import NewTemplateDialog
from ui.project_loader_window import ProjectLoaderWindow
from ui.template_loader_window import TemplateLoaderWindow

from logic.save_manager import save_project, load_project
from logic.undo_manager import undo_manager
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ScopeBuilder")
        self.resize(1200, 800)

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Toolbar layout
        toolbar_layout = QHBoxLayout()
        btn_new_project = QPushButton("New Project")
        btn_new_template = QPushButton("New Template")
        btn_open_template = QPushButton("Open Template")
        btn_edit_template = QPushButton("Edit Template")
        btn_save_project = QPushButton("Save Project")
        btn_load_project = QPushButton("Load Project")
        btn_export = QPushButton("Export Scope")
        btn_undo = QPushButton("Undo")
        btn_redo = QPushButton("Redo")

        # Connect buttons to handlers
        btn_new_project.clicked.connect(self.new_project)
        btn_new_template.clicked.connect(self.new_template)
        btn_open_template.clicked.connect(self.open_template)
        btn_edit_template.clicked.connect(self.edit_template)
        btn_save_project.clicked.connect(self.save_project)
        btn_load_project.clicked.connect(self.load_project)
        btn_export.clicked.connect(self.export_preview)
        btn_undo.clicked.connect(self.undo_action)
        btn_redo.clicked.connect(self.redo_action)

        # Add buttons to toolbar
        toolbar_layout.addWidget(btn_new_project)
        toolbar_layout.addWidget(btn_new_template)
        toolbar_layout.addWidget(btn_open_template)
        toolbar_layout.addWidget(btn_edit_template)
        toolbar_layout.addWidget(btn_save_project)
        toolbar_layout.addWidget(btn_load_project)
        toolbar_layout.addWidget(btn_export)
        toolbar_layout.addWidget(btn_undo)
        toolbar_layout.addWidget(btn_redo)
        toolbar_layout.addStretch()
        main_layout.addLayout(toolbar_layout)

        # Splitter layout
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.scope_tree = ScopeTreeWidget()
        self.preview_panel = ScopePreviewPanel()

        self.scope_tree.scopeChanged.connect(self.preview_panel.update_preview)

        splitter.addWidget(self.scope_tree)
        splitter.addWidget(self.preview_panel)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(splitter)

        # Global Undo/Redo keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self.undo_action)
        QShortcut(QKeySequence("Ctrl+Y"), self).activated.connect(self.redo_action)

    def undo_action(self):
        undo_manager.undo()

    def redo_action(self):
        undo_manager.redo()

    def new_project(self):
        confirm = QMessageBox.question(
            self,
            "New Project",
            "Are you sure you want to start a new project? Unsaved work will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.scope_tree.tree.clear()
            self.scope_tree.label.setText("Scope Tree")
            self.preview_panel.clear()

    def new_template(self):
        dialog = NewTemplateDialog(templates_folder="data", parent=self)
        if dialog.exec():
            template_path = dialog.template_path
            if template_path:
                editor = TemplateEditorDialog(self)
                editor.load_template(template_path)
                editor.exec()

    def open_template(self):
        def load_template_data(file_path):
            self.scope_tree.load_template(file_path)

        self.template_loader_window = TemplateLoaderWindow("data", load_template_data, self)
        self.template_loader_window.show()

    def edit_template(self):
        editor = TemplateEditorDialog(self)
        editor.exec()

    def export_preview(self):
        text = self.preview_panel.get_preview_text()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Scope", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                QMessageBox.information(self, "Export", "Scope successfully exported.")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))

    def save_project(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Project", "data/saved_projects/", "JSON Files (*.json)"
        )
        if not file_path:
            return

        template_path = self.scope_tree.label.text().replace("Loaded: ", "").strip()
        if not template_path or not os.path.exists(template_path):
            QMessageBox.warning(self, "Template Missing", "Please load a template first.")
            return

        checked_paths = self.scope_tree.get_checked_paths()
        save_project(file_path, template_path, checked_paths)
        QMessageBox.information(self, "Saved", "Project saved successfully.")

    def load_project(self):
        def load_project_data(file_path):
            project_data = load_project(file_path)
            if not project_data:
                QMessageBox.warning(self, "Error", "Could not load project file.")
                return

            template_path = project_data.get("template_file")
            checked_paths = project_data.get("checked_items", [])

            self.scope_tree.load_template(template_path)
            self.scope_tree.set_checked_paths(checked_paths)

        dialog = ProjectLoaderWindow("data/saved_projects", load_project_data, self)
        dialog.exec()

