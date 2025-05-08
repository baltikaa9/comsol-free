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

    def __add_loop(self, loop_name: str, loop_points: list[QPointF], max_element_size: float):
        point_tags = [gmsh.model.geo.addPoint(p.x(), p.y(), 0, max_element_size) for p in loop_points]
        line_tags = []
        for i in range(len(point_tags)):
            a = point_tags[i]
            b = point_tags[(i + 1) % len(point_tags)]
            line_tags.append(gmsh.model.geo.addLine(a, b))

        self.__boundary_lines[loop_name] = line_tags
        return gmsh.model.geo.addCurveLoop(line_tags)

    def add_loop(self, loop: list[EdgeItem], max_element_size: float):
        lines = []

        p1 = loop[0].p1
        curr = 0

        points = [gmsh.model.geo.addPoint(p1.x() / self.grid_spacing, p1.y() / self.grid_spacing, 0, max_element_size)]

        for edge in loop:
            poly = edge.path().toFillPolygon()
            for p in list(poly)[1:-1]:
                points.append(gmsh.model.geo.addPoint(p.x() / self.grid_spacing, p.y() / self.grid_spacing, 0, max_element_size))

        for i in range(len(points) - 1):
            a = points[i]
            b = points[(i + 1) % (len(points) - 1)]
            lines.append(gmsh.model.geo.addLine(a, b))
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

    def build_mesh_2(self, edges: list[EdgeItem], max_element_size: float, filename: str = 'mesh.msh'):
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

    def build_mesh(self, boundary_conditions: list[BoundaryConditions], max_element_size: float, filename: str = 'mesh.msh'):
        # Инициализация Gmsh
        gmsh.initialize()
        gmsh.model.add("geometry")

        # Собираем все уникальные рёбра
        all_edges = []
        for bc in boundary_conditions:
            for edge in bc.edges:
                if edge not in all_edges:
                    all_edges.append(edge)

        # Создание кривых в Gmsh
        def create_gmsh_curve(edge, point_dict):
            if isinstance(edge, EdgeItem):
                p1 = edge.line().p1()
                p2 = edge.line().p2()
                tuple_p1 = (p1.x() / self.grid_spacing, p1.y() / self.grid_spacing)
                tuple_p2 = (p2.x() / self.grid_spacing, p2.y() / self.grid_spacing)
                if tuple_p1 not in point_dict:
                    point_tag1 = gmsh.model.geo.addPoint(tuple_p1[0], tuple_p1[1], 0, max_element_size)
                    point_dict[tuple_p1] = point_tag1
                else:
                    point_tag1 = point_dict[tuple_p1]
                if tuple_p2 not in point_dict:
                    point_tag2 = gmsh.model.geo.addPoint(tuple_p2[0], tuple_p2[1], 0, max_element_size)
                    point_dict[tuple_p2] = point_tag2
                else:
                    point_tag2 = point_dict[tuple_p2]
                curve_tag = gmsh.model.geo.addLine(point_tag1, point_tag2)
                return curve_tag, (point_tag1, point_tag2)
            elif isinstance(edge, ArcEdgeItem):
                rect = edge.rect
                start_angle = edge.start_angle
                arc_len = edge.arc_len
                center_x = (rect.left() + rect.right()) / 2 / self.grid_spacing
                center_y = (rect.top() + rect.bottom()) / 2 / self.grid_spacing
                width = rect.width() / self.grid_spacing
                height = rect.height() / self.grid_spacing
                theta_start = -start_angle
                theta_end = theta_start - arc_len
                x_start = center_x + (width / 2) * math.cos(math.radians(theta_start))
                y_start = center_y + (height / 2) * math.sin(math.radians(theta_start))
                x_end = center_x + (width / 2) * math.cos(math.radians(theta_end))
                y_end = center_y + (height / 2) * math.sin(math.radians(theta_end))
                if width > height:
                    major_x = center_x + width / 2
                    major_y = center_y
                elif height > width:
                    major_x = center_x
                    major_y = center_y + height / 2
                else:
                    major_x = center_x + width / 2
                    major_y = center_y
                center_tuple = (center_x, center_y)
                start_tuple = (x_start, y_start)
                major_tuple = (major_x, major_y)
                end_tuple = (x_end, y_end)
                if center_tuple not in point_dict:
                    center_tag = gmsh.model.geo.addPoint(center_x, center_y, 0, max_element_size)
                    point_dict[center_tuple] = center_tag
                else:
                    center_tag = point_dict[center_tuple]
                if start_tuple not in point_dict:
                    start_tag = gmsh.model.geo.addPoint(x_start, y_start, 0, max_element_size)
                    point_dict[start_tuple] = start_tag
                else:
                    start_tag = point_dict[start_tuple]
                if major_tuple not in point_dict:
                    major_tag = gmsh.model.geo.addPoint(major_x, major_y, 0, max_element_size)
                    point_dict[major_tuple] = major_tag
                else:
                    major_tag = point_dict[major_tuple]
                if end_tuple not in point_dict:
                    end_tag = gmsh.model.geo.addPoint(x_end, y_end, 0, max_element_size)
                    point_dict[end_tuple] = end_tag
                else:
                    end_tag = point_dict[end_tuple]
                curve_tag = gmsh.model.geo.addEllipseArc(start_tag, center_tag, major_tag, end_tag)
                return curve_tag, (start_tag, end_tag)
            elif isinstance(edge, EdgeItem):
                path = edge.path()
                num_samples = 10
                points = []
                for i in range(num_samples + 1):
                    t = i / num_samples
                    point = path.pointAtPercent(t)
                    points.append((point.x() / self.grid_spacing, point.y() / self.grid_spacing))
                point_tags = []
                for p in points:
                    if p not in point_dict:
                        point_tag = gmsh.model.geo.addPoint(p[0], p[1], 0, max_element_size)
                        point_dict[p] = point_tag
                    else:
                        point_tag = point_dict[p]
                    point_tags.append(point_tag)
                curve_tag = gmsh.model.geo.addSpline(point_tags)
                return curve_tag, (point_tags[0], point_tags[-1])
            else:
                raise ValueError("Неизвестный тип грани")

        # Словарь для точек
        point_dict = {}

        # Создание кривых и маппинг
        edge_to_curve = {}
        curve_to_points = {}
        for edge in all_edges:
            curve_tag, (start_point, end_point) = create_gmsh_curve(edge, point_dict)
            edge_to_curve[edge] = curve_tag
            curve_to_points[curve_tag] = (start_point, end_point)

        # Построение графа для поиска замкнутых контуров
        G = nx.DiGraph()
        for curve_tag, (start, end) in curve_to_points.items():
            G.add_edge(start, end, curve=curve_tag)

        # Поиск всех замкнутых циклов
        cycles = list(nx.simple_cycles(G))

        # Создание CurveLoop для каждого цикла
        loop_tags = []
        for cycle in cycles:
            curve_tags = []
            for i in range(len(cycle)):
                start = cycle[i]
                end = cycle[(i + 1) % len(cycle)]
                curve_tag = G[start][end]["curve"]
                curve_tags.append(curve_tag)
            try:
                loop_tag = gmsh.model.geo.addCurveLoop(curve_tags)
                loop_tags.append(loop_tag)
            except Exception as e:
                print(f"Ошибка при создании CurveLoop: {e}")
                continue

        # Создание поверхностей
        surface_tags = []
        if loop_tags:
            # Предполагаем, что первый контур — внешний, остальные — отверстия
            surface_tag = gmsh.model.geo.addPlaneSurface([loop_tags[0]] + [-loop_tag for loop_tag in loop_tags[1:]])
            surface_tags.append(surface_tag)
            gmsh.model.addPhysicalGroup(2, [surface_tag], name="fluid_domain")

        # Привязка граничных условий
        boundary_groups = defaultdict(list)
        for bc in boundary_conditions:
            for edge in bc.edges:
                if edge in edge_to_curve:
                    boundary_groups[bc.type.value].append(edge_to_curve[edge])

        for group_name, curve_tags in boundary_groups.items():
            if curve_tags:
                gmsh.model.addPhysicalGroup(1, curve_tags, name=f"Boundary_{group_name}")

        # Синхронизация геометрии
        gmsh.model.geo.synchronize()

        # Генерация двумерной сетки
        try:
            gmsh.model.mesh.generate(2)
        except Exception as e:
            print(f"Ошибка при генерации сетки: {e}")

        # Сохранение сетки
        try:
            gmsh.write(filename)
        except Exception as e:
            print(f"Ошибка при сохранении сетки: {e}")

        # Отображение результата (опционально)
        gmsh.fltk.run()

        # Завершение
        gmsh.finalize()

    @staticmethod
    def find_cycles(lines: Iterable[QLineF]):
        G = nx.DiGraph()
        for line in lines:
            start, end = line.p1(), line.p2()
            G.add_edge((start.x(), start.y()), (end.x(), end.y()))
        return list(nx.simple_cycles(G))

    def find_closed_contours(self, lines: Iterable[tuple[tuple[float, float], tuple[float, float]]]):
        graph = defaultdict(list)
        for (p1, p2) in lines:
            graph[p1].append(p2)

        visited_points = set()
        visited_lines = set()
        contours = []

        def dfs(current_point, start_point, path):
            if current_point == start_point and len(path) >= 3:
                contours.append(list(path))
                return

            if current_point in visited_points:
                return

            visited_points.add(current_point)
            for next_point in graph[current_point]:
                line = (current_point, next_point)
                if line in visited_lines:
                    continue

                visited_lines.add(line)
                path.append(line)
                dfs(next_point, start_point, path)
                path.pop()
                visited_lines.remove(line)
            visited_points.remove(current_point)

        points = list(graph.keys())
        for point in points:
            if point not in visited_points:
                dfs(point, point, [])

        return contours[::4]

    @staticmethod
    def find_connected_line(current_line, edge_to_gmsh):
        all_curves = gmsh.model.getEntities(1)
        curve_tags = [curve[1] for curve in all_curves]

        if current_line not in curve_tags:
            print(f"Ошибка: Кривая с тегом {current_line} не существует.")
            return None

        try:
            _, (x1, y1, _), (x2, y2, _) = gmsh.model.getAdjacencies(1, current_line)
        except Exception as e:
            print(f"Ошибка при получении точек для кривой {current_line}: {str(e)}")
            return None

        for edge, lines in edge_to_gmsh.items():
            for line in lines:
                if line == current_line or line not in curve_tags:
                    continue

                try:
                    _, (a1, b1, _), (a2, b2, _) = gmsh.model.getAdjacencies(1, line)
                except Exception as e:
                    print(f"Ошибка при обработке кривой {line}: {str(e)}")
                    continue

                if (a1 == x2 and b1 == y2) or (a2 == x2 and b2 == y2):
                    return line

        return None