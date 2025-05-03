from enum import Enum
from dataclasses import dataclass


class TurbulenceModel(Enum):
    LAMINAR = "Laminar"
    SST = "k-omega SST"
    K_EPSILON = "k-epsilon"

@dataclass
class TurbulenceParams:
    model: TurbulenceModel = TurbulenceModel.LAMINAR
    # Общие параметры
    density: float = 1.225  # кг/м³
    viscosity: float = 1.8e-5  # Па·с
    # Параметры для SST/k-epsilon
    turbulent_intensity: float | None = 0.05  # 5%
    spec_length_scale: float | None = 0.01  # м

@dataclass
class BoundaryCondition:
    name: str
    bc_type: str  # "velocity", "pressure", "wall"
    values: dict  # {"velocity": (1,0), "turbulent_intensity": 0.05, ...}

@dataclass
class InitialCondition:
    velocity: tuple[float, float] = (0, 0)
    pressure: float = 101325  # Па
    turbulent_k: float = 0.001  # м²/с² (только для SST/k-epsilon)