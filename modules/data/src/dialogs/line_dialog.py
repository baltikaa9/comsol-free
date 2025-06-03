from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QFormLayout
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QWidget

from src.dialogs.dialog import Dialog


class LineDialog(Dialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setWindowTitle('Draw Line by Parameters')
        layout = QFormLayout()

        self.start_x = QLineEdit('0')
        self.start_y = QLineEdit('0')
        self.end_x = QLineEdit('100')
        self.end_y = QLineEdit('100')

        layout.addRow('Start X:', self.start_x)
        layout.addRow('Start Y:', self.start_y)
        layout.addRow('End X:', self.end_x)
        layout.addRow('End Y:', self.end_y)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_data(self):
        try:
            return {
                'start': QPointF(float(self.start_x.text()), float(self.start_y.text())),
                'end': QPointF(float(self.end_x.text()), float(self.end_y.text()))
            }
        except ValueError:
            return None