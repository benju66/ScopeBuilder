from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QHBoxLayout, QMessageBox
)
import os


class NewTemplateDialog(QDialog):
    def __init__(self, templates_folder, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Template")
        self.setFixedSize(400, 150)
        self.templates_folder = templates_folder
        self.template_path = None

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel("Enter a name for the new template:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. 03-5000 Precast Concrete")

        layout.addWidget(self.label)
        layout.addWidget(self.name_input)

        # Buttons
        button_layout = QHBoxLayout()
        self.btn_create = QPushButton("Create")
        self.btn_cancel = QPushButton("Cancel")
        self.btn_create.clicked.connect(self.create_template)
        self.btn_cancel.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.btn_cancel)
        button_layout.addWidget(self.btn_create)

        layout.addLayout(button_layout)

    def create_template(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Invalid Name", "Please enter a template name.")
            return

        safe_name = name.lower().replace(" ", "_").replace("/", "_")
        filename = f"{safe_name}.json"
        path = os.path.join(self.templates_folder, filename)

        if os.path.exists(path):
            QMessageBox.warning(self, "Template Exists", "A template with this name already exists.")
            return

        # Save empty structure
        self.template_path = path
        with open(path, "w", encoding="utf-8") as f:
            f.write('{\n  "template_name": "' + name + '",\n  "sections": []\n}')
        self.accept()
