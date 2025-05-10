import gmsh
from PySide6.QtCore import QPointF

from modules.data.src.physics.turbulence_models import BoundaryConditions
from modules.data.src.widgets.edge_item import EdgeItem


class GmshMeshBuilder:
    def __init__(self, grid_spacing: int = 1, filename: str = 'mesh.msh'):
        self.grid_spacing = grid_spacing
        self.filename = filename
        self.__boundary_lines: dict[str, list[int]] = {}
        self.boundary_conditions: dict[int, BoundaryConditions] = {}

        gmsh.initialize()
        gmsh.model.add("geometry")
        gmsh.option.setNumber("Mesh.MshFileVersion", 2)

    def add_loop(self, loop: list[EdgeItem], max_element_size: float):
        p1 = loop[0].p1
        points = [gmsh.model.geo.addPoint(p1.x() / self.grid_spacing, p1.y() / self.grid_spacing, 0, max_element_size)]

        lines_groups = {}
        for edge in loop:
            poly = edge.path().toFillPolygon()
            for p in list(poly)[1:-1]:
                points.append(gmsh.model.geo.addPoint(p.x() / self.grid_spacing, p.y() / self.grid_spacing, 0, max_element_size))

            for i in range(len(points) - 1):
                a = points[i]
                b = points[i + 1]
                if not lines_groups.get(edge.boundary_conditions.type):
                    lines_groups[edge.boundary_conditions.type] = []
                lines_groups[edge.boundary_conditions.type].append(gmsh.model.geo.addLine(a, b))

            points = points[-1:]

        gmsh.model.geo.synchronize()
        for type, lines in lines_groups.items():
            phys_tag = gmsh.model.addPhysicalGroup(1, lines, name=type.value)
            for edge in loop:
                if edge.boundary_conditions.type == type:
                    self.boundary_conditions[phys_tag] = edge.boundary_conditions
                    break

        gmsh.model.geo.removeAllDuplicates()
        return gmsh.model.geo.addCurveLoop([line for lines in lines_groups.values() for line in lines])

    def build_closed_loops(self, edges: list[EdgeItem]) -> list[list[EdgeItem]]:
        """
        Вернёт список замкнутых циклов (каждый — список EdgeItem в порядке обхода).
        Если какая-то цепочка не закрылась (открытая), она в результат не попадёт.
        """
        unused = set(edges)
        loops = []

        while unused:
            current = unused.pop()
            loop = [current]

            # растём вперёд
            while True:
                end_pt = loop[-1].p2

                # ищем неиспользованное ребро, у которого начало совпадает с end_pt
                candidate = None
                for e in list(unused):
                    if self.equal_points(e.p1, end_pt):
                        candidate = e
                        break
                    # если совпадает его p2 — можем перевернуть
                    if self.equal_points(e.p2, end_pt):
                        e.reverse()
                        candidate = e
                        break

                if not candidate:
                    # дальше не «цепляется»
                    break

                unused.remove(candidate)
                loop.append(candidate)

                # если мы вернулись к стартовой точке — закончили цикл
                if self.equal_points(loop[0].p1, loop[-1].p2):
                    loops.append(loop)
                    break
            # если цикл не замкнулся, мы его просто отбрасываем
        return loops

    def equal_points(self, a: QPointF, b: QPointF, tol=1e-3) -> bool:
        return (a - b).manhattanLength() < tol

    def build_mesh(self, edges: list[EdgeItem], max_element_size: float):
        loops: list[list[EdgeItem]] = self.build_closed_loops(edges)

        loops_tags = []
        for loop in loops:
            loops_tags.append(self.add_loop(loop, max_element_size))

        surface = gmsh.model.geo.addPlaneSurface(loops_tags)

        gmsh.model.addPhysicalGroup(dim=2, tags=[surface], tag=1, name='Domain')

        gmsh.model.geo.synchronize()
        gmsh.model.mesh.generate(2)

    def __del__(self):
        gmsh.write(self.filename)
        gmsh.fltk.run()
        gmsh.finalize()
