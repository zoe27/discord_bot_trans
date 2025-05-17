import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QIcon

class DraggableWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(500, 80)
        self.setStyleSheet("background-color: #f2f2f2; border-radius: 10px;")

        self.initUI()
        self.oldPos = self.pos()

    def initUI(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        icons = [
            ("🅧", self.on_close),
            ("🪟", self.on_button1),
            ("🖥️", self.on_button2),
            ("⬚", self.on_button3),
            ("⛶", self.on_button4),
            ("⧉", self.on_button5),
        ]

        for icon, callback in icons:
            btn = QPushButton(icon)
            btn.setFixedSize(40, 40)
            btn.setStyleSheet(
                "background-color: white; border: 1px solid #ccc; border-radius: 5px;"
            )
            btn.clicked.connect(callback)
            layout.addWidget(btn)

        # "选项" 和 "录制" 模拟
        option_label = QLabel("选项 ▼")
        record_label = QLabel("录制")
        option_label.setFixedWidth(60)
        record_label.setFixedWidth(40)

        layout.addWidget(option_label)
        layout.addWidget(record_label)

        self.setLayout(layout)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def on_close(self):
        self.close()

    def on_button1(self):
        print("点击了按钮 1")

    def on_button2(self):
        print("点击了按钮 2")

    def on_button3(self):
        print("点击了按钮 3")

    def on_button4(self):
        print("点击了按钮 4")

    def on_button5(self):
        print("点击了按钮 5")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DraggableWindow()
    window.show()
    sys.exit(app.exec_())
