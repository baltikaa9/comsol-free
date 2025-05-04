from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QDoubleSpinBox
from PySide6.QtWidgets import QFormLayout

from modules.data.src.dialogs.dialog import Dialog
from modules.data.src.physics.turbulence_models import InitialConditions


class InitialConditionsDialog(Dialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Начальные условия")
        layout = QFormLayout()
        self.u_input = QDoubleSpinBox()
        self.v_input = QDoubleSpinBox()
        self.p_input = QDoubleSpinBox()
        self.k_input = QDoubleSpinBox()
        self.omega_input = QDoubleSpinBox()

        for w in [self.u_input, self.v_input, self.p_input, self.k_input, self.omega_input]:
            w.setRange(-1e3, 1e3)

        layout.addRow("Скорость u (x):", self.u_input)
        layout.addRow("Скорость v (y):", self.v_input)
        layout.addRow("Давление p:", self.p_input)
        layout.addRow("k (turb. energy):", self.k_input)
        layout.addRow("ω (spec. dissipation):", self.omega_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def get_data(self) -> InitialConditions:
        return InitialConditions(
            self.u_input.value(),
            self.v_input.value(),
            self.p_input.value(),
            self.k_input.value(),
            self.omega_input.value(),
        )
