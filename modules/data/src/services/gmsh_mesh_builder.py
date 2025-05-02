import gmsh
from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainterPath


class GmshMeshBuilder:
    def __init__(self, grid_spacing: int = 1):
        self.grid_spacing = grid_spacing

        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 0)

    def __extract_polygon_loops(self, path: QPainterPath) -> list[list[QPointF]]:
        subpaths = path.toSubpathPolygons()
        max_h, max_w = 0, 0
        outer_i = 0
        for i in range(len(subpaths)):
            if (w := subpaths[i].boundingRect().width()) > max_w and (h := subpaths[i].boundingRect().height()) > max_h:
                max_w = w
                max_h = h

                outer_polygon = subpaths[i]
                outer_i = i

        outer_points = [QPointF(p.x() / self.grid_spacing, p.y() / self.grid_spacing) for p in outer_polygon][:-1]
        holes_points = [[QPointF(p.x() / self.grid_spacing, p.y() / self.grid_spacing) for p in subpaths[i]][:-1] for i in range(len(subpaths)) if i != outer_i]
        return [outer_points, *holes_points]

    @staticmethod
    def __add_loop(loop_points: list[QPointF], max_element_size: float):
        point_tags = [gmsh.model.geo.addPoint(p.x(), p.y(), 0, max_element_size) for p in loop_points]
        line_tags = []
        for i in range(len(point_tags)):
            a = point_tags[i]
            b = point_tags[(i + 1) % len(point_tags)]
            line_tags.append(gmsh.model.geo.addLine(a, b))
        return gmsh.model.geo.addCurveLoop(line_tags)

    def build_mesh(self, path: QPainterPath, max_element_size: float, filename: str = 'mesh.msh'):
        gmsh.model.add("geometry")

        loops = self.__extract_polygon_loops(path)

        outer_loop = loops[0]
        inner_loops = loops[1:] if len(loops) > 1 else []

        outer_tag = self.__add_loop(outer_loop, max_element_size)
        hole_tags = [self.__add_loop(hole, max_element_size) for hole in inner_loops]

        gmsh.model.geo.addPlaneSurface([outer_tag] + hole_tags)
        gmsh.model.geo.synchronize()
        gmsh.model.mesh.generate(2)

        gmsh.write(filename)
        gmsh.fltk.run()

    def __del__(self):
        gmsh.finalize()
