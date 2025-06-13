import random
from typing import Optional, Callable
from PyQt5.QtCore import QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView

class KeyPressSimulator:
    def __init__(self, web_view: QWebEngineView):
        self.web_view = web_view
        self.timer = QTimer()
        self.is_active = False
        self.config: Optional['KeyPressConfig'] = None

    def start(self, config: 'KeyPressConfig', callback: Callable[[], None]):
        self.config = config
        self.is_active = True
        self._schedule_next_press(callback)

    def stop(self):
        self.is_active = False
        self.timer.stop()

    def _schedule_next_press(self, callback: Callable[[], None]):
        if not self.is_active or not self.config:
            return

        min_ms = self.config.min_interval * 1000
        max_ms = self.config.max_interval * 1000
        if min_ms > max_ms:
            min_ms, max_ms = max_ms, min_ms

        new_interval = random.randint(min_ms, max_ms)
        
        self.timer.stop()
        self.timer.start(new_interval)
        self.timer.timeout.connect(lambda: self._simulate_press(callback))

    def _simulate_press(self, callback: Callable[[], None]):
        if not self.is_active or not self.config:
            return

        js_code = (
            "(function(){"
            "const canvas=document.querySelector('canvas');"
            f"function sendKeyEvent(type){{"
            f"const event=new KeyboardEvent(type,{{key:'{self.config.key}',code:'{self.config.key_name}',"
            f"keyCode:{self.config.key_code},which:{self.config.key_code},bubbles:true,cancelable:true}});"
            "if(canvas){canvas.focus();canvas.dispatchEvent(event);console.log('Dispatched '+type+' to canvas');}"
            "else{document.dispatchEvent(event);console.log('Dispatched '+type+' to document');}"
            "}"
            "sendKeyEvent('keydown');"
            "setTimeout(function(){sendKeyEvent('keyup');},100);"
            "})();"
        )
        self.web_view.page().runJavaScript(js_code, self._handle_js_result)
        callback()

    def _handle_js_result(self, result):
        pass 