import json

import gmsh
import matplotlib.pyplot as plt
import numpy as np
from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainterPath
from src.physics.turbulence_models import BoundaryConditions
from src.widgets.edge_item import EdgeItem


class StructuredMeshBuilder:
    """
    Построитель структурированной прямоугольной конечно-разностной сетки.
    В отличие от GmshMeshBuilder, создаёт регулярную сетку с прямоугольными ячейками.
    """

    def __init__(self, grid_spacing: int = 1, filename: str = 'structured_mesh.json'):
        """
        :param grid_spacing: Масштаб координат (делитель для преобразования экранных координат)
        :param filename: Имя выходного файла
        """
        self.grid_spacing = grid_spacing
        self.filename = filename

    def build_closed_loops(self, edges: list[EdgeItem]) -> list[list[EdgeItem]]:
        """
        Строит замкнутые петли из набора рёбер.
        Возвращает список петель, где каждая петля - список EdgeItem в порядке обхода.
        """
        unused = set(edges)
        loops = []

        while unused:
            current = unused.pop()
            loop = [current]

            # Растём вперёд
            while True:
                end_pt = loop[-1].p2

                # Ищем неиспользованное ребро, начало которого совпадает с end_pt
                candidate = None
                for e in list(unused):
                    if self.equal_points(e.p1, end_pt):
                        candidate = e
                        break
                    # Если совпадает p2 - переворачиваем
                    if self.equal_points(e.p2, end_pt):
                        e.reverse()
                        candidate = e
                        break

                if not candidate:
                    break

                unused.remove(candidate)
                loop.append(candidate)

                # Если вернулись к стартовой точке - цикл замкнулся
                if self.equal_points(loop[0].p1, loop[-1].p2):
                    loops.append(loop)
                    break

        return loops

    def equal_points(self, a: QPointF, b: QPointF, tol=1e-3) -> bool:
        """Проверка равенства двух точек с допуском"""
        return (a - b).manhattanLength() < tol

    def loop_area(self, loop: list[EdgeItem]) -> float:
        """
        Вычисляет площадь замкнутой петли по формуле Гаусса (shoelace formula).
        Используется для определения внешнего контура (самая большая площадь).
        """
        area = 0.0
        for edge in loop:
            x1, y1 = edge.p1.x(), edge.p1.y()
            x2, y2 = edge.p2.x(), edge.p2.y()
            area += (x1 * y2 - x2 * y1)
        return abs(area) / 2.0

    def create_path_from_loop(self, loop: list[EdgeItem]) -> QPainterPath:
        """
        Создаёт QPainterPath из петли рёбер для проверки принадлежности точки.
        Дискретизирует каждое ребро на точки и соединяет их линиями.
        """
        if not loop:
            return QPainterPath()

        combined_path = QPainterPath()

        # Количество точек для дискретизации каждого ребра
        num_samples = 50

        is_first = True

        for edge in loop:
            path = edge.path()

            # Дискретизируем путь на точки
            for i in range(num_samples + 1):
                t = i / num_samples
                point = path.pointAtPercent(t)

                if is_first and i == 0:
                    combined_path.moveTo(point)
                    is_first = False
                else:
                    combined_path.lineTo(point)

        combined_path.closeSubpath()
        return combined_path

    def build_mesh(self, edges: list[EdgeItem], dx: float, dy: float) -> dict:
        """
        Построение структурированной прямоугольной сетки.

        :param edges: Список рёбер с граничными условиями
        :param dx: Шаг сетки по X
        :param dy: Шаг сетки по Y
        :return: Словарь с данными сетки
        """
        # 1. Строим замкнутые петли
        loops = self.build_closed_loops(edges)
        if not loops:
            raise ValueError("Не удалось построить замкнутые петли из рёбер")

        # 2. Сортируем по площади (самая большая = внешний контур)
        loops.sort(key=lambda loop: self.loop_area(loop), reverse=True)
        outer_loop = loops[0]
        inner_loops = loops[1:] if len(loops) > 1 else []

        # 3. Находим bounding box и создаём сетку
        all_edges = [edge for loop in loops for edge in loop]
        bbox = self._get_bounding_box(all_edges)

        # Масштабируем шаги сетки в пиксельные единицы
        dx_px = dx * self.grid_spacing
        dy_px = dy * self.grid_spacing

        # Добавляем небольшой отступ в пикселях
        margin = max(dx_px, dy_px)
        min_x = bbox['min_x'] - margin
        max_x = bbox['max_x'] + margin
        min_y = bbox['min_y'] - margin
        max_y = bbox['max_y'] + margin

        # Создаём одномерные массивы координат в пикселях
        x_range_px = np.arange(min_x, max_x + dx_px / 2, dx_px)
        y_range_px = np.arange(min_y, max_y + dy_px / 2, dy_px)
        X, Y = np.meshgrid(x_range_px, y_range_px)

        # 4. Создаём маску домена (работает в пиксельных координатах)
        mask = self._create_domain_mask(X, Y, outer_loop, inner_loops)

        # 5. Определяем граничные узлы и назначаем граничные условия (работает в пиксельных координатах)
        bc_id = self._assign_boundary_conditions(X, Y, mask, edges)

        # 6. Формируем результат, масштабируя координаты обратно в мировые единицы
        mesh_data = {
            'grid': {
                'x': (x_range_px / self.grid_spacing).tolist(),
                'y': (y_range_px / self.grid_spacing).tolist(),
                'dx': dx,
                'dy': dy,
                'shape': list(X.shape),
                'grid_spacing': self.grid_spacing
            },
            'mask': mask.tolist(),
            'bc_id': bc_id.tolist(),
        }

        return mesh_data

    def _get_bounding_box(self, edges: list[EdgeItem]) -> dict:
        """Находит bounding box для набора рёбер"""
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')

        for edge in edges:
            path = edge.path()
            for i in range(path.elementCount()):
                elem = path.elementAt(i)
                min_x = min(min_x, elem.x)
                max_x = max(max_x, elem.x)
                min_y = min(min_y, elem.y)
                max_y = max(max_y, elem.y)

        return {'min_x': min_x, 'max_x': max_x, 'min_y': min_y, 'max_y': max_y}

    def _create_domain_mask(
            self,
            X: np.ndarray,
            Y: np.ndarray,
            outer_loop: list[EdgeItem],
            inner_loops: list[list[EdgeItem]]
    ) -> np.ndarray:
        """
        Создаёт маску домена: 1 = жидкость, 0 = твёрдое тело/пустота.
        Точка принадлежит домену, если она внутри внешнего контура И снаружи всех внутренних.
        """
        rows, cols = X.shape
        mask = np.zeros((rows, cols), dtype=int)

        # Создаём QPainterPath для внешнего контура
        outer_path = self.create_path_from_loop(outer_loop)

        # Создаём QPainterPath для каждого внутреннего контура (дырки)
        inner_paths = [self.create_path_from_loop(loop) for loop in inner_loops]

        # Проверяем каждый узел сетки
        # Используем небольшую окрестность для включения граничных точек
        offset = 0.1  # Маленькое смещение для проверки окрестности узла

        for i in range(rows):
            for j in range(cols):
                x, y = X[i, j], Y[i, j]

                # Проверяем точку и её небольшую окрестность (5 точек)
                points_to_check = [
                    QPointF(x, y),           # Центр
                    QPointF(x - offset, y),  # Слева
                    QPointF(x + offset, y),  # Справа
                    QPointF(x, y - offset),  # Снизу
                    QPointF(x, y + offset),  # Сверху
                ]

                # Если хотя бы одна точка внутри внешнего контура - включаем узел
                inside_outer = any(outer_path.contains(p) for p in points_to_check)

                # Проверяем: снаружи всех внутренних контуров? (проверяем центр)
                inside_any_inner = any(inner_path.contains(QPointF(x, y)) for inner_path in inner_paths)

                # Узел принадлежит домену, если внутри outer и снаружи inner
                if inside_outer and not inside_any_inner:
                    mask[i, j] = 1

        return mask

    def _assign_boundary_conditions(
            self,
            X: np.ndarray,
            Y: np.ndarray,
            mask: np.ndarray,
            edges: list[EdgeItem]
    ) -> np.ndarray:
        """
        Назначает граничные условия узлам сетки.
        Возвращает массив bc_id, где 0 = внутренний узел, 1,2,3... = номер граничного условия.

        Алгоритм:
        1. Дискретизирует каждый EdgeItem на точки
        2. Для каждой точки находит ближайший узел сетки
        3. Назначает bc_id только если узел внутри домена (mask=1)
        4. Фильтрует углы (перпендикулярные соседи mask=0)
        """
        rows, cols = X.shape
        bc_id = np.zeros((rows, cols), dtype=int)

        # Группируем рёбра по граничным условиям
        bc_groups = {}
        bc_id_to_index = {}
        bc_index = 1
        for edge in edges:
            bc = edge.boundary_conditions
            bc_id_key = id(bc)
            if bc_id_key not in bc_groups:
                bc_groups[bc_id_key] = []
                bc_id_to_index[bc_id_key] = bc_index
                bc_index += 1
            bc_groups[bc_id_key].append(edge)

        dx = X[0, 1] - X[0, 0] if cols > 1 else 1
        dy = Y[1, 0] - Y[0, 0] if rows > 1 else 1
        grid_step = min(dx, dy)

        # Дискретизируем рёбра и находим ближайшие узлы
        for bc_id_key, group_edges in bc_groups.items():
            for edge in group_edges:
                path = edge.path()
                path_length = path.length()
                # Плотная дискретизация
                num_samples = max(100, int(path_length / grid_step * 3))

                for t_idx in range(num_samples + 1):
                    t = t_idx / num_samples
                    point = path.pointAtPercent(t)
                    x_pt = point.x()
                    y_pt = point.y()

                    # Находим несколько ближайших узлов (в радиусе ~2 ячеек)
                    search_radius_cells = 2
                    candidates = []

                    # Определяем диапазон поиска
                    i_center = np.argmin(np.abs(Y[:, 0] - y_pt))
                    j_center = np.argmin(np.abs(X[0, :] - x_pt))

                    i_min = max(0, i_center - search_radius_cells)
                    i_max = min(rows, i_center + search_radius_cells + 1)
                    j_min = max(0, j_center - search_radius_cells)
                    j_max = min(cols, j_center + search_radius_cells + 1)

                    # Ищем среди соседних узлов
                    for i in range(i_min, i_max):
                        for j in range(j_min, j_max):
                            if mask[i, j] == 1:
                                dist = (X[i, j] - x_pt)**2 + (Y[i, j] - y_pt)**2
                                candidates.append((dist, i, j))

                    # Выбираем ближайший узел с mask=1
                    if candidates:
                        candidates.sort()
                        _, i_best, j_best = candidates[0]
                        bc_id[i_best, j_best] = bc_id_to_index[bc_id_key]

        return bc_id

    def _distance_to_path(self, point: QPointF, edges: list[EdgeItem], max_distance: float) -> float:
        """
        Вычисляет минимальное расстояние от точки до набора рёбер.
        Возвращает max_distance если не найдено ближе.
        """
        min_dist = max_distance

        for edge in edges:
            path = edge.path()
            # Дискретизируем путь на точки (плотность зависит от длины пути)
            path_length = path.length()
            # Используем max_distance как оценку шага сетки
            grid_step = max_distance / 1.5
            num_samples = max(100, int(path_length / grid_step * 3))
            for i in range(num_samples + 1):
                t = i / num_samples
                path_point = path.pointAtPercent(t)
                dx = path_point.x() - point.x()
                dy = path_point.y() - point.y()
                dist = (dx * dx + dy * dy) ** 0.5
                if dist < min_dist:
                    min_dist = dist

        return min_dist

    def _is_boundary_node(self, mask: np.ndarray, i: int, j: int) -> bool:
        """
        Проверяет, является ли узел (i,j) граничным.
        Граничный узел: mask[i,j] == 1 и хотя бы один сосед == 0.

        ПРИМЕЧАНИЕ: Этот метод больше не используется для назначения BC.
        Оставлен для возможного использования в будущем.
        """
        if mask[i, j] != 1:
            return False

        rows, cols = mask.shape
        # Проверяем 4 соседей (сверху, снизу, слева, справа)
        neighbors = [
            (i - 1, j), (i + 1, j),
            (i, j - 1), (i, j + 1)
        ]

        for ni, nj in neighbors:
            if 0 <= ni < rows and 0 <= nj < cols:
                if mask[ni, nj] == 0:
                    return True

        return False

    def save_to_json(self, mesh_data: dict, initial_conditions, boundary_conditions, material):
        """
        Сохраняет данные сетки и физические параметры в JSON файл.

        :param mesh_data: Данные сетки из build_mesh()
        :param initial_conditions: Объект InitialConditions
        :param boundary_conditions: Список BoundaryConditions
        :param material: Объект Material
        """
        output = {
            'mesh': mesh_data,
            'material': {
                'rho': material.rho,
                'mu': material.mu
            },
            'initial_conditions': {
                'u': initial_conditions.u,
                'v': initial_conditions.v,
                'p': initial_conditions.p
            },
            'boundary_conditions': []
        }

        # Добавляем турбулентные параметры, если есть
        if hasattr(initial_conditions, 'k') and initial_conditions.k is not None:
            output['initial_conditions']['k'] = initial_conditions.k
            output['initial_conditions']['omega'] = initial_conditions.omega

        # Сохраняем граничные условия
        for idx, bc in enumerate(boundary_conditions, start=1):
            bc_entry = {
                'id': idx,
                'type': bc.type.value
            }

            # Добавляем специфичные для типа параметры
            if hasattr(bc, 'u'):
                bc_entry['u'] = bc.u
            if hasattr(bc, 'v'):
                bc_entry['v'] = bc.v
            if hasattr(bc, 'k'):
                bc_entry['k'] = bc.k
            if hasattr(bc, 'omega'):
                bc_entry['omega'] = bc.omega
            if hasattr(bc, 'wall'):
                bc_entry['wall'] = bc.wall.value

            output['boundary_conditions'].append(bc_entry)

        # Сохраняем в файл
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        return self.filename

    def visualize_mesh(self, mesh_data: dict, edges: list[EdgeItem]):
        """
        Визуализирует структурированную сетку через Gmsh.
        Создаёт квадратные элементы и использует Gmsh GUI для визуализации.

        :param mesh_data: Данные сетки из build_mesh()
        :param edges: Список рёбер для отрисовки контура
        """
        # Извлекаем данные
        x = np.array(mesh_data['grid']['x'])
        y = np.array(mesh_data['grid']['y'])
        mask = np.array(mesh_data['mask'])
        bc_id = np.array(mesh_data['bc_id'])

        print(f"[DEBUG] Визуализация структурированной сетки {len(x)}x{len(y)} через Gmsh...")

        # Инициализация Gmsh
        gmsh.initialize()

        # Задаём цвет сетки ДО создания модели. Иногда это имеет значение.
        # Ручной расчёт цвета (A-B-G-R), т.к. gmsh.color может отсутствовать
        # Это не работает в среде пользователя, поэтому убираем попытку
        # r, g, b, a = 211, 211, 211, 255  # Light Gray
        # gray_color = (a << 24) | (b << 16) | (g << 8) | r
        # try:
        #     gmsh.option.setNumber("Mesh.Color.Quads", gray_color)
        #     print("[INFO] Цвет сетки изменён на серый.")
        # except Exception as e:
        #     print(f"[WARNING] Не удалось задать цвет сетки. Ошибка API Gmsh: {e}")
        #     print("[WARNING] Точки и линии могут сливаться с цветом сетки по умолчанию.")

        gmsh.model.add("structured_mesh_viz")

        # Создаём узлы и элементы
        node_tags = []
        node_coords = []
        node_map = {}  # (i, j) -> node_tag
        node_tag = 1

        # Добавляем все узлы где mask == 1
        for i in range(len(y)):
            for j in range(len(x)):
                if mask[i, j] == 1:
                    node_tags.append(node_tag)
                    node_coords.extend([x[j], y[i], 0.0])
                    node_map[(i, j)] = node_tag
                    node_tag += 1

        # Создаём дискретную поверхность для узлов и элементов
        surface_tag = 1
        gmsh.model.addDiscreteEntity(2, surface_tag)

        # Добавляем узлы в Gmsh
        if node_tags:
            gmsh.model.mesh.addNodes(2, surface_tag, node_tags, node_coords)

        # Создаём квадратные элементы (elementType=3 для 4-node quad)
        elem_tags = []
        elem_node_tags = []
        elem_tag = 1

        # Проходим по всем ячейкам и создаём квадраты
        for i in range(len(y) - 1):
            for j in range(len(x) - 1):
                # Проверяем что все 4 угла существуют
                if (mask[i, j] == 1 and mask[i, j+1] == 1 and
                    mask[i+1, j] == 1 and mask[i+1, j+1] == 1):

                    # Узлы квадрата (против часовой стрелки)
                    n1 = node_map[(i, j)]
                    n2 = node_map[(i, j+1)]
                    n3 = node_map[(i+1, j+1)]
                    n4 = node_map[(i+1, j)]

                    elem_tags.append(elem_tag)
                    elem_node_tags.extend([n1, n2, n3, n4])
                    elem_tag += 1

        # Добавляем элементы в Gmsh
        if elem_tags:
            gmsh.model.mesh.addElementsByType(surface_tag, 3, elem_tags, elem_node_tags)

        # --- Визуализация граничных узлов и линий ---

        # 1. Визуализация точек
        point_views = {}  # {bc_id: {'tag': view_tag, 'data': []}}

        for i in range(len(y)):
            for j in range(len(x)):
                bc_val = int(bc_id[i, j])
                if bc_val > 0 and mask[i, j] == 1:
                    if bc_val not in point_views:
                        view_tag = gmsh.view.add(f"BC Nodes (ID {bc_val})")
                        point_views[bc_val] = {'tag': view_tag, 'data': []}

                    node_x = x[j]
                    node_y = y[i]
                    # Данные для скалярной точки (SP) со смещением по Z
                    point_views[bc_val]['data'].extend([node_x, node_y, 0.01, float(bc_val)])

        for bc_val, view_data in point_views.items():
            if view_data['data']:
                view_tag = view_data['tag']
                num_points = len(view_data['data']) // 4
                gmsh.view.addListData(view_tag, "SP", num_points, view_data['data'])

                # Настраиваем опции для точек
                gmsh.view.option.setNumber(view_tag, "PointType", 4)
                gmsh.view.option.setNumber(view_tag, "PointSize", 12)


        # 2. Визуализация линий, соединяющих точки
        line_views = {}  # {bc_id: {'tag': view_tag, 'data': []}}

        # Горизонтальные сегменты
        for i in range(len(y)):
            for j in range(len(x) - 1):
                bc1 = int(bc_id[i, j])
                bc2 = int(bc_id[i, j + 1])
                if bc1 > 0 and bc1 == bc2:
                    if bc1 not in line_views:
                        view_tag = gmsh.view.add(f"BC Lines (ID {bc1})")
                        line_views[bc1] = {'tag': view_tag, 'data': []}
                    # Данные для скалярной линии (SL) со смещением по Z
                    line_views[bc1]['data'].extend([x[j], y[i], 0.01, x[j + 1], y[i], 0.01, float(bc1)])

        # Вертикальные сегменты
        for i in range(len(y) - 1):
            for j in range(len(x)):
                bc1 = int(bc_id[i, j])
                bc2 = int(bc_id[i + 1, j])
                if bc1 > 0 and bc1 == bc2:
                    if bc1 not in line_views:
                        view_tag = gmsh.view.add(f"BC Lines (ID {bc1})")
                        line_views[bc1] = {'tag': view_tag, 'data': []}
                    line_views[bc1]['data'].extend([x[j], y[i], 0.01, x[j], y[i + 1], 0.01, float(bc1)])

        for bc_val, view_data in line_views.items():
            if view_data['data']:
                view_tag = view_data['tag']
                num_lines = len(view_data['data']) // 7
                gmsh.view.addListData(view_tag, "SL", num_lines, view_data['data'])
                gmsh.view.option.setNumber(view_tag, "LineWidth", 3)

        print(f"[DEBUG] Created {len(point_views)} BC point views and {len(line_views)} BC line views.")

        # Сохраняем в файл
        viz_filename = 'structured_mesh_viz.msh'
        gmsh.write(viz_filename)
        print(f"[DEBUG] Сетка сохранена в {viz_filename}")
        print(f"[DEBUG] Узлов: {len(node_tags)}, Квадратных элементов: {len(elem_tags)}")

        # Открываем GUI Gmsh для визуализации
        gmsh.fltk.run()

        # Очистка
        gmsh.finalize()