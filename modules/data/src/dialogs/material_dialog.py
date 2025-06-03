from PySide6 import QtWidgets
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QDoubleSpinBox
from PySide6.QtWidgets import QFormLayout
from src.dialogs.dialog import Dialog
from src.physics.turbulence_models import Material


class MaterialDialog(Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки материала")
        self.resize(300, 120)

        # Поля для ввода
        self.densityEdit = QDoubleSpinBox()
        self.viscosityEdit = QDoubleSpinBox()

        for w in [self.densityEdit, self.viscosityEdit]:
            w.setRange(-1e7, 1e7)

        self.densityEdit.setDecimals(4)
        self.viscosityEdit.setDecimals(6)

        self.densityEdit.setValue(1.204)
        self.viscosityEdit.setValue(1.8e-5)

        self.densityEdit.setSuffix(' кг/м³')
        self.viscosityEdit.setSuffix(' Па·с')

        # Форма
        form = QFormLayout()
        form.addRow("Плотность", self.densityEdit)
        form.addRow("Динамическая вязкость", self.viscosityEdit)

        # Кнопки ОК/Отмена
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        # Итоговый лэйаут
        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def get_data(self) -> Material:
        return Material(
            self.densityEdit.value(),
            self.viscosityEdit.value(),
        )
