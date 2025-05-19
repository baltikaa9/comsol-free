from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QFormLayout
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QWidget

from modules.data.src.dialogs.dialog import Dialog


class EllipseDialog(Dialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setWindowTitle('Draw Ellipse by Parameters')
        layout = QFormLayout()

        self.center_x = QLineEdit('0')
        self.center_y = QLineEdit('0')
        self.radius_x = QLineEdit('180')
        self.radius_y = QLineEdit('180')

        layout.addRow('Center X:', self.center_x)
        layout.addRow('Center Y:', self.center_y)
        layout.addRow('Radius X:', self.radius_x)
        layout.addRow('Radius Y:', self.radius_y)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_data(self) -> dict[str, QPointF | float] | None:
        try:
            return {
                'center': QPointF(float(self.center_x.text()), float(self.center_y.text())),
                'radius_x': float(self.radius_x.text()),
                'radius_y': float(self.radius_y.text())
            }
        except ValueError:
            return None