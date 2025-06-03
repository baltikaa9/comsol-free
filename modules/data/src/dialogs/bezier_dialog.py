from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QFormLayout
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QWidget

from src.dialogs.dialog import Dialog


class BezierDialog(Dialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setWindowTitle('Draw Bezier Curve by Parameters')
        layout = QFormLayout()

        self.p0_x = QLineEdit('0')
        self.p0_y = QLineEdit('0')
        self.p1_x = QLineEdit('50')
        self.p1_y = QLineEdit('100')
        self.p2_x = QLineEdit('150')
        self.p2_y = QLineEdit('100')
        self.p3_x = QLineEdit('200')
        self.p3_y = QLineEdit('0')

        layout.addRow('Point 0 X:', self.p0_x)
        layout.addRow('Point 0 Y:', self.p0_y)
        layout.addRow('Point 1 X:', self.p1_x)
        layout.addRow('Point 1 Y:', self.p1_y)
        layout.addRow('Point 2 X:', self.p2_x)
        layout.addRow('Point 2 Y:', self.p2_y)
        layout.addRow('Point 3 X:', self.p3_x)
        layout.addRow('Point 3 Y:', self.p3_y)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_data(self):
        try:
            return [
                QPointF(float(self.p0_x.text()), float(self.p0_y.text())),
                QPointF(float(self.p1_x.text()), float(self.p1_y.text())),
                QPointF(float(self.p2_x.text()), float(self.p2_y.text())),
                QPointF(float(self.p3_x.text()), float(self.p3_y.text()))
            ]
        except ValueError:
            return None