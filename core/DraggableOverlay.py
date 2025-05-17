from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QWidget
import logging


class DraggableOverlay(QWidget):
    def __init__(self, rect, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)  # Keep mouse events
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(rect)
        logging.info(f"Created DraggableOverlay with geometry: {rect}")

        self.dragging = False
        self.offset = QPoint()
        self.setMouseTracking(True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw very transparent background (almost clear)
        painter.setOpacity(0.1)
        painter.fillRect(self.rect(), Qt.gray)

        # Draw border with higher opacity
        painter.setOpacity(0.8)
        pen = QPen(Qt.red, 1.5, Qt.SolidLine)  # Changed to red solid line for better visibility
        painter.setPen(pen)
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

    def enterEvent(self, event):
        self.setCursor(Qt.SizeAllCursor)
        logging.debug("Mouse entered overlay")

    def leaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        logging.debug("Mouse left overlay")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.globalPos() - self.pos()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = event.globalPos() - self.offset
            self.move(new_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.setCursor(Qt.SizeAllCursor)