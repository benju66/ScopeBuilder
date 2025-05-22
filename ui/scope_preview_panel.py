from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, 
    QHBoxLayout, QMessageBox, QComboBox, QCheckBox, QSpinBox,
    QFormLayout, QSlider, QFrame, QToolButton, QButtonGroup
)
from PyQt6.QtGui import QGuiApplication, QTextCursor, QFont, QTextCharFormat, QTextBlockFormat, QKeyEvent, QTextListFormat
from PyQt6.QtCore import Qt
from logic.undo_redo import Command
from logic.undo_manager import undo_manager


class IndentableTextEdit(QTextEdit):
    """Custom QTextEdit that supports Tab/Shift+Tab for indent/outdent and enhanced formatting"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.indent_size = 20  # Default indent size in pixels
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle Tab and Shift+Tab for indenting/outdenting"""
        if event.key() == Qt.Key.Key_Tab:
            if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                self.outdent_selection()
            else:
                self.indent_selection()
            return
        
        # Handle other keys normally
        super().keyPressEvent(event)
    
    def indent_selection(self):
        """Indent the current line or selected lines"""
        cursor = self.textCursor()
        
        if cursor.hasSelection():
            # Handle multiple lines
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            
            # Move to start of selection
            cursor.setPosition(start)
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            
            # Store the original selection for restoration
            start_block = cursor.blockNumber()
            cursor.setPosition(end)
            end_block = cursor.blockNumber()
            
            # Indent each selected block
            cursor.setPosition(start)
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            
            for block_num in range(start_block, end_block + 1):
                self.indent_current_block(cursor)
                if block_num < end_block:
                    cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
            
            # Restore selection (approximately)
            cursor.setPosition(start)
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            new_start = cursor.position()
            cursor.setPosition(end + (new_start - start))
            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
            new_end = cursor.position()
            
            cursor.setPosition(new_start)
            cursor.setPosition(new_end, QTextCursor.MoveMode.KeepAnchor)
            self.setTextCursor(cursor)
        else:
            # Handle single line
            self.indent_current_block(cursor)
    
    def outdent_selection(self):
        """Outdent the current line or selected lines"""
        cursor = self.textCursor()
        
        if cursor.hasSelection():
            # Handle multiple lines
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            
            # Move to start of selection
            cursor.setPosition(start)
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            
            # Store the original selection for restoration
            start_block = cursor.blockNumber()
            cursor.setPosition(end)
            end_block = cursor.blockNumber()
            
            # Outdent each selected block
            cursor.setPosition(start)
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            
            for block_num in range(start_block, end_block + 1):
                self.outdent_current_block(cursor)
                if block_num < end_block:
                    cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
            
            # Restore selection (approximately)
            cursor.setPosition(start)
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            new_start = cursor.position()
            cursor.setPosition(end)
            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
            new_end = cursor.position()
            
            cursor.setPosition(new_start)
            cursor.setPosition(new_end, QTextCursor.MoveMode.KeepAnchor)
            self.setTextCursor(cursor)
        else:
            # Handle single line
            self.outdent_current_block(cursor)
    
    def indent_current_block(self, cursor):
        """Indent the current block/paragraph"""
        # Get current block format
        block_format = cursor.blockFormat()
        
        # Increase left margin
        current_margin = block_format.leftMargin()
        block_format.setLeftMargin(current_margin + self.indent_size)
        
        # Apply the format
        cursor.setBlockFormat(block_format)
        self.setTextCursor(cursor)
    
    def outdent_current_block(self, cursor):
        """Outdent the current block/paragraph"""
        # Get current block format
        block_format = cursor.blockFormat()
        
        # Decrease left margin (but don't go below 0)
        current_margin = block_format.leftMargin()
        new_margin = max(0, current_margin - self.indent_size)
        block_format.setLeftMargin(new_margin)
        
        # Apply the format
        cursor.setBlockFormat(block_format)
        self.setTextCursor(cursor)
    
    def set_indent_size(self, size):
        """Set the indent size in pixels"""
        self.indent_size = size

    def insert_horizontal_line(self):
        """Insert a horizontal line at cursor position"""
        cursor = self.textCursor()
        
        # Move to end of current block
        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
        
        # Insert new line if not at beginning of empty line
        if cursor.block().text().strip():
            cursor.insertText("\n")
        
        # Insert HTML horizontal rule
        cursor.insertHtml('<hr style="border: none; border-top: 2px solid #333; margin: 10px 0;">')
        cursor.insertText("\n")
        
        # Set cursor position after the line
        self.setTextCursor(cursor)

    def toggle_bullet_list(self):
        """Toggle bullet list for current selection"""
        cursor = self.textCursor()
        
        # Check if we're in a list
        current_list = cursor.currentList()
        
        if current_list:
            # Remove from list
            block_format = cursor.blockFormat()
            block_format.setIndent(0)
            cursor.setBlockFormat(block_format)
            
            # Remove list formatting
            cursor.setCurrentList(None)
        else:
            # Create bullet list
            list_format = QTextListFormat()
            list_format.setStyle(QTextListFormat.Style.ListDisc)
            list_format.setIndent(1)
            cursor.createList(list_format)

    def toggle_numbered_list(self):
        """Toggle numbered list for current selection"""
        cursor = self.textCursor()
        
        # Check if we're in a list
        current_list = cursor.currentList()
        
        if current_list and current_list.format().style() == QTextListFormat.Style.ListDecimal:
            # Remove from numbered list
            block_format = cursor.blockFormat()
            block_format.setIndent(0)
            cursor.setBlockFormat(block_format)
            cursor.setCurrentList(None)
        else:
            # Create numbered list
            list_format = QTextListFormat()
            list_format.setStyle(QTextListFormat.Style.ListDecimal)
            list_format.setIndent(1)
            cursor.createList(list_format)


class ScopePreviewPanel(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize values first
        self._current_text_data = ""
        self._font_size_value = 11
        self._indent_size_value = 20

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Header with formatting options
        self.setup_header_controls(layout)
        
        # Rich text editor with indent/outdent support
        self.text_edit = IndentableTextEdit()
        self.text_edit.setPlaceholderText("Selected scope items will appear here...")
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
        # Set up rich text formatting
        self.setup_rich_text_formatting()
        
        layout.addWidget(self.text_edit)

        # Buttons
        self.setup_action_buttons(layout)

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

        # Professional formatting toolbar (initially hidden)
        self.format_toolbar = QFrame()
        self.format_toolbar.setMaximumHeight(55)
        self.format_toolbar.setStyleSheet("""
            QFrame {
                background: #2b2b2b;
                border: 1px solid #555;
                border-radius: 4px;
                margin: 2px 0;
            }
            QLabel {
                color: #cccccc;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton, QToolButton {
                background: #3c3c3c;
                border: 1px solid #555;
                border-radius: 2px;
                color: #ffffff;
                font-weight: bold;
                min-width: 28px;
                max-width: 28px;
                min-height: 28px;
                max-height: 28px;
            }
            QPushButton:hover, QToolButton:hover {
                background: #4a4a4a;
                border: 1px solid #0078d4;
            }
            QPushButton:pressed, QToolButton:pressed {
                background: #555;
            }
            QPushButton:checked, QToolButton:checked {
                background: #0078d4;
                border: 1px solid #005a9e;
            }
            QComboBox {
                background: #3c3c3c;
                border: 1px solid #555;
                border-radius: 2px;
                padding: 4px 6px;
                color: #ffffff;
                min-width: 100px;
            }
            QComboBox:focus {
                border: 1px solid #0078d4;
            }
            QComboBox::drop-down {
                border: none;
                background: #3c3c3c;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #cccccc;
                margin-right: 5px;
            }
        """)
        
        toolbar_layout = QVBoxLayout(self.format_toolbar)
        toolbar_layout.setContentsMargins(15, 8, 15, 8)
        toolbar_layout.setSpacing(8)
        
        # First row: Font and basic formatting
        top_row = QHBoxLayout()
        top_row.setSpacing(15)
        
        # Font size controls
        font_group = QHBoxLayout()
        font_group.setSpacing(5)
        font_group.addWidget(QLabel("Font:"))
        
        self.font_decrease_btn = QPushButton("−")
        self.font_decrease_btn.setToolTip("Decrease font size")
        self.font_decrease_btn.clicked.connect(self.decrease_font_size)
        
        self.font_size_label = QLabel("11pt")
        self.font_size_label.setMinimumWidth(35)
        self.font_size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.font_size_label.setStyleSheet("""
            QLabel {
                background: #1e1e1e;
                border: 1px solid #555;
                border-radius: 2px;
                padding: 3px;
                color: #ffffff;
            }
        """)
        
        self.font_increase_btn = QPushButton("+")
        self.font_increase_btn.setToolTip("Increase font size")
        self.font_increase_btn.clicked.connect(self.increase_font_size)
        
        font_group.addWidget(self.font_decrease_btn)
        font_group.addWidget(self.font_size_label)
        font_group.addWidget(self.font_increase_btn)
        top_row.addLayout(font_group)
        
        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.VLine)
        separator1.setStyleSheet("color: #666;")
        top_row.addWidget(separator1)
        
        # List formatting controls
        list_group = QHBoxLayout()
        list_group.setSpacing(5)
        list_group.addWidget(QLabel("Lists:"))
        
        self.bullet_btn = QToolButton()
        self.bullet_btn.setText("•")
        self.bullet_btn.setToolTip("Toggle bullet list")
        self.bullet_btn.setCheckable(True)
        self.bullet_btn.clicked.connect(self.toggle_bullet_list)
        
        self.number_btn = QToolButton()
        self.number_btn.setText("1.")
        self.number_btn.setToolTip("Toggle numbered list")
        self.number_btn.setCheckable(True)
        self.number_btn.clicked.connect(self.toggle_numbered_list)
        
        # Create button group to make them mutually exclusive
        self.list_btn_group = QButtonGroup()
        self.list_btn_group.addButton(self.bullet_btn)
        self.list_btn_group.addButton(self.number_btn)
        self.list_btn_group.setExclusive(False)  # Allow both to be unchecked
        
        list_group.addWidget(self.bullet_btn)
        list_group.addWidget(self.number_btn)
        top_row.addLayout(list_group)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.VLine)
        separator2.setStyleSheet("color: #666;")
        top_row.addWidget(separator2)
        
        # Insert controls
        insert_group = QHBoxLayout()
        insert_group.setSpacing(5)
        insert_group.addWidget(QLabel("Insert:"))
        
        self.hr_btn = QPushButton("─")
        self.hr_btn.setToolTip("Insert horizontal line")
        self.hr_btn.clicked.connect(self.insert_horizontal_line)
        
        insert_group.addWidget(self.hr_btn)
        top_row.addLayout(insert_group)
        
        top_row.addStretch()
        toolbar_layout.addLayout(top_row)
        
        # Second row: Indent and spacing controls
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(15)
        
        # Indent size controls
        indent_group = QHBoxLayout()
        indent_group.setSpacing(5)
        indent_group.addWidget(QLabel("Indent:"))
        
        self.indent_decrease_btn = QPushButton("−")
        self.indent_decrease_btn.setToolTip("Decrease indent size")
        self.indent_decrease_btn.clicked.connect(self.decrease_indent_size)
        
        self.indent_size_label = QLabel("20px")
        self.indent_size_label.setMinimumWidth(40)
        self.indent_size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.indent_size_label.setStyleSheet("""
            QLabel {
                background: #1e1e1e;
                border: 1px solid #555;
                border-radius: 2px;
                padding: 3px;
                color: #ffffff;
            }
        """)
        
        self.indent_increase_btn = QPushButton("+")
        self.indent_increase_btn.setToolTip("Increase indent size")
        self.indent_increase_btn.clicked.connect(self.increase_indent_size)
        
        indent_group.addWidget(self.indent_decrease_btn)
        indent_group.addWidget(self.indent_size_label)
        indent_group.addWidget(self.indent_increase_btn)
        bottom_row.addLayout(indent_group)
        
        # Separator
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.Shape.VLine)
        separator3.setStyleSheet("color: #666;")
        bottom_row.addWidget(separator3)
        
        # Line spacing control
        spacing_group = QHBoxLayout()
        spacing_group.setSpacing(8)
        spacing_group.addWidget(QLabel("Spacing:"))
        self.line_spacing = QComboBox()
        self.line_spacing.addItems(["Single", "1.15", "1.5", "Double"])
        self.line_spacing.setCurrentText("1.15")
        self.line_spacing.currentTextChanged.connect(self.refresh_preview)
        spacing_group.addWidget(self.line_spacing)
        bottom_row.addLayout(spacing_group)
        
        # Separator
        separator4 = QFrame()
        separator4.setFrameShape(QFrame.Shape.VLine)
        separator4.setStyleSheet("color: #666;")
        bottom_row.addWidget(separator4)
        
        # Numbering style
        numbering_group = QHBoxLayout()
        numbering_group.setSpacing(8)
        numbering_group.addWidget(QLabel("Style:"))
        self.numbering_style = QComboBox()
        self.numbering_style.addItems([
            "Professional", 
            "Standard Lists", 
            "Academic"
        ])
        self.numbering_style.currentTextChanged.connect(self.refresh_preview)
        numbering_group.addWidget(self.numbering_style)
        bottom_row.addLayout(numbering_group)
        
        bottom_row.addStretch()
        toolbar_layout.addLayout(bottom_row)
        
        layout.addWidget(self.format_toolbar)
        self.format_toolbar.hide()  # Initially hidden

    def toggle_bullet_list(self):
        """Toggle bullet list formatting"""
        self.text_edit.toggle_bullet_list()
        self.update_list_button_states()

    def toggle_numbered_list(self):
        """Toggle numbered list formatting"""
        self.text_edit.toggle_numbered_list()
        self.update_list_button_states()

    def update_list_button_states(self):
        """Update the visual state of list buttons based on current cursor position"""
        cursor = self.text_edit.textCursor()
        current_list = cursor.currentList()
        
        # Reset button states
        self.bullet_btn.setChecked(False)
        self.number_btn.setChecked(False)
        
        if current_list:
            list_style = current_list.format().style()
            if list_style == QTextListFormat.Style.ListDisc:
                self.bullet_btn.setChecked(True)
            elif list_style == QTextListFormat.Style.ListDecimal:
                self.number_btn.setChecked(True)

    def insert_horizontal_line(self):
        """Insert a horizontal line"""
        self.text_edit.insert_horizontal_line()

    def increase_font_size(self):
        """Increase font size"""
        if self._font_size_value < 16:
            self._font_size_value += 1
            self.font_size_label.setText(f"{self._font_size_value}pt")
            self.refresh_preview()

    def decrease_font_size(self):
        """Decrease font size"""
        if self._font_size_value > 8:
            self._font_size_value -= 1
            self.font_size_label.setText(f"{self._font_size_value}pt")
            self.refresh_preview()

    def increase_indent_size(self):
        """Increase indent size"""
        if self._indent_size_value < 50:
            self._indent_size_value += 5
            self.indent_size_label.setText(f"{self._indent_size_value}px")
            self.text_edit.set_indent_size(self._indent_size_value)
            self.refresh_preview()

    def decrease_indent_size(self):
        """Decrease indent size"""
        if self._indent_size_value > 10:
            self._indent_size_value -= 5
            self.indent_size_label.setText(f"{self._indent_size_value}px")
            self.text_edit.set_indent_size(self._indent_size_value)
            self.refresh_preview()

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
        
        # Set default font and indent size
        font = QFont("Arial", self._font_size_value)
        self.text_edit.setFont(font)
        self.text_edit.set_indent_size(self._indent_size_value)
        
        # Connect cursor position changed to update button states
        self.text_edit.cursorPositionChanged.connect(self.update_list_button_states)

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
        font_size = self._font_size_value
        indent_size = self._indent_size_value
        line_height = self.get_line_height()
        style = self.numbering_style.currentText()
        
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
                html_content.append('<hr style="border: none; border-bottom: 2px solid #333; margin: 20px 0 15px 0;">')
                continue
            
            # Main section headers (all caps, **bold**)
            if line.startswith('**') and line.endswith('**'):
                section_title = line[2:-2].strip()
                if section_title.isupper():
                    section_counter += 1
                    subsection_counters[section_counter] = 0
                    
                    html_content.append('<hr style="border: none; border-bottom: 1px solid #333; margin: 15px 0 5px 0;">')
                    html_content.append(f'''
                    <h2 style="font-size: {font_size + 1}pt; font-weight: bold; margin: 15px 0 12px 0; 
                              text-align: left; letter-spacing: 0.5px; line-height: {line_height};">
                        {section_title}
                    </h2>
                    ''')
                else:
                    html_content.append(f'<p style="font-weight: bold; margin: 10px 0; font-size: {font_size}pt;">{section_title}</p>')
                continue
            
            # Process numbered/lettered items based on style
            formatted_line = self.format_line_with_hierarchy(line, font_size, indent_size, line_height, style)
            html_content.append(formatted_line)
        
        return ''.join(html_content)

    def format_line_with_hierarchy(self, line, font_size, indent_size, line_height, style):
        """Format a line based on its hierarchy level and selected style"""
        import re
        
        if style == "Professional":
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
        
        elif style == "Standard Lists":
            # Use bullet points and simple numbering
            if re.match(r'^\s*•\s+', line) or re.match(r'^\s*\*\s+', line):
                stripped_line = line.strip()[1:].strip()
                return f'''
                <ul style="margin: 4px 0; padding-left: {indent_size}px;">
                    <li style="font-size: {font_size}pt; line-height: {line_height};">
                        {stripped_line}
                    </li>
                </ul>
                '''
            elif re.match(r'^\s*\d+\.\s+', line):
                stripped_line = re.sub(r'^\s*\d+\.\s*', '', line.strip())
                return f'''
                <ol style="margin: 4px 0; padding-left: {indent_size}px;">
                    <li style="font-size: {font_size}pt; line-height: {line_height};">
                        {stripped_line}
                    </li>
                </ol>
                '''
        
        elif style == "Academic":
            # Roman numerals, letters, numbers
            if re.match(r'^\s*[IVX]+\.\s+', line):
                return f'''
                <p style="font-size: {font_size}pt; font-weight: bold; margin: 10px 0 6px 0; 
                         line-height: {line_height};">
                    {line.strip()}
                </p>
                '''
            elif re.match(r'^\s*[A-Z]\.\s+', line):
                return f'''
                <p style="font-size: {font_size}pt; margin: 6px 0 4px {indent_size}px; 
                         line-height: {line_height}; font-weight: 500;">
                    {line.strip()}
                </p>
                '''
        
        # Default formatting for regular text
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
        font_size = self._font_size_value
        indent_size = self._indent_size_value
        line_height = self.get_line_height()
        
        # Build CSS styles separately to avoid f-string backslash issues
        body_style = f'body {{ font-family: Arial, sans-serif; font-size: {font_size}pt; line-height: {line_height}; margin: 1in; color: #000; }}'
        h1_style = f'h1 {{ font-size: {font_size + 3}pt; text-align: center; margin-bottom: 25px; letter-spacing: 1px; }}'
        h2_style = f'h2 {{ font-size: {font_size + 1}pt; margin: 15px 0 12px 0; letter-spacing: 0.5px; }}'
        indent1_style = f'.indent-1 {{ margin-left: {indent_size}px; }}'
        indent2_style = f'.indent-2 {{ margin-left: {indent_size * 2}px; }}'
        indent3_style = f'.indent-3 {{ margin-left: {indent_size * 3}px; }}'
        
        html = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            '<meta charset="UTF-8">',
            '<title>Concrete Scope of Work</title>',
            '<style>',
            body_style,
            h1_style,
            h2_style,
            'hr { border: none; border-bottom: 1px solid #333; margin: 15px 0 5px 0; }',
            indent1_style,
            indent2_style,
            indent3_style,
            '.subsection { font-weight: bold; margin: 12px 0 8px 0; }',
            '.item { margin: 4px 0; text-align: justify; }',
            'ul, ol { margin: 4px 0; padding-left: 20px; }',
            'li { margin: 2px 0; }',
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