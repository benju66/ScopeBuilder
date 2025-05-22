from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, 
    QHBoxLayout, QMessageBox, QComboBox, QCheckBox, QSpinBox,
    QFormLayout, QSlider
)
from PyQt6.QtGui import QGuiApplication, QTextCursor, QFont, QTextCharFormat, QTextBlockFormat
from PyQt6.QtCore import Qt
from logic.undo_redo import Command
from logic.undo_manager import undo_manager


class ScopePreviewPanel(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Header with formatting options
        self.setup_header_controls(layout)
        
        # Rich text editor
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Selected scope items will appear here...")
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
        # Set up rich text formatting
        self.setup_rich_text_formatting()
        
        layout.addWidget(self.text_edit)

        # Buttons
        self.setup_action_buttons(layout)

        self._current_text_data = ""

    def setup_header_controls(self, layout):
        """Setup the header controls for formatting options"""
        # Main header with basic controls
        header_layout = QHBoxLayout()
        self.label = QLabel("Live Scope Preview")
        
        # Format options
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Rich Text", "Plain Text", "HTML"])
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        
        self.professional_style = QCheckBox("Professional Style")
        self.professional_style.setChecked(True)
        self.professional_style.toggled.connect(self.refresh_preview)
        
        # Formatting toggle button
        self.format_toggle_btn = QPushButton("⚙ Format")
        self.format_toggle_btn.setCheckable(True)
        self.format_toggle_btn.setMaximumWidth(80)
        self.format_toggle_btn.setStyleSheet("""
            QPushButton {
                padding: 4px 8px;
                border: 1px solid #555;
                border-radius: 3px;
                background: #3c3c3c;
                color: #ffffff;
            }
            QPushButton:checked {
                background: #4a4a4a;
                border: 1px solid #666;
            }
            QPushButton:hover {
                background: #454545;
            }
        """)
        self.format_toggle_btn.toggled.connect(self.toggle_formatting_controls)
        
        header_layout.addWidget(self.label)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Format:"))
        header_layout.addWidget(self.format_combo)
        header_layout.addWidget(self.professional_style)
        header_layout.addWidget(self.format_toggle_btn)
        
        layout.addLayout(header_layout)

        # Compact formatting toolbar (initially hidden)
        self.format_toolbar = QWidget()
        self.format_toolbar.setMaximumHeight(40)  # Slightly taller for better spacing
        self.format_toolbar.setStyleSheet("""
            QWidget {
                background: #2b2b2b;
                border: 1px solid #555;
                border-radius: 3px;
                margin: 2px 0;
                color: #ffffff;
            }
            QLabel {
                color: #cccccc;
                font-size: 11px;
            }
            QSpinBox {
                background: #3c3c3c;
                border: 1px solid #555;
                border-radius: 2px;
                padding: 2px;
                color: #ffffff;
            }
            QSpinBox:focus {
                border: 1px solid #0078d4;
            }
            QComboBox {
                background: #3c3c3c;
                border: 1px solid #555;
                border-radius: 2px;
                padding: 2px 5px;
                color: #ffffff;
            }
            QComboBox:focus {
                border: 1px solid #0078d4;
            }
            QComboBox::drop-down {
                border: none;
                background: #3c3c3c;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #cccccc;
                margin-right: 5px;
            }
        """)
        
        toolbar_layout = QHBoxLayout(self.format_toolbar)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)
        toolbar_layout.setSpacing(15)  # Increased spacing to prevent overlap
        
        # Font size control
        toolbar_layout.addWidget(QLabel("Font:"))
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 16)
        self.font_size.setValue(11)
        self.font_size.setMaximumWidth(50)
        self.font_size.valueChanged.connect(self.refresh_preview)
        toolbar_layout.addWidget(self.font_size)
        
        # Separator
        separator1 = QLabel("|")
        separator1.setStyleSheet("color: #666; font-weight: bold;")
        toolbar_layout.addWidget(separator1)
        
        # Indent size control
        toolbar_layout.addWidget(QLabel("Indent:"))
        self.indent_size = QSpinBox()
        self.indent_size.setRange(10, 50)
        self.indent_size.setValue(20)
        self.indent_size.setSuffix("px")
        self.indent_size.setMinimumWidth(70)
        self.indent_size.valueChanged.connect(self.refresh_preview)
        toolbar_layout.addWidget(self.indent_size)
        
        # Separator
        separator2 = QLabel("|")
        separator2.setStyleSheet("color: #666; font-weight: bold;")
        toolbar_layout.addWidget(separator2)
        
        # Line spacing control
        toolbar_layout.addWidget(QLabel("Spacing:"))
        self.line_spacing = QComboBox()
        self.line_spacing.addItems(["Single", "1.15", "1.5", "Double"])
        self.line_spacing.setCurrentText("1.15")
        self.line_spacing.setMinimumWidth(70)
        self.line_spacing.currentTextChanged.connect(self.refresh_preview)
        toolbar_layout.addWidget(self.line_spacing)
        
        # Separator
        separator3 = QLabel("|")
        separator3.setStyleSheet("color: #666; font-weight: bold;")
        toolbar_layout.addWidget(separator3)
        
        # Numbering style
        toolbar_layout.addWidget(QLabel("Numbering:"))
        self.numbering_style = QComboBox()
        self.numbering_style.addItems(["Standard (A., 1., 2.)", "All Numbers (1., 1.1, 1.2)", "Letters First (A., A.1, A.2)"])
        self.numbering_style.setMinimumWidth(180)
        self.numbering_style.currentTextChanged.connect(self.refresh_preview)
        toolbar_layout.addWidget(self.numbering_style)
        
        toolbar_layout.addStretch()
        
        layout.addWidget(self.format_toolbar)
        self.format_toolbar.hide()  # Initially hidden

    def setup_action_buttons(self, layout):
        """Setup action buttons"""
        button_layout = QHBoxLayout()
        self.btn_copy = QPushButton("Copy to Clipboard")
        self.btn_copy.clicked.connect(self.copy_to_clipboard)
        
        self.btn_export_word = QPushButton("Export to Word")
        self.btn_export_word.clicked.connect(self.export_to_word)
        
        self.btn_print = QPushButton("Print Preview")
        self.btn_print.clicked.connect(self.print_preview)
        
        button_layout.addStretch()
        button_layout.addWidget(self.btn_copy)
        button_layout.addWidget(self.btn_export_word)
        button_layout.addWidget(self.btn_print)
        layout.addLayout(button_layout)

    def setup_rich_text_formatting(self):
        """Configure the text editor for rich text"""
        self.text_edit.setAcceptRichText(True)
        
        # Set default font
        font = QFont("Arial", self.font_size.value())
        self.text_edit.setFont(font)

    def update_preview(self, text_data):
        """Update preview with rich text formatting"""
        old_text = self.text_edit.toHtml()
        self._current_text_data = text_data
        
        if self.format_combo.currentText() == "Rich Text":
            new_text = self.format_as_rich_text(text_data)
        elif self.format_combo.currentText() == "HTML":
            new_text = self.format_as_html(text_data)
        else:
            new_text = text_data  # Plain text
            
        undo_manager.push(Command(
            do_func=lambda: self._set_content(new_text),
            undo_func=lambda: self._set_content(old_text),
            description="Update Preview"
        ))

    def format_as_rich_text(self, text_data):
        """Convert plain text to rich HTML formatting with enhanced styling"""
        if not text_data.strip():
            return ""
            
        lines = text_data.split('\n')
        html_content = []
        
        # Get formatting settings
        font_size = self.font_size.value()
        indent_size = self.indent_size.value()
        line_height = self.get_line_height()
        
        # Professional document header
        if self.professional_style.isChecked():
            html_content.append(f'''
            <div style="text-align: center; margin-bottom: 25px; page-break-inside: avoid;">
                <h1 style="font-size: {font_size + 3}pt; font-weight: bold; margin: 0; letter-spacing: 1px;">
                    03-0000 CONCRETE SCOPE OF WORK
                </h1>
            </div>
            ''')
        
        section_counter = 0
        subsection_counters = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                html_content.append('<br>')
                continue
                
            # Handle section dividers
            if line.startswith('----') or line.startswith('****'):
                html_content.append('<hr style="border: none; border-bottom: 2px solid #000; margin: 20px 0 15px 0;">')
                continue
            
            # Main section headers (all caps, **bold**)
            if line.startswith('**') and line.endswith('**'):
                section_title = line[2:-2].strip()
                if section_title.isupper():
                    section_counter += 1
                    subsection_counters[section_counter] = 0
                    
                    html_content.append('<hr style="border: none; border-bottom: 1px solid #000; margin: 15px 0 5px 0;">')
                    html_content.append(f'''
                    <h2 style="font-size: {font_size + 1}pt; font-weight: bold; margin: 15px 0 12px 0; 
                              text-align: left; letter-spacing: 0.5px; line-height: {line_height};">
                        {section_title}
                    </h2>
                    ''')
                else:
                    html_content.append(f'<p style="font-weight: bold; margin: 10px 0; font-size: {font_size}pt;">{section_title}</p>')
                continue
            
            # Process numbered/lettered items
            formatted_line = self.format_line_with_hierarchy(line, font_size, indent_size, line_height)
            html_content.append(formatted_line)
        
        return ''.join(html_content)

    def format_line_with_hierarchy(self, line, font_size, indent_size, line_height):
        """Format a line based on its hierarchy level"""
        import re
        
        # Detect line type and format accordingly
        if re.match(r'^\s*[A-Z]\.\s+', line):
            # Subsection headers (A., B., C.)
            return f'''
            <p style="font-size: {font_size}pt; font-weight: bold; margin: 12px 0 8px 0; 
                     line-height: {line_height}; color: #000;">
                {line.strip()}
            </p>
            '''
        elif re.match(r'^\s+\d+\.\s+', line):
            # Numbered items under subsections
            return f'''
            <p style="font-size: {font_size}pt; margin: 4px 0 4px {indent_size}px; 
                     line-height: {line_height}; text-align: justify;">
                {line.strip()}
            </p>
            '''
        elif re.match(r'^\s*\d+\.\d+\.\s+', line):
            # Sub-numbered items (1.1., 1.2., etc.)
            return f'''
            <p style="font-size: {font_size}pt; margin: 3px 0 3px {indent_size * 2}px; 
                     line-height: {line_height}; text-align: justify;">
                {line.strip()}
            </p>
            '''
        else:
            # Regular text or other formats
            return f'''
            <p style="font-size: {font_size}pt; margin: 5px 0; line-height: {line_height};">
                {line.strip()}
            </p>
            '''

    def get_line_height(self):
        """Get line height based on spacing setting"""
        spacing_map = {
            "Single": "1.0",
            "1.15": "1.15", 
            "1.5": "1.5",
            "Double": "2.0"
        }
        return spacing_map.get(self.line_spacing.currentText(), "1.15")

    def format_as_html(self, text_data):
        """Format as clean HTML for export with enhanced styling"""
        font_size = self.font_size.value()
        indent_size = self.indent_size.value()
        line_height = self.get_line_height()
        
        html = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            '<meta charset="UTF-8">',
            '<title>Concrete Scope of Work</title>',
            '<style>',
            f'body {{ font-family: Arial, sans-serif; font-size: {font_size}pt; line-height: {line_height}; margin: 1in; color: #000; }}',
            f'h1 {{ font-size: {font_size + 3}pt; text-align: center; margin-bottom: 25px; letter-spacing: 1px; }}',
            f'h2 {{ font-size: {font_size + 1}pt; margin: 15px 0 12px 0; letter-spacing: 0.5px; }}',
            'hr { border: none; border-bottom: 1px solid #000; margin: 15px 0 5px 0; }',
            f'.indent-1 {{ margin-left: {indent_size}px; }}',
            f'.indent-2 {{ margin-left: {indent_size * 2}px; }}',
            f'.indent-3 {{ margin-left: {indent_size * 3}px; }}',
            '.subsection { font-weight: bold; margin: 12px 0 8px 0; }',
            '.item { margin: 4px 0; text-align: justify; }',
            '@page { margin: 1in; }',
            '@media print { body { margin: 0; } }',
            '</style>',
            '</head>',
            '<body>'
        ]
        
        html.append(self.format_as_rich_text(text_data))
        html.extend(['</body>', '</html>'])
        return ''.join(html)

    def toggle_formatting_controls(self, checked):
        """Toggle visibility of formatting controls"""
        if checked:
            self.format_toolbar.show()
            self.format_toggle_btn.setText("⚙ Hide")
        else:
            self.format_toolbar.hide()
            self.format_toggle_btn.setText("⚙ Format")

    def on_format_changed(self):
        """Handle format change"""
        self.refresh_preview()

    def refresh_preview(self):
        """Refresh the preview with current formatting"""
        if hasattr(self, '_current_text_data'):
            self.update_preview(self._current_text_data)

    def _set_content(self, content):
        """Set content based on format type"""
        if self.format_combo.currentText() in ["Rich Text", "HTML"]:
            self.text_edit.setHtml(content)
        else:
            self.text_edit.setPlainText(content)
        self.text_edit.moveCursor(QTextCursor.MoveOperation.Start)

    def append_line(self, line):
        old_content = self.get_preview_content()
        new_content = old_content + "\n" + line

        undo_manager.push(Command(
            do_func=lambda: self._set_content(new_content),
            undo_func=lambda: self._set_content(old_content),
            description="Append Line"
        ))

    def clear(self):
        old_content = self.get_preview_content()

        undo_manager.push(Command(
            do_func=lambda: self._set_content(""),
            undo_func=lambda: self._set_content(old_content),
            description="Clear Preview"
        ))

    def get_preview_content(self):
        """Get content based on current format"""
        if self.format_combo.currentText() in ["Rich Text", "HTML"]:
            return self.text_edit.toHtml()
        else:
            return self.text_edit.toPlainText()

    def get_preview_text(self):
        """Get plain text version"""
        return self.text_edit.toPlainText()

    def copy_to_clipboard(self):
        if self.format_combo.currentText() == "Rich Text":
            # Copy as rich text to clipboard
            self.text_edit.selectAll()
            self.text_edit.copy()
            self.text_edit.moveCursor(QTextCursor.MoveOperation.Start)
            QMessageBox.information(self, "Copied", "Rich text copied to clipboard.")
        else:
            text = self.get_preview_text()
            if text.strip():
                QGuiApplication.clipboard().setText(text)
                QMessageBox.information(self, "Copied", "Text copied to clipboard.")
            else:
                QMessageBox.warning(self, "Empty", "Nothing to copy.")

    def export_to_word(self):
        """Export formatted content that can be opened in Word"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export to Word", "", 
                "HTML Files (*.html);;Rich Text Format (*.rtf);;All Files (*)"
            )
            
            if file_path:
                content = self.format_as_html(self._current_text_data)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                QMessageBox.information(self, "Export", 
                    f"Document exported successfully.\nFile can be opened in Microsoft Word.")
                    
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")

    def print_preview(self):
        """Show print preview"""
        try:
            from PyQt6.QtPrintSupport import QPrintPreviewDialog, QPrinter
            
            printer = QPrinter()
            preview = QPrintPreviewDialog(printer, self)
            preview.paintRequested.connect(self.print_document)
            preview.exec()
            
        except Exception as e:
            QMessageBox.information(self, "Print", "Print preview requires additional Qt components.")

    def print_document(self, printer):
        """Print the document"""
        self.text_edit.print(printer)