from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QDoubleSpinBox
from PySide6.QtWidgets import QFormLayout

from src.dialogs.dialog import Dialog
from src.physics.turbulence_models import InitialConditions
from src.physics.turbulence_models import TurbulenceModel


class InitialConditionsDialog(Dialog):
    def __init__(self, turb_type: TurbulenceModel):
        super().__init__()
        self.setWindowTitle("Начальные условия")
        layout = QFormLayout()
        self.u_input = QDoubleSpinBox()
        self.v_input = QDoubleSpinBox()
        self.p_input = QDoubleSpinBox()
        self.k_input = QDoubleSpinBox()
        self.om_input = QDoubleSpinBox()

        for w in [self.u_input, self.v_input, self.p_input, self.k_input, self.om_input]:
            w.setRange(-1e3, 1e3)

        self.u_input.setValue(0)
        self.v_input.setValue(0)
        self.p_input.setValue(0)
        self.k_input.setDecimals(8)
        self.k_input.setValue(4.184e-7)
        self.om_input.setValue(2.78)

        self.u_input.setSuffix(' м/с')
        self.v_input.setSuffix(' м/с')
        self.p_input.setSuffix(' Па')
        self.k_input.setSuffix(' м²/м²')
        self.om_input.setSuffix(' 1/с')

        layout.addRow("Скорость u (x):", self.u_input)
        layout.addRow("Скорость v (y):", self.v_input)
        layout.addRow("Давление p:", self.p_input)
        if turb_type != TurbulenceModel.LAMINAR:
            layout.addRow("k (turb. energy):", self.k_input)
            layout.addRow("ω (spec. dissipation):", self.om_input)

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
            self.om_input.value(),
        )
