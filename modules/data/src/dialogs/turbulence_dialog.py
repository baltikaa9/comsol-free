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
        self.setWindowTitle("Turbulence Model Settings")

        layout = QFormLayout()

        self.model_combo = QComboBox()
        for model in TurbulenceModel:
            self.model_combo.addItem(model.value, model)
        layout.addRow("Model:", self.model_combo)

        self.density_edit = QLineEdit(str(params.density))
        layout.addRow("Density (kg/m³):", self.density_edit)

        self.viscosity_edit = QLineEdit(str(params.viscosity))
        layout.addRow("Viscosity (Pa·s):", self.viscosity_edit)

        self.turb_intensity = QLineEdit(str(params.turbulent_intensity))
        layout.addRow("Turb. Intensity:", self.turb_intensity)

        self.length_scale = QLineEdit(str(params.spec_length_scale))
        layout.addRow("Length Scale (m):", self.length_scale)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def get_data(self):
        return TurbulenceParams(
            model=self.model_combo.currentData(),
            density=float(self.density_edit.text()),
            viscosity=float(self.viscosity_edit.text()),
            turbulent_intensity=float(self.turb_intensity.text()),
            spec_length_scale=float(self.length_scale.text())
        )