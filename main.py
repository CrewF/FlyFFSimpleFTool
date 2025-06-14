import sys
import json
import os
from PyQt5.QtCore import QUrl, Qt, QObject, pyqtSlot
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                            QTabWidget, QPushButton, QHBoxLayout, QStyle, QTabBar)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor

from flyff_browser.config import KeyPressConfig, get_key_config
from flyff_browser.key_simulator import KeyPressSimulator
from flyff_browser.ui.auto_press import AutoPressControls, KeyPressControl

class CustomTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        
        # Create and add the new tab button
        self.new_tab_button = QPushButton("+")
        self.new_tab_button.setFixedSize(24, 24)
        self.new_tab_button.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                color: #666;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #000;
            }
        """)
        self.new_tab_button.clicked.connect(self.parent().add_new_tab)
        
        # Add the button to the tab bar
        self.tabBar().setDrawBase(False)  # Remove the base line of the tab bar
        self.tabBar().setExpanding(False)  # Prevent tabs from expanding
        self.tabBar().setElideMode(Qt.ElideRight)  # Elide text if it's too long
        
        # Add the button as a tab
        self.addTab(QWidget(), "")  # Add an empty tab
        self.tabBar().setTabButton(self.count() - 1, QTabBar.RightSide, self.new_tab_button)
        self.tabBar().setTabEnabled(self.count() - 1, False)  # Disable the tab itself
        
        # Move the new tab button to the right side
        self.tabBar().setMovable(False)  # Prevent tab movement
        self.tabBar().setDocumentMode(True)  # Use document mode for better appearance
        
    def addTab(self, widget, label):
        # Insert the new tab before the last tab (which contains the + button)
        index = self.count() - 1
        return super().insertTab(index, widget, label)

class CustomWebPage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)

    def javaScriptConsoleMessage(self, level, message, line, source):
        pass

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        return super().acceptNavigationRequest(url, _type, isMainFrame)

class FlyffBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FlyFF Universe Simple FTool')
        self.setGeometry(100, 100, 1024, 768)

        # Create the tab widget
        self.tab_widget = CustomTabWidget(self)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # Create auto-press controls
        self.auto_press_controls = AutoPressControls(self, on_add_key=self.add_key_control)
        self.addToolBar(Qt.RightToolBarArea, self.auto_press_controls)

        # Initialize dictionaries for each tab
        self.tab_key_simulators = {}
        self.tab_key_configs = {}  # Store key configurations for each tab

        # Set up the main layout
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)

        # Create a widget to hold the layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Add the first tab
        self.add_new_tab()

    def on_tab_changed(self, index):
        """Handle tab changes."""
        # Update current tab index
        self._current_tab_index = index
        
        # Update the auto-press controls to show the current tab's controls
        self.update_auto_press_controls()

    def update_auto_press_controls(self):
        """Update the auto-press controls to show the current tab's controls."""
        # Clear existing controls
        for control in self.auto_press_controls.key_controls:
            control.deleteLater()
        self.auto_press_controls.key_controls.clear()
        
        # Add controls for current tab
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index in self.tab_key_configs:
            for i, config in enumerate(self.tab_key_configs[current_tab_index], 1):
                # Create the control first
                control = KeyPressControl(f'Key {i}', on_remove=None)
                
                # Now create the remove handler with the existing control
                def create_remove_handler(ctrl):
                    return lambda: self.auto_press_controls.remove_key_control(ctrl)
                control.on_remove = create_remove_handler(control)
                
                # Set up the control's state
                control.key_combo.setCurrentText(config['key'])
                control.min_spin.setValue(config['min_interval'])
                control.max_spin.setValue(config['max_interval'])
                if config['active']:
                    control.toggle_btn.setChecked(True)
                    control.toggle_btn.setText('Deactivate')
                
                # Add the control to the UI
                self.auto_press_controls.key_controls.append(control)
                self.auto_press_controls.layout.addWidget(control)
                self.connect_key_control(i, control)

    def add_new_tab(self):
        """Add a new tab with a web view."""
        web_view = QWebEngineView()
        web_page = CustomWebPage(web_view)
        web_view.setPage(web_page)
        
        # Connect to URL changed signal
        web_view.urlChanged.connect(self.on_url_changed)
        
        # Set initial URL
        web_view.setUrl(QUrl("https://universe.flyff.com/play"))
        
        # Add tab
        index = self.tab_widget.addTab(web_view, "FlyFF Universe")
        self.tab_widget.setCurrentIndex(index)
        
        # Initialize key simulators and configurations for this tab
        self.tab_key_simulators[index] = {}
        self.tab_key_configs[index] = []

    def close_tab(self, index):
        """Close a tab."""
        if self.tab_widget.count() > 1:  # Keep at least one tab
            # Stop all key simulators for this tab
            if index in self.tab_key_simulators:
                for simulator in self.tab_key_simulators[index].values():
                    simulator.stop()
                del self.tab_key_simulators[index]
            
            # Remove key configurations for this tab
            if index in self.tab_key_configs:
                del self.tab_key_configs[index]
            
            self.tab_widget.removeTab(index)

    def add_key_simulator(self, control_id: int):
        """Add a new key simulator for a control."""
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index not in self.tab_key_simulators:
            self.tab_key_simulators[current_tab_index] = {}
        self.tab_key_simulators[current_tab_index][control_id] = KeyPressSimulator(self.tab_widget.currentWidget())

    def remove_key_simulator(self, control_id: int):
        """Remove a key simulator."""
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index in self.tab_key_simulators and control_id in self.tab_key_simulators[current_tab_index]:
            self.tab_key_simulators[current_tab_index][control_id].stop()
            del self.tab_key_simulators[current_tab_index][control_id]

    def connect_key_control(self, control_id: int, control):
        """Connect a key control to its simulator."""
        control.toggle_btn.clicked.connect(
            lambda: self.toggle_auto_press(control_id))

    def toggle_auto_press(self, control_id: int):
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index not in self.tab_key_simulators:
            self.tab_key_simulators[current_tab_index] = {}
            
        control = self.auto_press_controls.key_controls[control_id - 1]
        
        # Update the configuration for this tab
        if current_tab_index not in self.tab_key_configs:
            self.tab_key_configs[current_tab_index] = []
        while len(self.tab_key_configs[current_tab_index]) < control_id:
            self.tab_key_configs[current_tab_index].append({})
        
        config = {
            'key': control.key_combo.currentText(),
            'min_interval': control.min_spin.value(),
            'max_interval': control.max_spin.value(),
            'active': control.toggle_btn.isChecked()
        }
        self.tab_key_configs[current_tab_index][control_id - 1] = config
        
        if control.toggle_btn.isChecked():
            key_name = control.key_combo.currentText()
            key_config = KeyPressConfig(
                min_interval=control.min_spin.value(),
                max_interval=control.max_spin.value(),
                key=key_name,
                key_code=get_key_config(key_name).key_code,
                key_name=get_key_config(key_name).key_name
            )
            self.tab_key_simulators[current_tab_index][control_id].start(
                key_config, 
                lambda: self.tab_key_simulators[current_tab_index][control_id]._schedule_next_press(lambda: None)
            )
            control.toggle_btn.setText('Deactivate')
        else:
            if current_tab_index in self.tab_key_simulators and control_id in self.tab_key_simulators[current_tab_index]:
                self.tab_key_simulators[current_tab_index][control_id].stop()
            control.toggle_btn.setText('Activate')

    def add_key_control(self):
        """Add a new key control."""
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index not in self.tab_key_configs:
            self.tab_key_configs[current_tab_index] = []
            
        control_id = len(self.tab_key_configs[current_tab_index]) + 1
        control = KeyPressControl(
            f'Key {control_id}',
            on_remove=lambda: self.auto_press_controls.remove_key_control(control)
        )
        self.auto_press_controls.key_controls.append(control)
        self.auto_press_controls.layout.addWidget(control)
        self.add_key_simulator(control_id)
        self.connect_key_control(control_id, control)
        
        # Initialize the configuration for this control
        self.tab_key_configs[current_tab_index].append({
            'key': control.key_combo.currentText(),
            'min_interval': control.min_spin.value(),
            'max_interval': control.max_spin.value(),
            'active': False
        })

    def on_url_changed(self, url):
        """Handle URL changes to detect login page."""
        pass

def main():
    app = QApplication(sys.argv)
    browser = FlyffBrowser()
    browser.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 