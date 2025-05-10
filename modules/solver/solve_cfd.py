# solve_cfd.py
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


# 1) Загрузка сетки
mesh = Mesh.from_file('mesh.xdmf')

domain = FEDomain('domain', mesh)

# 2) Объявляем регионы по меткам физических групп
omega = domain.create_region('Omega', 'all')
inlet = domain.create_region('Inlet', 'vertices of group 2', 'facet')  # тэг=2 for inlet
wall = domain.create_region('Wall', 'vertices of group 3', 'facet')  # тэг=3 for wall
outlet = domain.create_region('Outlet', 'vertices of group 4', 'facet')  # тэг=4 for outlet

# 3) Поля
field_u = Field('velocity', np.float64, 'vector', omega, approx_order=2)
field_p = Field('pressure', np.float64, 'scalar', omega, approx_order=1)

# 4) Переменные
u = FieldVariable('u', 'unknown', field_u, magnitude=[0.0, 0.0])
v = FieldVariable('v', 'test', field_u, primary_var_name='u')
p = FieldVariable('p', 'unknown', field_p)
q = FieldVariable('q', 'test', field_p, primary_var_name='p')

# 5) Материал и параметры
nu = 1.0e-3  # кинематическая вязкость
f = Material('f', val=[[0.0, 0.0]])  # нулевая правая часть
mu = Material('nu', val=nu)

# 6) Интеграл
integral = Integral('i', order=3)

# 7) Составляем вариационную форму
#   - viscous:  nu * ∇u : ∇v
#   - convective: (u·∇)u · v
#   - pressure   : - p ∇·v + q ∇·u
t1 = Term.new('dw_laplace(nu.val, v, u)', integral, omega, nu=mu, v=v, u=u)
t2 = Term.new('dw_convect(beta, v, u)', integral, omega,
              beta=FieldVariable('beta', 'parameter', field_u, val=[[1e-3, 0.0]]),
              v=v, u=u)
t3 = Term.new('dw_div(v, p)', integral, omega, v=v, p=p)
t4 = Term.new('dw_div(u, q)', integral, omega, u=u, q=q)

equations = {
    'NS': t1 + t2 + t3 + t4,
}

# 8) Граничные условия
#    Inlet: u = (1.0, 0.0)
bc_inlet = EssentialBC('u_inlet', inlet, {'u.all': [1.0, 0.0]})
#    Wall:  u = (0,0)
bc_wall = EssentialBC('u_wall', wall, {'u.all': [0.0, 0.0]})
#    Outlet: p = 0
bc_outlet = EssentialBC('p_outlet', outlet, {'p.0': 0.0})

bcs = Conditions([bc_inlet, bc_wall, bc_outlet])

# 9) Сборка и решение
problem = Problem('cfd', equations=equations, conf=IndexedStruct(bcs=bcs))
problem.set_bcs(bcs=bcs)
problem.set_solvers({
    'ls': ScipyDirect({}),
    'nls': Newton({'i_max': 10, 'eps_a': 1e-8}),
})
state = problem.solve()

if __name__ == '__main__':
    # 10) Сохраняем результаты
    problem.save_state('cfd_output.vtk', state)
