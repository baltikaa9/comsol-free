from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QDoubleSpinBox
from PySide6.QtWidgets import QFormLayout
from PySide6.QtWidgets import QWidget

from modules.data.src.dialogs.dialog import Dialog


class MeshDialog(Dialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setWindowTitle('Параметры сетки')

        self.dx_spin = QDoubleSpinBox()

        self.dx_spin.setDecimals(2)
        self.dx_spin.setRange(0.01, 100.0)
        self.dx_spin.setValue(1)
        self.dx_spin.setSingleStep(0.01)

        layout = QFormLayout(self)
        layout.addRow('Максимальный размер элемента', self.dx_spin)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        box = QDialogButtonBox(buttons)
        box.accepted.connect(self.accept)
        box.rejected.connect(self.reject)
        layout.addWidget(box)

    def get_data(self) -> float:
        return self.dx_spin.value()