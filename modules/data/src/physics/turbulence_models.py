from dataclasses import dataclass
from enum import Enum


class TurbulenceModel(Enum):
    LAMINAR = 'Laminar'
    SST = 'SST'
    K_EPSILON = 'k-epsilon'

class BoundaryConditionType(Enum):
    INLET = 'inlet'
    WALL = 'wall'
    OPEN = 'open boundary'

class WallType(Enum):
    SLIP = 'slip'
    NO_SLIP = 'no slip'

@dataclass
class TurbulenceParams:
    model: TurbulenceModel = TurbulenceModel.LAMINAR

@dataclass
class BoundaryConditions:   # TODO: сделать норм условия для wall и тд
    type: BoundaryConditionType

@dataclass
class InletBoundaryConditions(BoundaryConditions):
    type: BoundaryConditionType = BoundaryConditionType.INLET
    u: float = 0
    v: float = 0
    k: float | None = 4.184e-7  # м²/с² (только для SST/k-epsilon)
    omega: float | None = 2.78

@dataclass
class OpenBoundaryConditions(BoundaryConditions):
    type: BoundaryConditionType = BoundaryConditionType.OPEN
    k: float | None = 4.184e-7  # м²/с² (только для SST/k-epsilon)
    omega: float | None = 2.78

@dataclass
class WallBoundaryConditions(BoundaryConditions):
    type: BoundaryConditionType = BoundaryConditionType.WALL
    wall: WallType = WallType.NO_SLIP

@dataclass
class InitialConditions:
    u: float = 0
    v: float = 0
    p: float = 0   # Па
    k: float | None = 4.184e-7   # м²/с² (только для SST/k-epsilon)
    omega: float | None = 2.78

@dataclass
class Material:
    rho: float = 1.204
    mu: float = 1.81397e-5
