import json

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

        # Добавляем небольшой отступ
        margin = max(dx, dy)
        min_x = bbox['min_x'] - margin
        max_x = bbox['max_x'] + margin
        min_y = bbox['min_y'] - margin
        max_y = bbox['max_y'] + margin

        # Создаём одномерные массивы координат (в исходной системе координат)
        x_range = np.arange(min_x, max_x + dx / 2, dx)
        y_range = np.arange(min_y, max_y + dy / 2, dy)
        X, Y = np.meshgrid(x_range, y_range)

        # 4. Создаём маску домена
        mask = self._create_domain_mask(X, Y, outer_loop, inner_loops)

        # 5. Определяем граничные узлы и назначаем граничные условия
        bc_id = self._assign_boundary_conditions(X, Y, mask, edges)

        # 6. Формируем результат
        mesh_data = {
            'grid': {
                'x': x_range.tolist(),
                'y': y_range.tolist(),
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
        for i in range(rows):
            for j in range(cols):
                point = QPointF(X[i, j], Y[i, j])

                # Проверяем: внутри внешнего контура?
                inside_outer = outer_path.contains(point)

                # Проверяем: снаружи всех внутренних контуров?
                inside_any_inner = any(inner_path.contains(point) for inner_path in inner_paths)

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
        """
        rows, cols = X.shape
        bc_id = np.zeros((rows, cols), dtype=int)

        # Группируем рёбра по граничным условиям
        # Используем id(bc) как ключ, т.к. объекты BoundaryConditions не hashable
        bc_groups = {}
        bc_objects = {}  # Сохраняем соответствие id -> объект bc
        for edge in edges:
            bc = edge.boundary_conditions
            bc_id_key = id(bc)
            if bc_id_key not in bc_groups:
                bc_groups[bc_id_key] = []
                bc_objects[bc_id_key] = bc
            bc_groups[bc_id_key].append(edge)

        # Для каждой группы граничных условий
        bc_index = 1
        for bc_id_key, group_edges in bc_groups.items():
            for edge in group_edges:
                # Дискретизируем путь ребра на точки
                path = edge.path()
                num_samples = max(100, int(path.length() / min(X[0, 1] - X[0, 0], Y[1, 0] - Y[0, 0]) * 2))

                for t_idx in range(num_samples + 1):
                    t = t_idx / num_samples
                    point = path.pointAtPercent(t)
                    x_pt = point.x()
                    y_pt = point.y()

                    # Находим ближайший узел сетки
                    i_nearest = np.argmin(np.abs(Y[:, 0] - y_pt))
                    j_nearest = np.argmin(np.abs(X[0, :] - x_pt))

                    # Проверяем, что узел на границе домена
                    if 0 <= i_nearest < rows and 0 <= j_nearest < cols:
                        if self._is_boundary_node(mask, i_nearest, j_nearest):
                            bc_id[i_nearest, j_nearest] = bc_index

            bc_index += 1

        return bc_id

    def _is_boundary_node(self, mask: np.ndarray, i: int, j: int) -> bool:
        """
        Проверяет, является ли узел (i,j) граничным.
        Граничный узел: mask[i,j] == 1 и хотя бы один сосед == 0.
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
