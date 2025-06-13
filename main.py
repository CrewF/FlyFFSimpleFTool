import sys
import json
import os
from PyQt5.QtCore import QUrl, Qt, QObject, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor

from flyff_browser.config import KeyPressConfig, get_key_config
from flyff_browser.key_simulator import KeyPressSimulator
from flyff_browser.ui.auto_press import AutoPressControls

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

        # Create the web view with custom page
        self.web_view = QWebEngineView()
        self.web_page = CustomWebPage(self.web_view)
        self.web_view.setPage(self.web_page)
        
        # Connect to URL changed signal
        self.web_view.urlChanged.connect(self.on_url_changed)
        
        # Set initial URL
        self.web_view.setUrl(QUrl("https://universe.flyff.com/play"))

        # Create auto-press controls
        self.auto_press_controls = AutoPressControls(self)
        self.addToolBar(Qt.RightToolBarArea, self.auto_press_controls)

        # Initialize key simulators dictionary
        self.key_simulators = {}

        # Set up the main layout
        layout = QVBoxLayout()
        layout.addWidget(self.web_view)

        # Create a widget to hold the layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def add_key_simulator(self, control_id: int):
        """Add a new key simulator for a control."""
        self.key_simulators[control_id] = KeyPressSimulator(self.web_view)

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