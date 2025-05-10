import meshio

import numpy as np

from sfepy.base.base import IndexedStruct
from sfepy.discrete import FieldVariable
from sfepy.discrete import Material
from sfepy.discrete import Problem
from sfepy.discrete.common import Field
from sfepy.discrete.conditions import Conditions
from sfepy.discrete.conditions import EssentialBC
from sfepy.discrete.fem import FEDomain
from sfepy.discrete.fem import Mesh
from sfepy.discrete.integrals import Integral
from sfepy.solvers.ls import ScipyDirect
from sfepy.solvers.nls import Newton
from sfepy.terms import Term

def convert_mesh():
    # 1) читаем gmsh (.msh)
    msh = meshio.read('mesh.msh', file_format='gmsh')

    # 2) собираем в один массив все линии и их тэги
    all_lines = msh.cells_dict['line']  # shape (8,2)
    line_tags = np.concatenate(msh.cell_data['gmsh:physical'][:4])  # [1,1,2,2,3,3,2,2]

    # 3) берём треугольники и их тэги (должен быть именно один блок)
    tris = msh.cells_dict['triangle']  # shape (14,3)
    tri_tags = msh.cell_data['gmsh:physical'][-1]  # [1,1,1,…,1] длиной 14

    volume_mesh = meshio.Mesh(
        points=msh.points,
        cells=[('triangle', tris)],
        cell_data={'gmsh:physical': [tri_tags]}
    )

    boundary_mesh = meshio.Mesh(
        points=msh.points,
        cells=[('line', all_lines)],
        cell_data={'gmsh:physical': [line_tags]}
    )

    # Сохраняем в .xdmf
    meshio.write('volume.xdmf', volume_mesh)
    meshio.write('boundary.xdmf', boundary_mesh)

def solve(mesh: Mesh):
    domain = FEDomain('domain', mesh)

    # Определение регионов
    omega = domain.create_region('Omega', 'all')
    inlet = domain.create_region('Inlet', 'vertices of surface', 'facet')
    outlet = domain.create_region('Outlet', 'vertices of surface', 'facet')
    walls = domain.create_region('Walls', 'vertices of surface', 'facet')

    # Проверка регионов
    print("Available regions:", domain.regions)

    # Определение поля
    field = Field.from_args('temperature', np.float64, 'scalar', omega, approx_order=1)

    # Определение материала
    from sfepy.discrete import Material
    materials = {
        'mat': Material({'D': 1.0}),
    }

    # Определение уравнения
    from sfepy.terms import Term
    equations = {
        'Poisson': Term.new('dw_laplace(m.D, v, u)', integral=omega, m=materials['mat'], v=field, u=field),
    }

    # Граничные условия
    from sfepy.discrete.conditions import EssentialBC
    ebcs = {
        'inlet_temp': EssentialBC('Inlet', {'u.0': 10.0}),
        'outlet_temp': EssentialBC('Outlet', {'u.0': 0.0}),
    }

    # Настройка задачи
    problem = Problem('poisson')
    problem.setup(domain, fields=[field], materials=materials, equations=equations, ebcs=ebcs)

    # Решение
    state = problem.solve()

    # Сохранение результатов
    problem.save_state('poisson.vtk', state)


if __name__ == '__main__':
    # convert_mesh()
    mesh = Mesh.from_file('mesh.h5')

    solve(mesh)
