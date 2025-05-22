from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal
from logic.undo_redo import Command
from logic.undo_manager import undo_manager
import json
import os


class ScopeTreeWidget(QWidget):
    scopeChanged = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel("Scope Tree")
        layout.addWidget(self.label)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Scope Item"])
        self.tree.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.tree.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.tree.setEditTriggers(QTreeWidget.EditTrigger.DoubleClicked)
        self.tree.setColumnCount(1)
        layout.addWidget(self.tree)

        self.tree.itemChanged.connect(self.on_item_changed)
        self.tree.itemChanged.connect(self.track_item_changes)

        self.root_data = []
        self._last_item_state = {}

    def load_template(self, file_path):
        if not os.path.exists(file_path):
            self.label.setText("File not found.")
            return

        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                self.root_data = data.get("sections", [])
                self.tree.clear()
                self.build_tree(self.root_data, self.tree.invisibleRootItem())
                self.label.setText(f"Loaded: {os.path.basename(file_path)}")
        except Exception as e:
            self.label.setText(f"Error loading template: {str(e)}")

    def build_tree(self, items, parent):
        for item in items:
            title = item.get("title", item.get("text", "Untitled"))
            tree_item = QTreeWidgetItem([title])
            tree_item.setFlags(tree_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            tree_item.setCheckState(0, Qt.CheckState.Unchecked)
            tree_item.setFlags(tree_item.flags() | Qt.ItemFlag.ItemIsEditable)

            if item.get("locked", False):
                tree_item.setFlags(tree_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                tree_item.setToolTip(0, "🔒 Locked")
                tree_item.setData(0, Qt.ItemDataRole.UserRole, "locked")

            if item.get("highlight", False):
                tree_item.setForeground(0, Qt.GlobalColor.darkYellow)
                tree_item.setData(0, Qt.ItemDataRole.UserRole + 1, "highlight")

            parent.addChild(tree_item)

            if "children" in item:
                self.build_tree(item["children"], tree_item)

    def on_item_changed(self, item, column):
        if column == 0:
            scope_text = self.generate_scope_text()
            self.scopeChanged.emit(scope_text)

    def track_item_changes(self, item, column):
        if column != 0:
            return

        current_text = item.text(0)
        current_check = item.checkState(0)

        prev = self._last_item_state.get(id(item))
        self._last_item_state[id(item)] = (current_text, current_check)

        if prev is None:
            return

        prev_text, prev_check = prev

        if current_text != prev_text:
            undo_manager.push(Command(
                do_func=lambda: item.setText(0, current_text),
                undo_func=lambda: item.setText(0, prev_text),
                description="Edit Text"
            ))

        if current_check != prev_check:
            undo_manager.push(Command(
                do_func=lambda: item.setCheckState(0, current_check),
                undo_func=lambda: item.setCheckState(0, prev_check),
                description="Toggle Check"
            ))

    def generate_scope_text(self):
        """Generate formatted scope text that matches PDF structure exactly"""
        divider_sections = {"MILESTONES", "ESTIMATED WORKFORCE", "CLARIFICATIONS", "SCOPE CLARIFICATIONS"}

        def recurse(node, prefix_stack, parent_is_root=False):
            lines = []
            letter_counter = 0  # For A., B., C. subsections
            number_counter = 0  # For 1., 2., 3. items under subsections
            
            for i in range(node.childCount()):
                child = node.child(i)
                if child.checkState(0) == Qt.CheckState.Checked:
                    text = child.text(0).strip()
                    
                    # Determine hierarchy level
                    level = len(prefix_stack)
                    
                    if level == 0:
                        # Top-level sections (SCOPE CLARIFICATIONS, ESTIMATED WORKFORCE, etc.)
                        text_upper = text.upper()
                        if any(section in text_upper for section in divider_sections):
                            lines.append("----------------------------------------")
                        lines.append(f"**{text_upper}**")
                        lines.append("")
                        
                    elif level == 1:
                        # Subsections (A. Footings and Foundations, B. Slab-on-Grade, etc.)
                        letter_counter += 1
                        letter = chr(ord('A') + letter_counter - 1)
                        lines.append(f"{letter}. {text}")
                        
                        # Reset number counter for items under this subsection
                        number_counter = 0
                        
                    elif level == 2:
                        # Items under subsections (1., 2., 3., etc.)
                        number_counter += 1
                        lines.append(f"    {number_counter}. {text}")
                        
                    else:
                        # Deeper levels (rare, but handle gracefully)
                        indent = "    " * (level - 1)
                        sub_number = len([x for x in lines if x.strip().startswith(f"{indent}")]) + 1
                        lines.append(f"{indent}{sub_number}. {text}")
                    
                    # Recursively process children
                    child_lines = recurse(child, prefix_stack + [str(i)], level == 0)
                    lines.extend(child_lines)
                    
            return lines

        root = self.tree.invisibleRootItem()
        result_lines = recurse(root, [])
        
        # Clean up the output - remove excessive empty lines
        cleaned_lines = []
        prev_empty = False
        
        for line in result_lines:
            if line.strip():
                cleaned_lines.append(line)
                prev_empty = False
            elif not prev_empty:  # Only add one empty line at a time
                cleaned_lines.append("")
                prev_empty = True
        
        return "\n".join(cleaned_lines)

    def get_checked_paths(self):
        def recurse(item, path_so_far):
            paths = []
            for i in range(item.childCount()):
                child = item.child(i)
                current_path = path_so_far + [child.text(0)]
                if child.checkState(0) == Qt.CheckState.Checked:
                    paths.append(current_path)
                paths.extend(recurse(child, current_path))
            return paths

        return recurse(self.tree.invisibleRootItem(), [])

    def set_checked_paths(self, paths):
        def recurse(item, path_so_far):
            for i in range(item.childCount()):
                child = item.child(i)
                current_path = path_so_far + [child.text(0)]
                if current_path in paths:
                    child.setCheckState(0, Qt.CheckState.Checked)
                recurse(child, current_path)

        recurse(self.tree.invisibleRootItem(), [])