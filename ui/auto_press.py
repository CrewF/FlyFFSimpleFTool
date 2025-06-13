from PyQt5.QtWidgets import (QToolBar, QPushButton, QCheckBox, QLabel, 
                           QSpinBox, QWidget, QVBoxLayout, QComboBox,
                           QGroupBox, QHBoxLayout, QScrollArea)
from PyQt5.QtCore import Qt

from flyff_browser.config import AVAILABLE_KEYS

class KeyPressControl(QGroupBox):
    def __init__(self, title: str, parent=None, on_remove=None):
        super().__init__(title, parent)
        self.on_remove = on_remove
        self.setFixedHeight(180)  # Set fixed height for the control
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)  # Add padding inside the group box
        
        # Key selection
        key_layout = QHBoxLayout()
        key_label = QLabel('Key:')
        self.key_combo = QComboBox()
        for key, _, _ in AVAILABLE_KEYS:
            self.key_combo.addItem(key)
        key_layout.addWidget(key_label)
        key_layout.addWidget(self.key_combo)
        layout.addLayout(key_layout)

        # Interval controls
        interval_layout = QHBoxLayout()
        
        # Min interval
        min_layout = QVBoxLayout()
        min_label = QLabel('Min Interval (s):')
        self.min_spin = QSpinBox()
        self.min_spin.setRange(1, 9999)
        self.min_spin.setValue(3)
        min_layout.addWidget(min_label)
        min_layout.addWidget(self.min_spin)
        interval_layout.addLayout(min_layout)

        # Max interval
        max_layout = QVBoxLayout()
        max_label = QLabel('Max Interval (s):')
        self.max_spin = QSpinBox()
        self.max_spin.setRange(1, 9999)
        self.max_spin.setValue(6)
        max_layout.addWidget(max_label)
        max_layout.addWidget(self.max_spin)
        interval_layout.addLayout(max_layout)

        layout.addLayout(interval_layout)

        # Toggle button
        self.toggle_btn = QPushButton('Activate')
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setFixedHeight(30)  # Make the button taller
        layout.addWidget(self.toggle_btn)

        self.setLayout(layout)

        # Add remove button to title
        if self.on_remove:
            remove_btn = QPushButton('×')
            remove_btn.setFixedWidth(20)
            remove_btn.setFixedHeight(20)
            remove_btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    background-color: transparent;
                    color: #666;
                    font-weight: bold;
                }
                QPushButton:hover {
                    color: #ff0000;
                }
            """)
            remove_btn.clicked.connect(self.on_remove)
            
            # Create a widget to hold the title and remove button
            title_widget = QWidget()
            title_layout = QHBoxLayout()
            title_layout.setContentsMargins(0, 0, 0, 0)
            title_layout.setSpacing(2)
            
            # Add the title text
            title_label = QLabel(self.title())
            title_layout.addWidget(title_label)
            
            # Add the remove button
            title_layout.addWidget(remove_btn)
            
            title_widget.setLayout(title_layout)
            self.setTitle("")  # Clear the default title
            self.layout().insertWidget(0, title_widget)  # Add at the top of the layout

class AutoPressControls(QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.key_controls = []
        self.setFixedWidth(225)  # Reduced from 300 to 250
        self._setup_ui()

    def _setup_ui(self):
        # Create main container
        main_container = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)  # Add some padding
        main_container.setLayout(main_layout)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Create scroll content widget
        scroll_content = QWidget()
        self.layout = QVBoxLayout()
        self.layout.setSpacing(10)  # Add spacing between controls
        self.layout.setAlignment(Qt.AlignTop)  # Align controls to the top
        scroll_content.setLayout(self.layout)

        # Add button (outside scroll area)
        add_btn = QPushButton('+ Add Key')
        add_btn.setFixedHeight(30)  # Make the button taller
        add_btn.clicked.connect(self.add_key_control)
        main_layout.addWidget(add_btn)

        # Add scroll area
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # Add the main container to the toolbar
        self.addWidget(main_container)

    def add_key_control(self):
        control_id = len(self.key_controls) + 1
        control = KeyPressControl(
            f'Key {control_id}',
            on_remove=lambda: self.remove_key_control(control)
        )
        self.key_controls.append(control)
        self.parent().add_key_simulator(control_id)
        self.parent().connect_key_control(control_id, control)
        
        # Add the control to the scroll area's layout
        self.layout.addWidget(control)

    def remove_key_control(self, control):
        control_id = self.key_controls.index(control) + 1
        self.key_controls.remove(control)
        self.parent().remove_key_simulator(control_id)
        control.deleteLater()
        
        # Renumber remaining controls
        for i, ctrl in enumerate(self.key_controls, 1):
            ctrl.setTitle(f'Key {i}') 