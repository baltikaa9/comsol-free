from enum import Enum
from dataclasses import dataclass

from modules.data.src.widgets.edge_item import EdgeItem


class TurbulenceModel(Enum):
    LAMINAR = 'Laminar'
    SST = 'SST'
    K_EPSILON = 'k-epsilon'

class BoundaryConditionType(Enum):
    INLET = 'inlet'
    OUTLET = 'outlet'
    WALL = 'wall'
    OPEN = 'open boundary'

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
class BoundaryConditions:   # TODO: сделать норм условия для wall и тд
    edges: list[EdgeItem]
    type: BoundaryConditionType = BoundaryConditionType.INLET
    u: float = 0
    v: float = 0
    k: float = 0.001  # м²/с² (только для SST/k-epsilon)
    omega: float = 0

@dataclass
class InitialConditions:
    u: float = 0
    v: float = 0
    p: float = 101325   # Па
    k: float = 0.001    # м²/с² (только для SST/k-epsilon)
    omega: float = 0
