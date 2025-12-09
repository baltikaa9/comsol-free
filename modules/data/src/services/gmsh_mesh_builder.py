import gmsh
import numpy as np
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QPainterPath

from modules.data.src.physics.turbulence_models import BoundaryConditions
from modules.data.src.widgets.edge_item import EdgeItem


class GmshMeshBuilder:
    def __init__(self, grid_spacing: int = 1, filename: str = 'mesh.msh', regular: bool = False):
        self.grid_spacing = grid_spacing
        self.filename = filename
        self.__boundary_lines: dict[str, list[int]] = {}
        self.boundary_conditions: dict[int, BoundaryConditions] = {}

        gmsh.initialize()
        gmsh.model.add("geometry")
        gmsh.option.setNumber("Mesh.MshFileVersion", 2)

        if regular:
            # --- НАСТРОЙКИ ДЛЯ КВАДРИЛАТЕРАЛЬНОЙ СЕТКИ (Quad Mesh) ---
            # 1. Принудительно пытаться объединять треугольники в четырехугольники (Quads)
            gmsh.option.setNumber("Mesh.RecombineAll", 1)

            # 2. Выбор алгоритма для Quad-сетки: 8 = Frontal-Delaunay for Quads
            # (Лучший алгоритм для структурирования Quad-элементов)
            gmsh.option.setNumber("Mesh.Algorithm", 8)

            # 3. Алгоритм подразделения для улучшения качества Quad-сетки
            gmsh.option.setNumber("Mesh.SubdivisionAlgorithm", 1)

        # Сглаживание границ для более ровной сетки (опционально)
        gmsh.option.setNumber("Mesh.Smoothing", 10)

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

        outer_loop = loops_tags[0]
        inner_loops = loops_tags[1:]

        domain_surfaces = []
        hole_surfaces = []

        # surface = gmsh.model.geo.addPlaneSurface(loops_tags)
        surface_domain = gmsh.model.geo.addPlaneSurface([outer_loop] + inner_loops)
        domain_surfaces.append(surface_domain)

        # gmsh.model.geo.mesh.setRecombine(2, surface_domain)

        if inner_loops:
            for hole_loop_tag in inner_loops:
                # Создаем поверхность, ограниченную только внутренним контуром
                s_hole = gmsh.model.geo.addPlaneSurface([hole_loop_tag])
                hole_surfaces.append(s_hole)

                # Принудительное создание квадрилатеральной сетки для отверстия
                # gmsh.model.geo.mesh.setRecombine(2, s_hole)

        gmsh.model.geo.synchronize()

        gmsh.model.addPhysicalGroup(dim=2, tags=domain_surfaces, tag=1, name='Domain')

        if hole_surfaces:
            gmsh.model.addPhysicalGroup(dim=2, tags=hole_surfaces, tag=2, name='Hole')

        gmsh.model.mesh.generate(2)

    def generate_structured_mask(self, edges: list[EdgeItem], dx: float, dy: float):
        """
        Создает регулярную сетку и маску принадлежности домену, используя ядро Gmsh.

        :param edges: Список ребер геометрии.
        :param dx: Шаг сетки по X (в мировых координатах).
        :param dy: Шаг сетки по Y (в мировых координатах).
        :return: (X, Y, Mask) - 2D массивы координат и маска (1=Fluid, 0=Solid/Hole).
        """

        # 1. Очищаем Gmsh и строим геометрию
        # ВНИМАНИЕ: Здесь могут быть проблемы, если Gmsh уже инициализирован и используется
        # другими частями программы. Лучше использовать save/restore.
        # Но если метод вызывается изолированно, gmsh.clear() подходит.
        gmsh.clear()

        loops = self.build_closed_loops(edges)
        loop_tags = []

        # Размер элемента сетки Gmsh должен быть меньше или равен шагу маски для точности
        mesh_size = min(dx, dy)

        for loop in loops:
            # Координаты точек в Gmsh будут поделены на self.grid_spacing!
            loop_tags.append(self.add_loop(loop, mesh_size))

        if not loop_tags:
            return np.array([]), np.array([]), np.array([])

        surface = gmsh.model.geo.addPlaneSurface(loop_tags)
        gmsh.model.geo.synchronize()
        gmsh.model.mesh.generate(2)

        # 2. Определяем границы и создаем регулярную сетку
        bbox = gmsh.model.getBoundingBox(-1, -1)
        # Границы возвращаются в масштабе Gmsh (после деления на self.grid_spacing)
        min_x_gmsh, min_y_gmsh = bbox[0], bbox[1]
        max_x_gmsh, max_y_gmsh = bbox[3], bbox[4]

        # Переводим границы обратно в мировые координаты
        start_x = min_x_gmsh * self.grid_spacing
        end_x = max_x_gmsh * self.grid_spacing
        start_y = min_y_gmsh * self.grid_spacing
        end_y = max_y_gmsh * self.grid_spacing

        # Создаем одномерные массивы координат
        # Добавляем небольшой запас, чтобы включить последний узел
        x_range = np.arange(start_x, end_x + dx/100, dx)
        y_range = np.arange(start_y, end_y + dy/100, dy)

        X, Y = np.meshgrid(x_range, y_range)
        Mask = np.zeros_like(X, dtype=int)

        rows, cols = X.shape
        eps = 1e-9 # Малый допуск для смещения точки

        # 3. Заполняем маску, опрашивая Gmsh
        for i in range(rows):
            for j in range(cols):
                # Координаты для запроса в масштабе Gmsh
                gx = X[i, j] / self.grid_spacing
                gy = Y[i, j] / self.grid_spacing

                try:
                    # Смещаем точку на eps, чтобы избежать проблем на границах и узлах
                    # getElementByCoordinates: возвращает tag, u, v, uMap, vMap, wMap
                    tag, _, _, _, _, _ = gmsh.model.mesh.getElementByCoordinates(
                        gx + eps, gy + eps, 0, dim=2, strict=True
                    )

                    if tag > 0:
                        Mask[i, j] = 1 # Fluid / Domain

                except Exception:
                    # Точка вне сгенерированной сетки (Hole / Wall)
                    Mask[i, j] = 0

        return X, Y, Mask

    def __del__(self):
        gmsh.write(self.filename)
        gmsh.fltk.run()
        gmsh.finalize()
