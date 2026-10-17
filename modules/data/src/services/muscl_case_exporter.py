"""Write input files for the unmodified MUSCL-2D-CUDA solver.

The solver reads positional INI files rather than structured_mesh.json.  This
module deliberately requires solver-native thermodynamic values: the current
editor's pressure is in Pa, while MUSCL's P/T are solver-scaled quantities.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


@dataclass(frozen=True)
class MusclSolid:
    """A MUSCL-supported solid. Coordinates are solver coordinates.

    ``kind`` is ``ellipse`` (center + semi-axes), ``rectangle`` (opposite
    corners), or ``right_triangle`` (two vertices, as expected by MUSCL).
    """

    kind: Literal["ellipse", "rectangle", "right_triangle"]
    points: tuple[tuple[float, float], tuple[float, float]]


@dataclass(frozen=True)
class MusclCase:
    """Complete solver-native configuration for one MUSCL run."""

    nx: int
    ny: int
    t_max: float
    dt_save: float
    courant: float
    riemann_solver: int
    limiter: int
    xmin: float
    xmax: float
    ymin: float
    ymax: float
    u0: float
    v0: float
    pressure0: float
    temperature0: float
    vibrational_temperature0: float
    mass_fraction0: float
    gamma: float
    viscosity_1: float
    viscosity_2: float
    conductivity: float
    vibrational_conductivity: float
    viscosity_exponent: float
    boundary_x_left: int = 0
    boundary_x_right: int = 0
    boundary_y_bottom: int = 0
    boundary_y_top: int = 0
    solids: tuple[MusclSolid, ...] = field(default_factory=tuple)
    start_mode: int = 0
    medium: int = 2
    save_interval: float = 1.0
    gpu_id: int = 0


class MusclCaseExporter:
    """Export a validated case in the exact positional format read by MUSCL."""

    FILES = (
        "__start.ini",
        "__subdomain.ini",
        "__boundary.ini",
        "__medium.ini",
        "__external_periodic_force.ini",
        "__relax.ini",
        "__smooth_perturb.ini",
        "__solid.ini",
        "__GPUs.ini",
    )

    @staticmethod
    def _validate(case: MusclCase) -> None:
        if case.nx <= 0 or case.ny <= 0:
            raise ValueError("Nx и Ny должны быть положительными")
        if case.nx % 16 or case.ny % 16:
            raise ValueError("Nx и Ny MUSCL должны быть кратны размеру CUDA-блока (16)")
        if not (case.xmin < case.xmax and case.ymin < case.ymax):
            raise ValueError(
                "Границы области должны задавать положительную ширину и высоту"
            )
        if case.gamma <= 1:
            raise ValueError("gamma должна быть больше 1")
        if case.temperature0 <= 0 or case.pressure0 <= 0:
            raise ValueError("Начальные P и T должны быть положительными")
        if case.t_max <= 0 or case.dt_save <= 0 or case.courant <= 0:
            raise ValueError("t_max, dt_save и Courant должны быть положительными")
        if case.riemann_solver not in (0, 1, 2):
            raise ValueError(
                "Решатель потоков должен быть 0 (LF), 1 (HLL) или 2 (HLLC)"
            )
        if case.limiter not in (0, 1, 2):
            raise ValueError(
                "Ограничитель должен быть 0 (minmod), 1 (van Leer) или 2 (van Albada)"
            )
        if any(
            code not in (0, 1, 2)
            for code in (
                case.boundary_x_left,
                case.boundary_x_right,
                case.boundary_y_bottom,
                case.boundary_y_top,
            )
        ):
            raise ValueError("Граничные коды MUSCL должны быть 0, 1 или 2")
        if not 0 <= case.gpu_id:
            raise ValueError("GPU id не может быть отрицательным")
        values = (
            case.t_max,
            case.dt_save,
            case.courant,
            case.xmin,
            case.xmax,
            case.ymin,
            case.ymax,
            case.u0,
            case.v0,
            case.pressure0,
            case.temperature0,
            case.vibrational_temperature0,
            case.mass_fraction0,
            case.gamma,
            case.viscosity_1,
            case.viscosity_2,
            case.conductivity,
            case.vibrational_conductivity,
            case.viscosity_exponent,
        )
        if not all(math.isfinite(value) for value in values):
            raise ValueError("Параметры MUSCL должны быть конечными числами")
        for solid in case.solids:
            if solid.kind not in ("ellipse", "rectangle", "right_triangle"):
                raise ValueError(f"Неподдерживаемая форма MUSCL: {solid.kind}")
            if len(solid.points) != 2 or any(
                len(point) != 2 or not all(math.isfinite(v) for v in point)
                for point in solid.points
            ):
                raise ValueError(
                    "Каждое препятствие должно иметь две конечные 2D-точки"
                )
            if solid.kind == "ellipse" and any(value == 0 for value in solid.points[1]):
                raise ValueError("Полуоси эллипса должны быть ненулевыми")
            if (
                solid.kind == "right_triangle"
                and solid.points[0][0] == solid.points[1][0]
            ):
                raise ValueError(
                    "У прямоугольного треугольника x-координаты вершин не должны совпадать"
                )

    @staticmethod
    def _line(value: object, description: str) -> str:
        return f"{value}\t--- {description}\n"

    @classmethod
    def export(cls, case: MusclCase, output_dir: str | Path) -> Path:
        """Write all configuration files and return their directory.

        This exports a rectangular, uniform MUSCL domain and optional native
        MUSCL solids. It does not claim that editor geometry has been mapped;
        callers must perform that conversion explicitly.
        """
        cls._validate(case)
        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)

        files: dict[str, str] = {}
        start = [
            (case.start_mode, "i_start"),
            (case.nx, "Nx"),
            (case.ny, "Ny"),
            (case.t_max, "t_max"),
            (case.dt_save, "dt_save"),
            (case.courant, "Courant"),
            (case.riemann_solver, "k_rs (0=LF, 1=HLL, 2=HLLC)"),
            (case.limiter, "k_lim (0=minmod, 1=vanLeer, 2=vanAlbada)"),
            (case.xmin, "rmin.x"),
            (case.xmax, "rmax.x"),
            (case.ymin, "rmin.y"),
            (case.ymax, "rmax.y"),
            (case.u0, "V0.x"),
            (case.v0, "V0.y"),
            (case.pressure0, "P0"),
            (case.temperature0, "T0"),
            (case.vibrational_temperature0, "Tv0"),
            (case.mass_fraction0, "Y0"),
        ]
        files["__start.ini"] = "".join(cls._line(v, label) for v, label in start)
        files["__subdomain.ini"] = "0\t--- n_sdm (number of subdomains)\n"
        files["__boundary.ini"] = "".join(
            cls._line(v, label)
            for v, label in [
                (case.boundary_x_left, "i_BC_xL"),
                (case.boundary_x_right, "i_BC_xR"),
                (case.boundary_y_bottom, "i_BC_yL"),
                (case.boundary_y_top, "i_BC_yR"),
                (0, "i_fluxT_xL"),
                (case.temperature0, "T_xL"),
                (1.0e3, "kappa_xL"),
                (0, "i_fluxT_xR"),
                (case.temperature0, "T_xR"),
                (1.0e3, "kappa_xR"),
                (0, "i_fluxT_yL"),
                (case.temperature0, "T_yL"),
                (1.0e3, "kappa_yL"),
                (0, "i_fluxT_yR"),
                (case.temperature0, "T_yR"),
                (1.0e3, "kappa_yR"),
            ]
        )
        # MUSCL reads each value on a separate fscanf line, including the
        # relaxation species entries. Defaults disable chemistry and forcing.
        medium = [
            (case.medium, "i_medium"),
            (0.0, "S0"),
            (case.gamma, "gamma0"),
            (case.viscosity_1, "eta0_1"),
            (case.viscosity_2, "eta0_2"),
            (case.conductivity, "kappa0"),
            (case.vibrational_conductivity, "kappa0_v"),
            (case.viscosity_exponent, "beta_eta"),
            (0.0, "Q_R0"),
            (0.0, "Q_T0"),
            (0.0, "I_R0"),
            (0.0, "I_T0"),
            (0.3, "Tex"),
            (case.xmin, "x1_sm"),
            (case.xmax, "x2_sm"),
            (1.0, "dx_sm"),
            (case.ymin, "y1_sm"),
            (case.ymax, "y2_sm"),
            (1.0, "dy_sm"),
            (0.0, "t1_sm"),
            (1000.0, "tau0_a"),
            (10.0, "Ta"),
            (0.0, "Ha"),
            (0.0, "tau_min"),
            (1.0, "del_a"),
            (0.0, "I0"),
        ]
        files["__medium.ini"] = "".join(cls._line(v, label) for v, label in medium)
        files["__external_periodic_force.ini"] = "".join(
            cls._line(v, label)
            for v, label in [
                (0, "i_force"),
                (0.0, "omega_s"),
                (0.0, "af_s.x"),
                (0.0, "af_s.y"),
                (0.0, "af_s.z"),
                (case.xmin, "xmin_s"),
                (case.xmax, "xmax_s"),
                (1.0, "dx_s"),
                (case.ymin, "ymin_s"),
                (case.ymax, "ymax_s"),
                (1.0, "dy_s"),
                (1, "m_sprl"),
            ]
        )
        files["__relax.ini"] = (
            "".join(
                cls._line(v, label)
                for v, label in [
                    (10.0, "atau1"),
                    (0.0, "atau2"),
                    (0.0, "atau3"),
                    (0.0, "ntau"),
                    (0, "mtau"),
                    (1, "Nv"),
                ]
            )
            + "1 6.0\t--- r_v1 theta_v1\n"
        )
        files["__smooth_perturb.ini"] = (
            "0\t--- it_smooth\n4\t--- ir_smooth\n0\t--- n_prt\n"
        )
        solids = [("ellipse", 0), ("rectangle", 1), ("right_triangle", 2)]
        type_by_kind = dict(solids)
        solid_lines = [
            cls._line(len(case.solids), "n_sld"),
            cls._line(0.0, "kappa_sld"),
            cls._line(case.temperature0, "T_sld"),
            cls._line(1, "kRS_sld"),
        ]
        for index, solid in enumerate(case.solids, start=1):
            solid_lines.extend(
                [
                    cls._line(index, "k_sld"),
                    f"{type_by_kind[solid.kind]} 0\t--- shape type, solid\n",
                    cls._line(2, "mpar_sld"),
                ]
            )
            for x, y in solid.points:
                solid_lines.append(f"{x:.17g} {y:.17g}\t--- geometry parameter\n")
        files["__solid.ini"] = "".join(solid_lines)
        files["__GPUs.ini"] = cls._line(case.gpu_id, "deviceId GPU")

        for filename, content in files.items():
            (destination / filename).write_text(content, encoding="ascii")
        return destination
