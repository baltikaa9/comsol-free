from PySide6.QtWidgets import (
    QComboBox,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QWidget,
)
from src.dialogs.dialog import Dialog


class MeshDialog(Dialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setWindowTitle('Параметры сетки')

        # Выбор типа сетки
        self.mesh_type_combo = QComboBox()
        self.mesh_type_combo.addItems(['Треугольная (GMSH)', 'Прямоугольная (структурированная)'])
        self.mesh_type_combo.setCurrentIndex(1)

        self.dx_spin = QDoubleSpinBox()
        self.dx_spin.setDecimals(2)
        self.dx_spin.setRange(0.01, 100.0)
        self.dx_spin.setValue(10)
        self.dx_spin.setSingleStep(0.01)

        # Чекбокс визуализации
        # self.visualize_checkbox = QCheckBox()
        # self.visualize_checkbox.setChecked(False)

        layout = QFormLayout(self)
        layout.addRow('Тип сетки', self.mesh_type_combo)
        layout.addRow('Максимальный размер элемента', self.dx_spin)
        # layout.addRow('Показать визуализацию (может лагать)', self.visualize_checkbox)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        box = QDialogButtonBox(buttons)
        box.accepted.connect(self.accept)
        box.rejected.connect(self.reject)
        layout.addWidget(box)

    def get_data(self) -> float:
        return self.dx_spin.value()

    def get_mesh_type(self) -> str:
        """Возвращает 'triangular' или 'structured'"""
        return 'triangular' if self.mesh_type_combo.currentIndex() == 0 else 'structured'

    # def get_visualize(self) -> bool:
    #     """Возвращает True если нужно показать визуализацию"""
    #     return self.visualize_checkbox.isChecked()
