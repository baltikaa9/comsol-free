import math
from collections import defaultdict
from typing import Iterable

import gmsh
import networkx as nx
from PySide6.QtCore import QLineF
from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainterPath

from modules.data.src.physics.turbulence_models import BoundaryConditions
from modules.data.src.widgets.edge_item import EdgeItem


class GmshMeshBuilder:
    def __init__(self, grid_spacing: int = 1):
        self.grid_spacing = grid_spacing
        self.__boundary_lines: dict[str, list[int]] = {}

    def add_loop(self, loop: list[EdgeItem], max_element_size: float):
        lines = []

        p1 = loop[0].p1
        points = [gmsh.model.geo.addPoint(p1.x() / self.grid_spacing, p1.y() / self.grid_spacing, 0, max_element_size)]

        for edge in loop:

            poly = edge.path().toFillPolygon()
            for p in list(poly)[1:-1]:
                points.append(gmsh.model.geo.addPoint(p.x() / self.grid_spacing, p.y() / self.grid_spacing, 0, max_element_size))

            for i in range(len(points) - 1):
                a = points[i]
                b = points[i + 1]
                lines.append(gmsh.model.geo.addLine(a, b))

            points = points[-1:]

        gmsh.model.geo.removeAllDuplicates()
        return gmsh.model.geo.addCurveLoop(lines)

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

    def build_mesh(self, edges: list[EdgeItem], max_element_size: float, filename: str = 'mesh.msh'):
        gmsh.initialize()
        gmsh.model.add("geometry")

        loops: list[list[EdgeItem]] = self.build_closed_loops(edges)

        loops_tags = []
        for loop in loops:
            loops_tags.append(self.add_loop(loop, max_element_size))

        surface_tag = gmsh.model.geo.addPlaneSurface(loops_tags)

        gmsh.model.geo.synchronize()
        gmsh.model.mesh.generate(2)
        gmsh.write(filename)
        gmsh.fltk.run()
        gmsh.finalize()
