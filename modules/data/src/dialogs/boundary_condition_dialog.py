from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QFormLayout
from PySide6.QtWidgets import QLineEdit

from modules.data.src.dialogs.dialog import Dialog
from modules.data.src.physics.turbulence_models import BoundaryCondition
from modules.data.src.physics.turbulence_models import TurbulenceModel


class BoundaryConditionDialog(Dialog):
    def __init__(self, model: TurbulenceModel, bc: BoundaryCondition = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Boundary Condition")
        self.bc = bc or BoundaryCondition(
            name="New BC",
            bc_type="velocity",
            values={"velocity": (0, 0)}
        )

        layout = QFormLayout()

        self.type_combo = QComboBox()
        self.type_combo.addItems(["velocity", "pressure", "wall"])
        layout.addRow("Type:", self.type_combo)

        self.velocity_x = QLineEdit("0")
        self.velocity_y = QLineEdit("0")
        layout.addRow("Velocity X (m/s):", self.velocity_x)
        layout.addRow("Velocity Y (m/s):", self.velocity_y)

        if model != TurbulenceModel.LAMINAR:
            self.turb_intensity = QLineEdit("0.05")
            layout.addRow("Turb. Intensity:", self.turb_intensity)

            self.turb_length = QLineEdit("0.01")
            layout.addRow("Turb. Length (m):", self.turb_length)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

        if bc:
            self.type_combo.setCurrentText(bc.bc_type)
            self.velocity_x.setText(str(bc.values.get("velocity", (0, 0))[0]))
            self.velocity_y.setText(str(bc.values.get("velocity", (0, 0))[1]))
            if "turbulent_intensity" in bc.values:
                self.turb_intensity.setText(str(bc.values["turbulent_intensity"]))
                self.turb_length.setText(str(bc.values["turbulent_length"]))

    def get_data(self) -> BoundaryCondition:
        return BoundaryCondition(
            name=self.bc.name,
            bc_type=self.type_combo.currentText(),
            values=self.get_values()
        )

    def get_values(self):
        values = {
            "velocity": (
                float(self.velocity_x.text()),
                float(self.velocity_y.text())
            )
        }
        if hasattr(self, 'turb_intensity'):
            values.update({
                "turbulent_intensity": float(self.turb_intensity.text()),
                "turbulent_length": float(self.turb_length.text())
            })
        return values