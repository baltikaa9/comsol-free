from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QDoubleSpinBox
from PySide6.QtWidgets import QFormLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from modules.data.src.dialogs.dialog import Dialog
from modules.data.src.physics.turbulence_models import BoundaryConditionType
from modules.data.src.physics.turbulence_models import BoundaryConditions
from modules.data.src.physics.turbulence_models import InletBoundaryConditions
from modules.data.src.physics.turbulence_models import OpenBoundaryConditions
from modules.data.src.physics.turbulence_models import TurbulenceModel
from modules.data.src.physics.turbulence_models import WallBoundaryConditions
from modules.data.src.physics.turbulence_models import WallType
from modules.data.src.widgets.edge_item import EdgeItem


class BoundaryConditionsDialog(Dialog):
    def __init__(self, edges: list[EdgeItem], turb_type: TurbulenceModel):
        super().__init__()

        self.turb_type = turb_type

        self.setWindowTitle(f'Граничное условие для ребер {[edge.id for edge in edges]}')
        layout = QVBoxLayout()

        self.type_combo = QComboBox()
        for condition in BoundaryConditionType:
            self.type_combo.addItem(condition.value, condition)

        self.type_combo.currentIndexChanged.connect(self.on_type_change)

        layout.addWidget(QLabel("Тип граничного условия:"))
        layout.addWidget(self.type_combo)

        # --- Общие поля для inlet и open ---
        self.u_input = QDoubleSpinBox()
        self.v_input = QDoubleSpinBox()
        self.k_input = QDoubleSpinBox()
        self.om_input = QDoubleSpinBox()
        for w in (self.u_input, self.v_input, self.k_input, self.om_input):
            w.setRange(-1e6, 1e6)

        self.u_input.setValue(50)
        self.v_input.setValue(0)
        self.k_input.setDecimals(8)
        self.k_input.setValue(4.184e-7)
        self.om_input.setValue(2.78)

        self.inputs_form = QFormLayout()
        self.inputs_form.addRow("u:", self.u_input)
        self.inputs_form.addRow("v:", self.v_input)
        if turb_type != TurbulenceModel.LAMINAR:
            self.inputs_form.addRow("k:", self.k_input)
            self.inputs_form.addRow("ω:", self.om_input)
        layout.addLayout(self.inputs_form)

        # --- Поля для стенки ---
        self.wall_type_combo = QComboBox()
        for wt in WallType:
            self.wall_type_combo.addItem(wt.value, wt)
        self.wall_widget = QWidget()
        self.wall_widget.setVisible(False)
        wall_layout = QFormLayout(self.wall_widget)
        wall_layout.addRow("Тип стенки:", self.wall_type_combo)
        layout.addWidget(self.wall_widget)

        # --- Кнопки ---
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Инициализация вида в зависимости от первого элемента
        self.setLayout(layout)
        self.on_type_change(self.type_combo.currentIndex())

    def on_type_change(self, index: int):
        """В зависимости от выбранного типа показываем нужные поля."""
        t = self.type_combo.itemData(index)
        is_inlet = (t == BoundaryConditionType.INLET)
        is_open  = (t == BoundaryConditionType.OPEN)
        is_wall  = (t == BoundaryConditionType.WALL)

        # Параметры u, v нужны только для INLET
        self.inputs_form.labelForField(self.u_input).setVisible(is_inlet)
        self.u_input.setVisible(is_inlet)
        self.inputs_form.labelForField(self.v_input).setVisible(is_inlet)
        self.v_input.setVisible(is_inlet)

        if self.turb_type != TurbulenceModel.LAMINAR:
            # Параметры k, omega нужны для INLET и OPEN
            for widget in (self.k_input, self.om_input):
                lbl = self.inputs_form.labelForField(widget)
                lbl.setVisible(is_inlet or is_open)
                widget.setVisible(is_inlet or is_open)

        # Поле wall_widget — только для WALL
        self.wall_widget.setVisible(is_wall)

    def get_data(self) -> BoundaryConditions:
        """Возвращает конкретный объект условий."""
        t = self.type_combo.currentData()
        if t == BoundaryConditionType.INLET:
            return InletBoundaryConditions(
                u=self.u_input.value(),
                v=self.v_input.value(),
                k=self.k_input.value() if self.turb_type != TurbulenceModel.LAMINAR else None,
                omega=self.om_input.value() if self.turb_type != TurbulenceModel.LAMINAR else None,
            )
        elif t == BoundaryConditionType.OPEN:
            return OpenBoundaryConditions(
                k=self.k_input.value() if self.turb_type != TurbulenceModel.LAMINAR else None,
                omega=self.om_input.value() if self.turb_type != TurbulenceModel.LAMINAR else None,
            )
        else:  # WALL
            return WallBoundaryConditions(
                wall=self.wall_type_combo.currentData()
            )
