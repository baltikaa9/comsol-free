import h5py
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
    m = meshio.read("mesh.msh", file_format="gmsh")
    meshio.write("mesh.h5", m)

    # --- объём: только треугольники ---
    # tri_cells = [(c.type, c.data) for c in m.cells if c.type == "triangle"]
    # tri_phys = [pd for ctype, pd in zip([c.type for c in m.cells],
    #                                     m.cell_data["gmsh:physical"])
    #             if ctype == "triangle"]
    #
    # meshio.write("mesh_vol.xdmf",
    #              meshio.Mesh(points=m.points,
    #                          cells=tri_cells,
    #                          cell_data={"gmsh:physical": tri_phys}),
    #              file_format="xdmf")
    #
    # # --- границы: только линии ---
    # line_cells = [(c.type, c.data) for c in m.cells if c.type == "line"]
    # line_phys = [pd for ctype, pd in zip([c.type for c in m.cells],
    #                                      m.cell_data["gmsh:physical"])
    #              if ctype == "line"]
    #
    # meshio.write("mesh_bnd.xdmf",
    #              meshio.Mesh(points=m.points,
    #                          cells=line_cells,
    #                          cell_data={"gmsh:physical": line_phys}),
    #              file_format="xdmf")


def solve(mesh: Mesh):
    domain = FEDomain('domain', mesh)

    # Определение регионов
    omega = domain.create_region('Omega', 'all')
    inlet = domain.create_region('Inlet', 'vertices in (x > 1.9)', 'facet')
    outlet = domain.create_region('Outlet', 'cells of group 1', 'facet')
    walls = domain.create_region('Walls', 'cells of group 2', 'facet')

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
    mesh = Mesh.from_file('mesh_matid_1.h5')

    # mesh = Mesh.from_file("test/circle_in_square.h5")

    print(mesh.cmesh.cell_groups)
    # facet_groups = mesh.get_facet_groups()
    # print(facet_groups)
    # m = meshio.read('mesh.mesh', file_format='gmsh')

    c=1

    # with h5py.File('mesh.h5', 'r') as f:
    #     print(list(f.keys()))  # Показывает разделы, например: ['cells', 'cell_sets', 'facets', 'facet_sets']
    #     print(f['cell_sets'].keys())  # Показывает группы для объемных элементов
    #     print(f['facet_sets'].keys())  # Показывает группы для граней

    solve(mesh)
