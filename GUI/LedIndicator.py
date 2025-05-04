from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor, QPainter, QBrush


class LedIndicator(QWidget):
    def __init__(self, color=Qt.gray, size=14, parent=None):
        super().__init__(parent)
        self._color = color
        self._size = size
        self.setFixedSize(size, size)

    def activate(self):
        self._color = Qt.green
        self.update()

    def deactivate(self):
        self._color = Qt.gray
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        brush = QBrush(self._color)
        painter.setBrush(brush)
        painter.setPen(Qt.black)
        painter.drawEllipse(0, 0, self._size, self._size)
