from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QFormLayout
from PySide6.QtWidgets import QLineEdit

from modules.data.src.dialogs.dialog import Dialog
from modules.data.src.physics.turbulence_models import TurbulenceModel
from modules.data.src.physics.turbulence_models import TurbulenceParams


class TurbulenceDialog(Dialog):
    def __init__(self, params: TurbulenceParams, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Выбор турбулентности')

        layout = QFormLayout()

        self.model_combo = QComboBox()
        for model in TurbulenceModel:
            self.model_combo.addItem(model.value, model)

        index = list(TurbulenceModel).index(params.model)
        self.model_combo.setCurrentIndex(index)
        layout.addRow("Модель:", self.model_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def get_data(self):
        return TurbulenceParams(
            model=self.model_combo.currentData(),
        )