import json
import os
import sys
from pathlib import Path

from PySide6.QtCore import QEvent, QLineF, QRectF, Qt
from PySide6.QtGui import QIcon, QKeyEvent, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QGraphicsView,
    QInputDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
    QTreeWidgetItem,
)
from src.dialogs.boundary_conditions_dialog import BoundaryConditionsDialog
from src.dialogs.initial_conditions_dialog import InitialConditionsDialog
from src.dialogs.material_dialog import MaterialDialog
from src.dialogs.mesh_dialog import MeshDialog
from src.dialogs.ssh_result_dialog import SSHResultDialog, SSHWorker
from src.dialogs.ssh_settings_dialog import SSHSettingsDialog
from src.dialogs.turbulence_dialog import TurbulenceDialog
from src.event_handler import EventHandler
from src.operations.boolean_operations import BooleanOperations
from src.operations.transformation_operations import TransformationOperations
from src.physics.turbulence_models import (
    BoundaryConditions,
    BoundaryConditionType,
    InitialConditions,
    InletBoundaryConditions,
    Material,
    OpenBoundaryConditions,
    TurbulenceModel,
    TurbulenceParams,
    WallBoundaryConditions,
)
from src.services.command_service import CommandService
from src.services.drawing_service import DrawingService
from src.services.gmsh_mesh_builder import GmshMeshBuilder
from src.services.project_service import ProjectSerializer
from src.services.selection_service import SelectionService
from src.services.ssh_client import SSHClientService, SSHConfig, SSHConfigManager
from src.services.structured_mesh_builder import StructuredMeshBuilder
from src.shapes.ellipse_item import EllipseItem
from src.shapes.line_item import LineItem
from src.shapes.parametric_curve_item import ParametricCurveItem
from src.shapes.rectangle_item import RectangleItem
from src.ui.template import Ui_MainWindow
from src.widgets.edge_item import EdgeItem
from src.widgets.grid_scene import GridScene


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Set window icon
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "assets", "icon.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.grid_spacing = 50
        self.scene = GridScene(spacing=self.grid_spacing)
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)

        self.ui.graphicsView.setScene(self.scene)
        self.ui.graphicsView.setRenderHints(QPainter.RenderHint.Antialiasing)
        self.ui.graphicsView.scale(1, -1)
        self.ui.graphicsView.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.FullViewportUpdate
        )

        self.selection_service = SelectionService(self.scene)
        command_service = CommandService()
        self.event_handler = EventHandler(
            self,
            self.scene,
            self.ui.graphicsView,
            self.ui.propertiesLayout,
            self.selection_service,
            command_service,
        )
        self.drawing_service = DrawingService(
            self, self.scene, command_service, self.selection_service
        )
        self.boolean_operations = BooleanOperations(
            self,
            self.scene,
            command_service,
            self.drawing_service,
            self.selection_service,
        )
        self.transformation_operations = TransformationOperations(
            self, self.scene, command_service, self.selection_service
        )

        self.ui.actionDrawLineByParams.triggered.connect(
            self.drawing_service.draw_line_by_params
        )
        self.ui.actionDrawRectByParams.triggered.connect(
            self.drawing_service.draw_rect_by_params
        )
        self.ui.actionDrawCircleByParams.triggered.connect(
            self.drawing_service.draw_ellipse_by_params
        )
        self.ui.actionDrawCurveByParams.triggered.connect(
            self.drawing_service.draw_curve_by_params
        )
        self.ui.actionDrawParametric.triggered.connect(
            self.drawing_service.draw_parametric
        )
        self.ui.actionUnion.triggered.connect(self.boolean_operations.perform_union)
        self.ui.actionDifference.triggered.connect(
            self.boolean_operations.perform_difference
        )
        self.ui.actionIntersection.triggered.connect(
            self.boolean_operations.perform_intersection
        )
        self.ui.actionMirror.triggered.connect(
            self.transformation_operations.perform_mirror
        )
        self.ui.actionRotate.triggered.connect(
            self.transformation_operations.perform_rotate
        )
        self.ui.actionBuildMesh.triggered.connect(self.build_gmsh_mesh)
        self.ui.actionUploadSSH.triggered.connect(self.upload_to_ssh)
        self.ui.actionSSHSettings.triggered.connect(self.show_ssh_settings)

        # Подключение действий для работы с проектами
        self.ui.actionSaveProject.triggered.connect(self.save_project)
        self.ui.actionOpenProject.triggered.connect(self.open_project)
        self.ui.actionSaveProjectAs.triggered.connect(self.save_project_as)

        # Блокируем сворачивание тулбаров
        for tb in [self.ui.toolBarShapes, self.ui.toolBarOps, self.ui.toolBarMisc]:
            tb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        # SSH сервис (путь к директории comsol-ssh)
        cli_dir = self._get_comsol_ssh_dir()
        self.ssh_client = SSHClientService(cli_dir)

        # Файл сетки по умолчанию
        mesh_file = os.path.join(os.getcwd(), "structured_mesh.json")
        self.ssh_manager = SSHConfigManager("configs/ssh_configs.json")
        # Подставляем дефолтный файл сетки если не задан
        if not self.ssh_manager.configs:
            # Создаем дефолтную конфигурацию
            from src.services.ssh_client import SSHConfig

            default_config = SSHConfig(
                name="Default", project_path="", remote_dir="/home/baltika/projects"
            )
            self.ssh_manager.configs.append(default_config)
            self.ssh_manager.save()

        self.ui.graphicsView.viewport().installEventFilter(self)

        # Инициализация параметров
        self.turbulence_params = TurbulenceParams()
        self.boundary_conditions: list[BoundaryConditions] = []
        self.boundary_edges: list[EdgeItem] = []
        self.initial_conditions = InitialConditions()
        self.material = Material()

        # Переменные для работы с проектами
        self.current_project_path = None  # Путь к текущему проекту
        self.project_serializer = ProjectSerializer()  # Сериализатор проектов

        # Инициализация UI
        self.init_turbulence_ui()

    @staticmethod
    def _get_comsol_ssh_dir() -> Path:
        """Возвращает путь к bin/ с comsol-клиентами."""
        if getattr(sys, "frozen", False):
            base = Path(sys.executable).parent / "_internal"
        else:
            base = Path(__file__).parent.parent.parent.parent
        return base / "bin"

    def eventFilter(self, obj, event: QEvent):
        if obj is self.ui.graphicsView.viewport():
            return self.event_handler.event_filter(event)

        return super().eventFilter(obj, event)

    def keyPressEvent(self, event: QKeyEvent):
        self.event_handler.key_press_event(event)

    def build_gmsh_mesh(self):
        dialog = MeshDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        dx = dialog.get_data()
        mesh_type = dialog.get_mesh_type()
        # visualize = dialog.get_visualize()

        # Фильтруем только рёбра которые ещё существуют на сцене
        valid_edges = [edge for edge in self.boundary_edges if edge.scene() is not None]

        if not valid_edges:
            QMessageBox.warning(
                self, "Ошибка", "Нет рёбер с граничными условиями на сцене!"
            )
            return

        if mesh_type == "structured":
            # Прямоугольная структурированная сетка
            builder = StructuredMeshBuilder(
                self.grid_spacing, filename="structured_mesh.json"
            )
            try:
                mesh_data = builder.build_mesh(valid_edges, dx, dx)

                # Группируем граничные условия
                unique_bc = []
                seen_bc_ids = set()
                for edge in valid_edges:
                    bc = edge.boundary_conditions
                    bc_id = id(bc)
                    if bc_id not in seen_bc_ids:
                        unique_bc.append(bc)
                        seen_bc_ids.add(bc_id)

                output_file = builder.save_to_json(
                    mesh_data, self.initial_conditions, unique_bc, self.material
                )

                # Визуализация сетки
                # if visualize:
                builder.visualize_mesh(mesh_data, valid_edges)

                QMessageBox.information(
                    self,
                    "Готово",
                    f"Структурированная сетка сохранена в {output_file}\n"
                    f"Размер сетки: {mesh_data['grid']['shape']}\n"
                    f"Узлов домена: {sum(sum(row) for row in mesh_data['mask'])}",
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Ошибка", f"Не удалось построить сетку:\n{str(e)}"
                )
        else:
            # Треугольная сетка через GMSH
            builder = GmshMeshBuilder(self.grid_spacing)
            builder.build_mesh(valid_edges, dx)
            self.export_json()

    def init_turbulence_ui(self):
        self.ui.projectTree.itemClicked.connect(self.on_tree_item_clicked)
        self.ui.projectTree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.ui.projectTree.customContextMenuRequested.connect(
            self.show_tree_context_menu
        )
        self.update_project_tree()

    def update_project_tree(self):
        self.ui.projectTree.clear()

        material_item = QTreeWidgetItem(["Настройки материала"])
        material_item.addChild(QTreeWidgetItem([f"ρ: {self.material.rho} кг/м³"]))
        material_item.addChild(QTreeWidgetItem([f"μ: {self.material.mu} Па·с"]))

        # Модель турбулентности
        turbulence_item = QTreeWidgetItem(["Модель турбулентности"])
        turbulence_item.addChild(
            QTreeWidgetItem([f"{self.turbulence_params.model.value}"])
        )

        # Начальные условия
        init_item = QTreeWidgetItem(["Начальные условия"])
        init_item.addChild(QTreeWidgetItem([f"u: {self.initial_conditions.u} м/с"]))
        init_item.addChild(QTreeWidgetItem([f"v: {self.initial_conditions.v} м/с"]))
        init_item.addChild(QTreeWidgetItem([f"p: {self.initial_conditions.p} Па"]))

        if self.turbulence_params.model != TurbulenceModel.LAMINAR:
            init_item.addChild(
                QTreeWidgetItem([f"k: {self.initial_conditions.k} м²/с²"])
            )
            init_item.addChild(
                QTreeWidgetItem([f"omega: {self.initial_conditions.omega} 1/с"])
            )

        # Граничные условия
        bc_item = QTreeWidgetItem(["Граничные условия"])
        for bc in self.boundary_conditions:
            bc_child = QTreeWidgetItem([bc.type.value])
            bc_child.setData(0, Qt.ItemDataRole.UserRole, bc)
            # bc_child.addChild(QTreeWidgetItem([f'Type: {bc.bc_type}']))

            if isinstance(bc, WallBoundaryConditions):
                bc_child.addChild(QTreeWidgetItem([f"wall: {bc.wall.value}"]))
            elif isinstance(bc, InletBoundaryConditions):
                bc_child.addChild(QTreeWidgetItem([f"u: {bc.u} м/с"]))

                bc_child.addChild(QTreeWidgetItem([f"v: {bc.v} м/с"]))

            if (
                isinstance(bc, (InletBoundaryConditions, OpenBoundaryConditions))
                and self.turbulence_params.model != TurbulenceModel.LAMINAR
            ):
                bc_child.addChild(QTreeWidgetItem([f"k: {bc.k} м²/с²"]))

                bc_child.addChild(QTreeWidgetItem([f"omega: {bc.omega} 1/с"]))

            bc_item.addChild(bc_child)

        self.ui.projectTree.addTopLevelItem(material_item)
        self.ui.projectTree.addTopLevelItem(turbulence_item)
        self.ui.projectTree.addTopLevelItem(init_item)
        self.ui.projectTree.addTopLevelItem(bc_item)

    def on_tree_item_clicked(self, item, column):
        parent = item.parent()

        # Для верхнеуровневых элементов
        if not parent:
            if item.text(0) == "Настройки материала":
                self.edit_material()
            elif item.text(0) == "Модель турбулентности":
                self.edit_turbulence_model()
            elif item.text(0) == "Начальные условия":
                self.edit_initial_conditions()
            elif item.text(0) == "Граничные условия":
                self.add_boundary_condition()
            return

        # Для дочерних элементов
        parent_text = parent.text(0)

        if parent_text == "Настройки материала":
            self.edit_material()
        elif parent_text == "Начальные условия":
            self.edit_initial_conditions()
        elif parent_text == "Граничные условия":
            self.edit_boundary_condition(item)

    def add_boundary_condition(self):
        selected_edges = self.selection_service.selected_edges
        if not selected_edges:
            QMessageBox.warning(self, "Ошибка", "Выберите ребра (Alt + клик)!")
            return

        dialog = BoundaryConditionsDialog(selected_edges, self.turbulence_params.model)
        if dialog.exec():
            bc = dialog.get_data()
            self.boundary_conditions.append(bc)

            for edge in selected_edges:
                edge.boundary_conditions = bc
                self.boundary_edges.append(edge)

        self.update_project_tree()
        self.highlight_edges()

    def highlight_edges(self):
        for edge in self.boundary_edges:
            color = (
                Qt.GlobalColor.red
                if edge.boundary_conditions.type == BoundaryConditionType.INLET
                else Qt.GlobalColor.blue
            )
            edge.setPen(QPen(color, 0))

    def edit_material(self):
        dialog = MaterialDialog(self)
        if dialog.exec():
            self.material = dialog.get_data()
            self.update_project_tree()

    def edit_turbulence_model(self):
        dialog = TurbulenceDialog(self.turbulence_params, self)
        if dialog.exec():
            self.turbulence_params = dialog.get_data()
            self.update_project_tree()

    def edit_initial_conditions(self):
        dialog = InitialConditionsDialog(self.turbulence_params.model)
        if dialog.exec():
            self.initial_conditions = dialog.get_data()
            self.update_project_tree()

    def edit_boundary_condition(self, item):
        bc = item.data(0, Qt.ItemDataRole.UserRole)
        dialog = BoundaryConditionsDialog(
            [edge for edge in self.boundary_edges if edge.boundary_conditions == bc],
            self.turbulence_params.model,
        )
        if dialog.exec():
            new_bc = dialog.get_data()
            index = self.boundary_conditions.index(bc)
            self.boundary_conditions[index] = new_bc
            self.update_project_tree()
            self.highlight_edges()

    def show_tree_context_menu(self, position):
        item = self.ui.projectTree.itemAt(position)
        menu = QMenu()

        if item and item.text(0) == "Граничные условия":
            menu.addAction("Добавить условие", self.add_boundary_condition)
        elif item and item.parent() and item.parent().text(0) == "Граничные условия":
            menu.addAction(
                "Удалить условие", lambda: self.delete_boundary_condition(item)
            )

        menu.exec(self.ui.projectTree.viewport().mapToGlobal(position))

    def delete_boundary_condition(self, item):
        bc = item.data(0, Qt.ItemDataRole.UserRole)
        self.boundary_conditions.remove(bc)
        for edge in self.boundary_edges:
            if edge.boundary_conditions == bc:
                self.boundary_edges.remove(edge)
        self.update_project_tree()

    def export_json(self):
        data = {
            "material": {"rho": self.material.rho, "mu": self.material.mu},
            "physics": self.turbulence_params.model.value,
            "init": {
                "u": self.initial_conditions.u,
                "v": self.initial_conditions.v,
                "p": self.initial_conditions.p,
            },
            "boundary": {},
        }

        if self.turbulence_params.model != TurbulenceModel.LAMINAR:
            data["init"].update(
                {"k": self.initial_conditions.k, "om": self.initial_conditions.omega}
            )

        for bc in self.boundary_conditions:
            bounds = [
                edge.id
                for edge in self.boundary_edges
                if edge.boundary_conditions == bc
            ]

            entry: dict = {"bounds": bounds}

            if isinstance(bc, InletBoundaryConditions):
                entry["u"] = bc.u
                entry["v"] = bc.v

            if (
                isinstance(bc, (InletBoundaryConditions, OpenBoundaryConditions))
                and self.turbulence_params.model != TurbulenceModel.LAMINAR
            ):
                entry["k"] = bc.k
                entry["om"] = bc.omega

            if isinstance(bc, WallBoundaryConditions):
                entry["wall"] = bc.wall.value

            key = bc.type.name.lower()
            data["boundary"][key] = entry

        out_path = os.path.join(os.getcwd(), "result_test.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        QMessageBox.information(
            self, "Готово", f"Сетка и настройки сохранены в {out_path}"
        )

    def upload_to_ssh(self):
        configs = self.ssh_manager.configs
        if not configs:
            QMessageBox.warning(
                self, "SSH", "Нет конфигураций. Добавьте через Настройки SSH."
            )
            return

        # Проверяем наличие сетки
        mesh_file = "structured_mesh.json"
        if not Path(mesh_file).exists():
            QMessageBox.warning(
                self, "Ошибка", "Файл сетки не найден. Постройте сетку перед загрузкой."
            )
            return

        names = [c.name for c in configs]
        name, ok = QInputDialog.getItem(
            self, "Выбор конфигурации", "Подключиться как:", names, 0, False
        )
        if not ok:
            return

        cfg = next(c for c in configs if c.name == name)

        # Проверяем, что папка проекта указана
        if not cfg.project_path:
            QMessageBox.warning(
                self, "Ошибка", "Не указана папка с CUDA-проектом в настройках SSH."
            )
            return

        worker = SSHWorker(self.ssh_client, cfg, mesh_file)
        dialog = SSHResultDialog(worker, self)
        dialog.show()
        worker.new_line.connect(dialog.append_line)
        worker.finished.connect(dialog.set_final)
        worker.start()

    def show_ssh_settings(self):
        """Диалог настроек SSH подключения."""
        dialog = SSHSettingsDialog(self.ssh_manager, self)
        dialog.exec()

    def open_project(self):
        """Открывает проект из файла."""
        from PySide6.QtWidgets import QFileDialog

        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть проект",
            "",
            "Проекты (*.json);;Все файлы (*.*)",
        )

        if filepath:
            self._load_from_file(filepath)

    def _restore_geometry(self, geometry_data: dict):
        for item_data in geometry_data.get("items", []):
            item_type = item_data.get("type")
    
            if item_type == "line":
                self.drawing_service.restore_line(
                    QLineF(item_data["x1"], item_data["y1"],
                           item_data["x2"], item_data["y2"])
                )
            elif item_type == "rectangle":
                self.drawing_service.restore_rect(
                    QRectF(item_data["x"], item_data["y"],
                           item_data["width"], item_data["height"])
                )
            elif item_type == "ellipse":
                self.drawing_service.restore_ellipse(
                    QRectF(item_data["x"], item_data["y"],
                           item_data["width"], item_data["height"])
                )
            elif item_type == "parametric_curve":
                points = item_data.get("points", [])
                if not points:
                    continue
                path = QPainterPath()
                path.moveTo(points[0]["x"], points[0]["y"])
                for p in points[1:]:
                    path.lineTo(p["x"], p["y"])
                self.drawing_service.restore_curve(path)
    
            elif item_type == "boolean":
                elements = item_data.get("elements")
                if not elements:
                    continue
            
                path = QPainterPath()
                for e in elements:
                    if e["t"] == 0:
                        path.moveTo(e["x"], e["y"])
                    elif e["t"] == 1:
                        path.lineTo(e["x"], e["y"])
                    elif e["t"] == 2:
                        path.cubicTo(
                            e["c1x"], e["c1y"],
                            e["c2x"], e["c2y"],
                            e["x"], e["y"],
                        )
            
                edges_data = item_data.get("edges", [])
                self.drawing_service.restore_boolean(path, edges_data)

    def _save_to_file(self, filepath: str) -> bool:
        """Сохраняет проект в указанный файл."""
        try:
            # Передаём актуальные параметры в сериализатор
            self.project_serializer.material = self.material
            self.project_serializer.initial_conditions = self.initial_conditions
            self.project_serializer.turbulence_model = self.turbulence_params.model
            # BC не передаём — они живут на рёбрах сцены и сохраняются через serialize_scene

            return self.project_serializer.save_project(filepath, self.scene)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {str(e)}")
            return False

    def save_project(self):
        """Сохраняет текущий проект."""
        if self.current_project_path:
            if self._save_to_file(self.current_project_path):
                QMessageBox.information(self, "Сохранение", "Проект успешно сохранён!")
        else:
            self.save_project_as()

    def save_project_as(self):
        """Сохраняет проект с выбором имени файла."""
        from PySide6.QtWidgets import QFileDialog

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить проект",
            "",
            "Проекты (*.json);;Все файлы (*.*)",
        )
        if not filepath:
            return

        if not filepath.endswith(".json"):
            filepath += ".json"

        if self._save_to_file(filepath):
            self.current_project_path = filepath
            self.setWindowTitle(f"Comsol-FreeFDD - {Path(filepath).name}")
            QMessageBox.information(self, "Сохранение", "Проект успешно сохранён!")

    def _load_from_file(self, filepath: str):
        """Загружает проект из указанного файла."""
        try:
            project_data = self.project_serializer.load_project(filepath)
            if not project_data:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить проект.")
                return

            # 1. Очищаем текущее состояние
            self.scene.clear()
            self.boundary_conditions.clear()
            self.boundary_edges.clear()

            # 2. Восстанавливаем физику (материал, IC, модель турбулентности)
            if "physics" in project_data:
                self.project_serializer.deserialize_physics(project_data["physics"])
                self.material = self.project_serializer.material
                self.initial_conditions = self.project_serializer.initial_conditions
                self.turbulence_params.model = self.project_serializer.turbulence_model

            # 3. Восстанавливаем геометрию (фигуры добавляются на сцену)
            geometry = project_data.get("geometry", {})
            if geometry.get("items"):
                self._restore_geometry(geometry)

            # 4. Восстанавливаем BC на рёбрах сцены.
            #    Метод сам заполняет self.boundary_edges и self.boundary_conditions.
            if geometry.get("edges"):
                self.project_serializer.apply_edge_boundary_conditions(
                    edges_data=geometry["edges"],
                    scene=self.scene,
                    boundary_edges_out=self.boundary_edges,
                    boundary_conditions_out=self.boundary_conditions,
                )

            # 5. Перекрашиваем рёбра в соответствии с типом BC
            self.highlight_edges()

            # 6. Предупреждаем о булевых формах
            boolean_count = sum(
                1 for i in geometry.get("items", [])
                if i.get("type") == "boolean" and not i.get("elements")
            )
            if boolean_count > 0:
                QMessageBox.warning(
                    self,
                    "Внимание",
                    f"В проекте найдено {boolean_count} булевой(ых) форм(ы).\n"
                    "Они не могут быть восстановлены автоматически.\n"
                    "Пожалуйста, пересоздайте их вручную.",
                )

            # 7. Обновляем дерево проекта
            self.update_project_tree()

            self.current_project_path = filepath
            self.setWindowTitle(f"Comsol-FreeFDD - {Path(filepath).name}")
            QMessageBox.information(self, "Загрузка", "Проект успешно загружен!")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке: {str(e)}")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
