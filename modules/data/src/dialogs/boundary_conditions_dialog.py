from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QDoubleSpinBox
from PySide6.QtWidgets import QFormLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QVBoxLayout

from modules.data.src.dialogs.dialog import Dialog
from modules.data.src.physics.turbulence_models import BoundaryConditionType
from modules.data.src.physics.turbulence_models import BoundaryConditions
from modules.data.src.widgets.edge_item import EdgeItem


class BoundaryConditionsDialog(Dialog):
    def __init__(self, edges: list[EdgeItem]):
        super().__init__()
        self.setWindowTitle(f'Граничное условие для ребер {[edge.id for edge in edges]}')
        layout = QVBoxLayout()

        self.type_combo = QComboBox()
        for condition in BoundaryConditionType:
            self.type_combo.addItem(condition.value, condition)
        self.type_combo.currentIndexChanged.connect(self.on_type_change)
        layout.addWidget(QLabel("Тип граничного условия:"))
        layout.addWidget(self.type_combo)

        # Поля значений для inlet
        self.u_input = QDoubleSpinBox()
        self.v_input = QDoubleSpinBox()
        self.k_input = QDoubleSpinBox()
        self.omega_input = QDoubleSpinBox()

        for w in [self.u_input, self.v_input, self.k_input, self.omega_input]:
            w.setRange(-1e3, 1e3)

        self.inputs_layout = QFormLayout()
        self.inputs_layout.addRow("u:", self.u_input)
        self.inputs_layout.addRow("v:", self.v_input)
        self.inputs_layout.addRow("k:", self.k_input)
        self.inputs_layout.addRow("ω:", self.omega_input)

        layout.addLayout(self.inputs_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)
        self.on_type_change(0)

    def on_type_change(self, index: int):
        condition_type = self.type_combo.itemData(index)
        enabled = condition_type == BoundaryConditionType.INLET
        for i in range(self.inputs_layout.count()):
            item = self.inputs_layout.itemAt(i).widget()
            if item:
                item.setEnabled(enabled)

    def get_data(self) -> BoundaryConditions:
        return BoundaryConditions(
            self.type_combo.currentData(),
            self.u_input.value(),
            self.v_input.value(),
            self.k_input.value(),
            self.omega_input.value(),
        )
