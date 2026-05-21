"""
Модуль для сохранения и загрузки проектов.
Сохраняет геометрию (формы + рёбра с BC) и физические параметры.

Архитектура хранения:
  - physics: только материал, начальные условия, модель турбулентности
  - geometry.items: фигуры сцены
  - geometry.edges: рёбра с привязанными BC (единственное место хранения BC)
"""

import json
from pathlib import Path
from typing import Optional

from src.physics.turbulence_models import (
    BoundaryConditions,
    BoundaryConditionType,
    InitialConditions,
    InletBoundaryConditions,
    Material,
    OpenBoundaryConditions,
    TurbulenceModel,
    WallBoundaryConditions,
    WallType,
)
from src.shapes.boolean_item import BooleanShapeItem
from src.shapes.ellipse_item import EllipseItem
from src.shapes.line_item import LineItem
from src.shapes.parametric_curve_item import ParametricCurveItem
from src.shapes.rectangle_item import RectangleItem
from src.widgets.edge_item import EdgeItem
from src.widgets.grid_scene import GridScene


class ProjectSerializer:
    """Сериализатор проекта для сохранения/загрузки данных."""

    def __init__(self):
        self.material = Material()
        self.initial_conditions = InitialConditions()
        self.turbulence_model = TurbulenceModel.LAMINAR
        # boundary_conditions здесь НЕ хранятся — они живут на рёбрах сцены.
        # Список нужен только как временный буфер после десериализации для MainWindow.
        self.restored_boundary_conditions: list[BoundaryConditions] = []

    # -------------------------------------------------------------------------
    # Вспомогательные методы сериализации
    # -------------------------------------------------------------------------

    def _serialize_bc(self, bc: BoundaryConditions) -> dict:
        """
        Единственное место сериализации одного BC-объекта.
        Тип всегда сохраняется в нижнем регистре для надёжного сравнения.
        """
        bc_data: dict = {"type": bc.type.value.lower()}

        if isinstance(bc, InletBoundaryConditions):
            bc_data["u"] = float(bc.u)
            bc_data["v"] = float(bc.v)
            if bc.k is not None:
                bc_data["k"] = float(bc.k)
            if bc.omega is not None:
                bc_data["omega"] = float(bc.omega)
        elif isinstance(bc, OpenBoundaryConditions):
            if bc.k is not None:
                bc_data["k"] = float(bc.k)
            if bc.omega is not None:
                bc_data["omega"] = float(bc.omega)
        elif isinstance(bc, WallBoundaryConditions):
            bc_data["wall"] = bc.wall.value

        return bc_data

    def _deserialize_bc(self, bc_data: dict) -> BoundaryConditions:
        """
        Единственное место десериализации одного BC-объекта.
        Тип нормализуется в нижний регистр перед сравнением.
        """
        bc_type = bc_data.get("type", "wall").lower()

        if bc_type == "inlet":
            bc = InletBoundaryConditions()
            bc.u = bc_data.get("u", 0.0)
            bc.v = bc_data.get("v", 0.0)
            bc.k = bc_data.get("k", 4.184e-7)
            bc.omega = bc_data.get("omega", 2.78)
        elif bc_type == "open":
            bc = OpenBoundaryConditions()
            bc.k = bc_data.get("k", 4.184e-7)
            bc.omega = bc_data.get("omega", 2.78)
        elif bc_type == "wall":
            bc = WallBoundaryConditions()
            wall_str = bc_data.get("wall", "no_slip")
            bc.wall = WallType.NO_SLIP if wall_str == "no_slip" else WallType.SLIP
        else:
            # Неизвестный тип — возвращаем базовый wall как безопасный fallback
            bc = WallBoundaryConditions()
            bc.wall = WallType.NO_SLIP

        return bc

    # -------------------------------------------------------------------------
    # Сериализация геометрии
    # -------------------------------------------------------------------------

    def _serialize_shape(self, item) -> Optional[dict]:
        """Сериализует одну фигуру. Возвращает None если тип неизвестен."""
        if isinstance(item, LineItem):
            line = item.line()
            return {
                "type": "line",
                "x1": float(line.x1()),
                "y1": float(line.y1()),
                "x2": float(line.x2()),
                "y2": float(line.y2()),
            }
        elif isinstance(item, RectangleItem):
            rect = item.rect()
            return {
                "type": "rectangle",
                "x": float(rect.x()),
                "y": float(rect.y()),
                "width": float(rect.width()),
                "height": float(rect.height()),
            }
        elif isinstance(item, EllipseItem):
            rect = item.rect()
            return {
                "type": "ellipse",
                "x": float(rect.x()),
                "y": float(rect.y()),
                "width": float(rect.width()),
                "height": float(rect.height()),
            }
        elif isinstance(item, ParametricCurveItem):
            path = item.path()
            points = [
                {"x": float(path.elementAt(i).x), "y": float(path.elementAt(i).y)}
                for i in range(path.elementCount())
            ]
            return {"type": "parametric_curve", "points": points}
        elif isinstance(item, BooleanShapeItem):
            print(f"[serialize boolean] edges count: {len(item.edges)}")
            for edge in item.edges:
                p = edge.path()
                print(f"  edge {edge.id}: elementCount={p.elementCount()}, boundingRect={p.boundingRect()}")
                sp = edge.sceneTransform().map(p)
                print(f"  edge {edge.id} scene path: elementCount={sp.elementCount()}, boundingRect={sp.boundingRect()}")
            # Сохраняем путь фигуры
            path = item.path()
            elements = []
            i = 0
            while i < path.elementCount():
                elem = path.elementAt(i)
                t = elem.type.value
                if t == 0:
                    elements.append({"t": 0, "x": float(elem.x), "y": float(elem.y)})
                    i += 1
                elif t == 1:
                    elements.append({"t": 1, "x": float(elem.x), "y": float(elem.y)})
                    i += 1
                elif t == 2:  # CurveTo — три элемента подряд
                    c1 = path.elementAt(i)
                    c2 = path.elementAt(i + 1)
                    ep = path.elementAt(i + 2)
                    elements.append({
                        "t": 2,
                        "c1x": float(c1.x), "c1y": float(c1.y),
                        "c2x": float(c2.x), "c2y": float(c2.y),
                        "x": float(ep.x), "y": float(ep.y),
                    })
                    i += 3
                else:
                    i += 1
        
            # Сохраняем рёбра с их путями и ID
            edges_info = []
            for edge in item.edges:
                ep = edge.path()
                edge_elems = []
                for j in range(ep.elementCount()):
                    ee = ep.elementAt(j)
                    edge_elems.append({
                        "t": ee.type.value,
                        "x": float(ee.x),
                        "y": float(ee.y),
                    })
                edges_info.append({"id": edge.id, "path": edge_elems})
        
            return {
                "type": "boolean",
                "elements": elements,
                "edges": edges_info,
            }
        return None

    def _serialize_edge(self, edge: EdgeItem) -> Optional[dict]:
        """
        Сериализует ребро с его граничным условием.
        Рёбра без BC не сохраняются — они восстанавливаются как дочерние
        объекты своих родительских фигур.
        """
        bc = getattr(edge, "boundary_conditions", None)
        if bc is None:
            return None

        return {
            "id": edge.id,
            "boundary_condition": self._serialize_bc(bc),
        }

    def serialize_scene(self, scene: GridScene) -> dict:
        """
        Сериализует сцену.
        Фигуры и рёбра с BC хранятся раздельно, но в одном разделе geometry.
        """
        shapes_data = []
        edges_data = []

        for item in scene.items():
            if isinstance(item, EdgeItem):
                edge_dict = self._serialize_edge(item)
                if edge_dict:
                    edges_data.append(edge_dict)
            else:
                shape_dict = self._serialize_shape(item)
                if shape_dict:
                    shapes_data.append(shape_dict)

        return {"items": shapes_data, "edges": edges_data}

    # -------------------------------------------------------------------------
    # Сериализация физики (без BC — они хранятся в geometry.edges)
    # -------------------------------------------------------------------------

    def serialize_physics(self) -> dict:
        """
        Сериализует материал, начальные условия и модель турбулентности.
        Граничные условия НЕ включаются — они сохраняются вместе с рёбрами.
        """
        return {
            "material": {
                "rho": float(self.material.rho),
                "mu": float(self.material.mu),
            },
            "initial_conditions": {
                "u": float(self.initial_conditions.u),
                "v": float(self.initial_conditions.v),
                "p": float(self.initial_conditions.p),
                "k": float(self.initial_conditions.k),
                "omega": float(self.initial_conditions.omega),
            },
            "turbulence_model": self.turbulence_model.value,
        }

    # -------------------------------------------------------------------------
    # Десериализация физики
    # -------------------------------------------------------------------------

    def deserialize_physics(self, physics_data: dict) -> None:
        """
        Восстанавливает материал, начальные условия и модель турбулентности.
        BC восстанавливаются отдельно через restore_boundary_conditions.
        """
        if "material" in physics_data:
            mat = physics_data["material"]
            self.material.rho = mat.get("rho", 1.204)
            self.material.mu = mat.get("mu", 1.81397e-5)

        if "initial_conditions" in physics_data:
            ic = physics_data["initial_conditions"]
            self.initial_conditions.u = ic.get("u", 0.0)
            self.initial_conditions.v = ic.get("v", 0.0)
            self.initial_conditions.p = ic.get("p", 0.0)
            self.initial_conditions.k = ic.get("k", 4.184e-7)
            self.initial_conditions.omega = ic.get("omega", 2.78)

        if "turbulence_model" in physics_data:
            try:
                self.turbulence_model = TurbulenceModel(
                    physics_data["turbulence_model"]
                )
            except ValueError:
                self.turbulence_model = TurbulenceModel.LAMINAR

    # -------------------------------------------------------------------------
    # Публичный API
    # -------------------------------------------------------------------------

    def save_project(self, filepath: str, scene: GridScene) -> bool:
        """Сохраняет проект в JSON-файл."""
        try:
            project_data = {
                "version": 1,
                "geometry": self.serialize_scene(scene),
                "physics": self.serialize_physics(),
            }
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(project_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения проекта: {e}")
            return False

    def load_project(self, filepath: str) -> Optional[dict]:
        """Загружает проект из JSON-файла. Возвращает сырой словарь или None."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки проекта: {e}")
            return None

    def apply_edge_boundary_conditions(
        self,
        edges_data: list[dict],
        scene: GridScene,
        boundary_edges_out: list,
        boundary_conditions_out: list,
    ) -> None:
        """
        Восстанавливает BC на рёбрах сцены по данным из geometry.edges.

        Заполняет boundary_edges_out и boundary_conditions_out —
        те самые списки, которыми управляет MainWindow.
        Объекты BC не дублируются: один BC-объект на одно ребро.
        """
        # Строим индекс всех рёбер сцены: id → EdgeItem
        edge_map: dict[str, EdgeItem] = {}
        for item in scene.items():
            if hasattr(item, "edges"):
                for edge in item.edges:
                    edge_map[edge.id] = edge

        print(f"[apply_bc] edge_map ids: {list(edge_map.keys())}")
        print(f"[apply_bc] edges_data ids: {[e.get('id') for e in edges_data]}")

        for edge_data in edges_data:
            edge_id = edge_data.get("id")
            bc_data = edge_data.get("boundary_condition")
            if not edge_id or not bc_data:
                continue

            edge = edge_map.get(edge_id)
            if edge is None:
                # Ребро не найдено на сцене — пропускаем
                continue

            bc = self._deserialize_bc(bc_data)
            edge.boundary_conditions = bc

            boundary_edges_out.append(edge)
            boundary_conditions_out.append(bc)