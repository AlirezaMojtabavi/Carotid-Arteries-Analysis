from PyQt5.QtCore import pyqtSignal, QObject


class ConsoleOutput(QObject):
    """ Redirect print output to GUI using Qt Signals """
    new_text = pyqtSignal(str)

    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.new_text.connect(self.update_text)

    def write(self, text):
        """Emit text and ensure UI updates immediately."""
        if text.strip():  # Avoid unnecessary empty lines
            self.new_text.emit(text)

    def flush(self):
        """For compatibility with sys.stdout"""
        pass

    def update_text(self, text):
        """ Append text safely in the GUI thread """
        self.text_widget.appendPlainText(text.strip())
        self.text_widget.verticalScrollBar().setValue(self.text_widget.verticalScrollBar().maximum())  # Auto-scroll
