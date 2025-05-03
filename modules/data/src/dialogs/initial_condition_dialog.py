from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QFormLayout
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QVBoxLayout

from modules.data.src.dialogs.dialog import Dialog
from modules.data.src.physics.turbulence_models import InitialCondition
from modules.data.src.physics.turbulence_models import TurbulenceModel


class InitialConditionDialog(Dialog):
    def __init__(self, initial_conditions, turbulence_model, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Initial Conditions")

        layout = QVBoxLayout()

        # Поля скорости
        form = QFormLayout()
        self.velocity_x = QLineEdit(str(initial_conditions.velocity[0]))
        self.velocity_y = QLineEdit(str(initial_conditions.velocity[1]))
        form.addRow("Velocity X (m/s):", self.velocity_x)
        form.addRow("Velocity Y (m/s):", self.velocity_y)

        # Параметры турбулентности
        if turbulence_model != TurbulenceModel.LAMINAR:
            self.turb_k = QLineEdit(str(initial_conditions.turbulent_k))
            form.addRow("Turbulent Kinetic Energy (k):", self.turb_k)

        layout.addLayout(form)

        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_data(self):
        velocity = (
            float(self.velocity_x.text()),
            float(self.velocity_y.text())
        )
        turbulent_k = float(self.turb_k.text()) if hasattr(self, 'turb_k') else 0.0
        return InitialCondition(velocity=velocity, turbulent_k=turbulent_k)