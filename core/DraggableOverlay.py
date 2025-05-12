from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QWidget
import logging


class DraggableOverlay(QWidget):
    def __init__(self, rect, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(rect)
        logging.info(f"Created DraggableOverlay with geometry: {rect}")

        self.dragging = False
        self.offset = QPoint()

        # Set mouse tracking to detect mouse enter/leave events
        self.setMouseTracking(True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(Qt.white, 2, Qt.DashLine)
        painter.setPen(pen)
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
        logging.debug("Overlay painted with white dashed border")

    def enterEvent(self, event):
        self.setCursor(Qt.SizeAllCursor)
        logging.debug("Mouse entered overlay")

    def leaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        logging.debug("Mouse left overlay")

    def mousePressEvent(self, event):
        logging.info(f"Mouse pressed at {event.globalPos()} with button {event.button()}")
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.globalPos() - self.pos()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        logging.info(f"Mouse moved to {event.globalPos()} with button {event.button()}")
        if self.dragging:
            new_pos = event.globalPos() - self.offset
            self.move(new_pos)

    def mouseReleaseEvent(self, event):
        logging.info(f"Mouse released at {event.globalPos()} with button {event.button()}")
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.setCursor(Qt.SizeAllCursor)