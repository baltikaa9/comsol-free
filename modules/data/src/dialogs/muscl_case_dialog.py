from PySide6.QtWidgets import (
    QComboBox,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QSpinBox,
    QVBoxLayout,
)
from src.dialogs.dialog import Dialog
from src.services.muscl_case_exporter import MusclCase


class MusclCaseDialog(Dialog):
    """Collect solver-native settings; values are not inferred from CFD UI units."""

    def __init__(self, domain, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Параметры расчёта MUSCL")
        self.resize(480, 700)

        self.values = {}
        layout = QVBoxLayout(self)

        grid_form = QFormLayout()
        self.nx = self._int(2048, 16, 65536, 16)
        self.ny = self._int(1024, 16, 65536, 16)
        self.tmax = self._float(100.0, 1e-12, 1e12)
        self.dt_save = self._float(1.0, 1e-12, 1e12)
        self.courant = self._float(0.5, 1e-12, 1.0)
        self.gpu = self._int(0, 0, 1024)
        for label, widget in [
            ("Nx (кратно 16)", self.nx),
            ("Ny (кратно 16)", self.ny),
            ("Максимальное время", self.tmax),
            ("Интервал сохранения", self.dt_save),
            ("Число Куранта", self.courant),
            ("GPU id", self.gpu),
        ]:
            grid_form.addRow(label, widget)
        self.riemann = QComboBox()
        self.riemann.addItems(["LF", "HLL", "HLLC"])
        self.riemann.setCurrentIndex(2)
        self.limiter = QComboBox()
        self.limiter.addItems(["minmod", "van Leer", "van Albada"])
        self.limiter.setCurrentIndex(1)
        grid_form.addRow("Riemann solver", self.riemann)
        grid_form.addRow("Ограничитель наклона", self.limiter)
        self._group(layout, "Сетка и расчёт", grid_form)

        self.domain = domain
        domain_form = QFormLayout()
        domain_form.addRow(
            "Взята из внешнего прямоугольника геометрии",
            QLabel(
                f"[{domain['xmin']:g}, {domain['xmax']:g}] × "
                f"[{domain['ymin']:g}, {domain['ymax']:g}]"
            ),
        )
        self._group(layout, "Расчётная область", domain_form)

        state_form = QFormLayout()
        self.u0 = self._float(4.0, -1e12, 1e12)
        self.v0 = self._float(0.0, -1e12, 1e12)
        self.p0 = self._float(1.0, 1e-12, 1e12)
        self.temp0 = self._float(0.3, 1e-12, 1e12)
        self.tv0 = self._float(0.3, 1e-12, 1e12)
        self.y0 = self._float(0.0, 0.0, 1.0)
        self.gamma = self._float(1.4, 1.000001, 10.0)
        for label, widget in [
            ("u0 (MUSCL units)", self.u0),
            ("v0 (MUSCL units)", self.v0),
            ("P0 (MUSCL units)", self.p0),
            ("T0 (MUSCL units)", self.temp0),
            ("Tv0 (MUSCL units)", self.tv0),
            ("Y0", self.y0),
            ("gamma", self.gamma),
        ]:
            state_form.addRow(label, widget)
        self._group(layout, "Начальное состояние и газ", state_form)

        transport_form = QFormLayout()
        self.eta1 = self._float(0.25e-4, 0.0, 1e12)
        self.eta2 = self._float(0.25e-4, 0.0, 1e12)
        self.kappa = self._float(1.0e-4, 0.0, 1e12)
        self.kappa_v = self._float(0.0, 0.0, 1e12)
        self.beta = self._float(0.8, -10.0, 10.0)
        for label, widget in [
            ("eta0_1", self.eta1),
            ("eta0_2", self.eta2),
            ("kappa0", self.kappa),
            ("kappa0_v", self.kappa_v),
            ("beta_eta", self.beta),
        ]:
            transport_form.addRow(label, widget)
        self._group(layout, "Переносные коэффициенты MUSCL", transport_form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def _group(layout, title, form):
        box = QGroupBox(title)
        box.setLayout(form)
        layout.addWidget(box)

    @staticmethod
    def _float(value, minimum, maximum):
        widget = QDoubleSpinBox()
        widget.setDecimals(10)
        widget.setRange(minimum, maximum)
        widget.setValue(value)
        widget.setKeyboardTracking(False)
        return widget

    @staticmethod
    def _int(value, minimum, maximum, step=1):
        widget = QSpinBox()
        widget.setRange(minimum, maximum)
        widget.setSingleStep(step)
        widget.setValue(value)
        return widget

    def get_case(self) -> MusclCase:
        return MusclCase(
            nx=self.nx.value(),
            ny=self.ny.value(),
            t_max=self.tmax.value(),
            dt_save=self.dt_save.value(),
            courant=self.courant.value(),
            riemann_solver=self.riemann.currentIndex(),
            limiter=self.limiter.currentIndex(),
            xmin=self.domain["xmin"],
            xmax=self.domain["xmax"],
            ymin=self.domain["ymin"],
            ymax=self.domain["ymax"],
            u0=self.u0.value(),
            v0=self.v0.value(),
            pressure0=self.p0.value(),
            temperature0=self.temp0.value(),
            vibrational_temperature0=self.tv0.value(),
            mass_fraction0=self.y0.value(),
            gamma=self.gamma.value(),
            viscosity_1=self.eta1.value(),
            viscosity_2=self.eta2.value(),
            conductivity=self.kappa.value(),
            vibrational_conductivity=self.kappa_v.value(),
            viscosity_exponent=self.beta.value(),
            gpu_id=self.gpu.value(),
        )
