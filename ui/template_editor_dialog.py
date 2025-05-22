from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QHBoxLayout, QFileDialog, QMessageBox,
    QInputDialog, QCheckBox
)
from PyQt6.QtCore import Qt
import json


class TemplateEditorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Template Editor")
        self.resize(800, 600)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Scope Item"])
        self.tree.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.tree.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.tree.setEditTriggers(QTreeWidget.EditTrigger.DoubleClicked)
        self.tree.setColumnCount(1)
        self.layout.addWidget(self.tree)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add Item")
        self.btn_delete = QPushButton("Delete Item")
        self.btn_lock = QPushButton("Toggle Lock")
        self.btn_highlight = QPushButton("Toggle Highlight")
        self.btn_load = QPushButton("Load Template")
        self.btn_save = QPushButton("Save Template")
        self.btn_close = QPushButton("Close")

        for btn in [
            self.btn_add, self.btn_delete, self.btn_lock, self.btn_highlight,
            self.btn_load, self.btn_save, self.btn_close
        ]:
            btn_layout.addWidget(btn)

        self.layout.addLayout(btn_layout)

        # Connect buttons
        self.btn_add.clicked.connect(self.add_item)
        self.btn_delete.clicked.connect(self.delete_item)
        self.btn_lock.clicked.connect(self.toggle_lock)
        self.btn_highlight.clicked.connect(self.toggle_highlight)
        self.btn_load.clicked.connect(self.load_template)
        self.btn_save.clicked.connect(self.save_template)
        self.btn_close.clicked.connect(self.accept)

    def add_item(self):
        selected = self.tree.currentItem()
        text, ok = QInputDialog.getText(self, "Add Item", "Enter scope item text:")
        if ok and text:
            new_item = QTreeWidgetItem([text])
            new_item.setFlags(new_item.flags() | Qt.ItemFlag.ItemIsEditable)
            if selected:
                selected.addChild(new_item)
                selected.setExpanded(True)
            else:
                self.tree.invisibleRootItem().addChild(new_item)

    def delete_item(self):
        selected = self.tree.currentItem()
        if selected:
            parent = selected.parent()
            if parent:
                parent.removeChild(selected)
            else:
                self.tree.invisibleRootItem().removeChild(selected)

    def toggle_lock(self):
        item = self.tree.currentItem()
        if item:
            locked = item.data(0, Qt.ItemDataRole.UserRole) == "locked"
            if locked:
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                item.setToolTip(0, "")
                item.setData(0, Qt.ItemDataRole.UserRole, "")
            else:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                item.setToolTip(0, "🔒 Locked")
                item.setData(0, Qt.ItemDataRole.UserRole, "locked")

    def toggle_highlight(self):
        item = self.tree.currentItem()
        if item:
            highlighted = item.foreground(0) == Qt.GlobalColor.darkYellow
            if highlighted:
                item.setForeground(0, Qt.GlobalColor.black)
                item.setData(0, Qt.ItemDataRole.UserRole + 1, "")
            else:
                item.setForeground(0, Qt.GlobalColor.darkYellow)
                item.setData(0, Qt.ItemDataRole.UserRole + 1, "highlight")

    def load_template(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Template", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.tree.clear()
                    self.setWindowTitle(f"Editing: {file_path}")
                    self.build_tree(data.get("sections", []), self.tree.invisibleRootItem())
                    self.loaded_file_path = file_path
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load template:\n{str(e)}")

    def save_template(self):
        if hasattr(self, 'loaded_file_path'):
            path = self.loaded_file_path
        else:
            path, _ = QFileDialog.getSaveFileName(self, "Save Template", "", "JSON Files (*.json)")
            if not path:
                return

        try:
            data = {
                "template_name": "Template",
                "sections": self.extract_tree(self.tree.invisibleRootItem())
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            QMessageBox.information(self, "Saved", "Template saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save template:\n{str(e)}")

    def build_tree(self, items, parent):
        for item in items:
            label = item.get("title", item.get("text", "Untitled"))
            node = QTreeWidgetItem([label])
            node.setFlags(node.flags() | Qt.ItemFlag.ItemIsEditable)

            if item.get("locked", False):
                node.setFlags(node.flags() & ~Qt.ItemFlag.ItemIsEditable)
                node.setToolTip(0, "🔒 Locked")
                node.setData(0, Qt.ItemDataRole.UserRole, "locked")

            if item.get("highlight", False):
                node.setForeground(0, Qt.GlobalColor.darkYellow)
                node.setData(0, Qt.ItemDataRole.UserRole + 1, "highlight")

            parent.addChild(node)

            if "children" in item:
                self.build_tree(item["children"], node)

    def extract_tree(self, parent):
        items = []
        for i in range(parent.childCount()):
            node = parent.child(i)
            label = node.text(0)
            locked = node.data(0, Qt.ItemDataRole.UserRole) == "locked"
            highlight = node.data(0, Qt.ItemDataRole.UserRole + 1) == "highlight"
            child = {
                "title": label,
                "locked": locked,
                "highlight": highlight
            }
            children = self.extract_tree(node)
            if children:
                child["children"] = children
            items.append(child)
        return items
