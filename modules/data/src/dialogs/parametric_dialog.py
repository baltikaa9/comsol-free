from PySide6.QtWidgets import QFormLayout, QLineEdit, QDialogButtonBox, QDialog


class ParametricDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Draw Parametric Curve')
        layout = QFormLayout()

        self.x_expr = QLineEdit('1.8 * t - 1.8')
        self.y_expr = QLineEdit('1.8 * 0.594689181 * (0.298222773 * sqrt(t) - 0.127125232 * t - 0.357907906 * t**2 + 0.291984971 * t**3 - 0.105174696 * t**4)')
        self.t_min = QLineEdit('0')
        self.t_max = QLineEdit('1')
        self.samples = QLineEdit('100')

        layout.addRow('X(t):', self.x_expr)
        layout.addRow('Y(t):', self.y_expr)
        layout.addRow('t Min:', self.t_min)
        layout.addRow('t Max:', self.t_max)
        layout.addRow('Samples:', self.samples)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_data(self):
        try:
            return {
                'x_expr': self.x_expr.text(),
                'y_expr': self.y_expr.text(),
                't_min': float(self.t_min.text()),
                't_max': float(self.t_max.text()),
                'samples': int(self.samples.text())
            }
        except ValueError:
            return None