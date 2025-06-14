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
from flyff_browser.ui.auto_press import AutoPressControls

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
        
        # Create auto-press controls
        self.auto_press_controls = AutoPressControls(self)
        self.addToolBar(Qt.RightToolBarArea, self.auto_press_controls)

        # Initialize key simulators dictionary
        self.key_simulators = {}

        # Set up the main layout
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)

        # Create a widget to hold the layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Add the first tab
        self.add_new_tab()

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

    def close_tab(self, index):
        """Close a tab."""
        if self.tab_widget.count() > 1:  # Keep at least one tab
            self.tab_widget.removeTab(index)

    def add_key_simulator(self, control_id: int):
        """Add a new key simulator for a control."""
        self.key_simulators[control_id] = KeyPressSimulator(self.tab_widget.currentWidget())

    def remove_key_simulator(self, control_id: int):
        """Remove a key simulator."""
        if control_id in self.key_simulators:
            self.key_simulators[control_id].stop()
            del self.key_simulators[control_id]

    def connect_key_control(self, control_id: int, control):
        """Connect a key control to its simulator."""
        control.toggle_btn.clicked.connect(
            lambda: self.toggle_auto_press(control_id))

    def toggle_auto_press(self, control_id: int):
        control = self.auto_press_controls.key_controls[control_id - 1]
        
        if control.toggle_btn.isChecked():
            key_name = control.key_combo.currentText()
            config = KeyPressConfig(
                min_interval=control.min_spin.value(),
                max_interval=control.max_spin.value(),
                key=key_name,
                key_code=get_key_config(key_name).key_code,
                key_name=get_key_config(key_name).key_name
            )
            self.key_simulators[control_id].start(
                config, 
                lambda: self.key_simulators[control_id]._schedule_next_press(lambda: None)
            )
            control.toggle_btn.setText('Deactivate')
        else:
            self.key_simulators[control_id].stop()
            control.toggle_btn.setText('Activate')

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