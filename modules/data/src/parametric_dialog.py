from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit,
                               QDialogButtonBox, QFormLayout, QSpinBox, QDoubleSpinBox)


class ParametricDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Параметрическая кривая")

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.expr_x = QLineEdit("1.8 * t - 1.8")
        self.expr_y = QLineEdit("1.8 * 0.594689181 * (0.298222773 * sqrt(t) - 0.127125232 * t - 0.357907906 * t**2 + 0.291984971 * t**3 - 0.105174696 * t**4)")
        self.t_min = QDoubleSpinBox()
        self.t_max = QDoubleSpinBox()
        self.samples = QSpinBox()

        self.t_min.setRange(-1e6, 1e6)
        self.t_max.setRange(-1e6, 1e6)
        self.samples.setRange(3, 10000)

        self.t_min.setValue(0)
        self.t_max.setValue(1)
        self.samples.setValue(100)

        form_layout.addRow("x(t):", self.expr_x)
        form_layout.addRow("y(t):", self.expr_y)
        form_layout.addRow("t min:", self.t_min)
        form_layout.addRow("t max:", self.t_max)
        form_layout.addRow("samples:", self.samples)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return {
            "x_expr": self.expr_x.text(),
            "y_expr": self.expr_y.text(),
            "t_min": self.t_min.value(),
            "t_max": self.t_max.value(),
            "samples": self.samples.value()
        }
