from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QFormLayout
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QWidget

from src.dialogs.dialog import Dialog


class RectDialog(Dialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setWindowTitle('Draw Rectangle by Parameters')
        layout = QFormLayout()

        self.top_left_x = QLineEdit('0')
        self.top_left_y = QLineEdit('0')
        self.width = QLineEdit('180')
        self.height = QLineEdit('180')

        layout.addRow('Bot-Left X:', self.top_left_x)
        layout.addRow('Bot-Left Y:', self.top_left_y)
        layout.addRow('Width:', self.width)
        layout.addRow('Height:', self.height)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_data(self):
        try:
            return {
                'top_left_x': float(self.top_left_x.text()),
                'top_left_y': float(self.top_left_y.text()),
                'width': float(self.width.text()),
                'height': float(self.height.text())
            }
        except ValueError:
            return None