from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt

class PositionAdjustDialog(QDialog):
    def __init__(self, ros_worker, parent=None):
        super().__init__(parent)
        self.ros_worker = ros_worker
        self.offset = 0.0

        self.setWindowTitle("Adjust position")

        layout = QVBoxLayout(self)

        self.label = QLabel("Offset: 0")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        btn_layout = QHBoxLayout()
        layout.addLayout(btn_layout)

        for text, value in [("-5", -5), ("-1", -1), ("+1", 1), ("+5", 5)]:
            btn = QPushButton(text)
            btn.clicked.connect(lambda _, v=value: self.adjust(v))
            btn_layout.addWidget(btn)

        confirm = QPushButton("Confirm")
        confirm.clicked.connect(self.confirm)
        layout.addWidget(confirm)

    def adjust(self, value):
        self.offset += value
        self.label.setText(f"Offset: {self.offset}")
        self.ros_worker.publish_float("/gui/offset", self.offset)

    def confirm(self):
        self.ros_worker.publish_empty("/gui/offset_complete")
        self.accept()
