from PySide6.QtCore import QEvent
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtGui import QPainter
from PySide6.QtGui import QPen
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QGraphicsView
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QMenu
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QTreeWidgetItem

from modules.data.src.dialogs.boundary_conditions_dialog import BoundaryConditionsDialog
from modules.data.src.dialogs.initial_conditions_dialog import InitialConditionsDialog
from modules.data.src.dialogs.mesh_dialog import MeshDialog
from modules.data.src.dialogs.turbulence_dialog import TurbulenceDialog
from modules.data.src.event_handler import EventHandler
from modules.data.src.operations.boolean_operations import BooleanOperations
from modules.data.src.operations.transformation_operations import TransformationOperations
from modules.data.src.physics.turbulence_models import BoundaryConditionType
from modules.data.src.physics.turbulence_models import BoundaryConditions
from modules.data.src.physics.turbulence_models import InitialConditions
from modules.data.src.physics.turbulence_models import TurbulenceModel
from modules.data.src.physics.turbulence_models import TurbulenceParams
from modules.data.src.services.command_service import CommandService
from modules.data.src.services.drawing_service import DrawingService
from modules.data.src.services.gmsh_mesh_builder import GmshMeshBuilder
from modules.data.src.services.selection_service import SelectionService
from modules.data.src.ui.template import Ui_MainWindow
from modules.data.src.widgets.edge_item import EdgeItem
from modules.data.src.widgets.grid_scene import GridScene


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.grid_spacing = 50
        self.scene = GridScene(spacing=self.grid_spacing)
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)
        self.ui.graphicsView.setScene(self.scene)
        self.ui.graphicsView.setRenderHints(QPainter.RenderHint.Antialiasing)
        self.ui.graphicsView.scale(1, -1)
        self.ui.graphicsView.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

        self.selection_service = SelectionService(self.scene)
        command_service = CommandService()
        self.event_handler = EventHandler(
            self,
            self.scene,
            self.ui.graphicsView,
            self.ui.propertiesLayout,
            self.selection_service,
            command_service
        )
        self.drawing_service = DrawingService(self, self.scene, command_service, self.selection_service)
        self.boolean_operations = BooleanOperations(
            self,
            self.scene,
            command_service,
            self.drawing_service,
            self.selection_service
        )
        self.transformation_operations = TransformationOperations(
            self,
            self.scene,
            command_service,
            self.selection_service
        )

        self.ui.actionDrawLineByParams.triggered.connect(self.drawing_service.draw_line_by_params)
        self.ui.actionDrawRectByParams.triggered.connect(self.drawing_service.draw_rect_by_params)
        self.ui.actionDrawCircleByParams.triggered.connect(self.drawing_service.draw_ellipse_by_params)
        self.ui.actionDrawCurveByParams.triggered.connect(self.drawing_service.draw_curve_by_params)
        self.ui.actionDrawParametric.triggered.connect(self.drawing_service.draw_parametric)
        self.ui.actionUnion.triggered.connect(self.boolean_operations.perform_union)
        self.ui.actionDifference.triggered.connect(self.boolean_operations.perform_difference)
        self.ui.actionIntersection.triggered.connect(self.boolean_operations.perform_intersection)
        self.ui.actionMirror.triggered.connect(self.transformation_operations.perform_mirror)
        self.ui.actionRotate.triggered.connect(self.transformation_operations.perform_rotate)
        self.ui.actionBuildMesh.triggered.connect(self.build_gmsh_mesh)

        self.ui.graphicsView.viewport().installEventFilter(self)

        # Инициализация параметров
        self.turbulence_params = TurbulenceParams()
        self.boundary_conditions: list[BoundaryConditions] = []
        self.boundary_edges: list[EdgeItem] = []
        self.initial_conditions = InitialConditions()

        # Инициализация UI
        self.init_turbulence_ui()

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

        builder = GmshMeshBuilder(self.grid_spacing)
        builder.build_mesh(self.boundary_edges, dx)

    def init_turbulence_ui(self):
        self.ui.projectTree.itemClicked.connect(self.on_tree_item_clicked)
        self.ui.projectTree.setContextMenuPolicy(Qt.CustomContextMenu)  # <-- Добавить эту строку
        self.ui.projectTree.customContextMenuRequested.connect(self.show_tree_context_menu)
        self.update_project_tree()

    def update_project_tree(self):
        self.ui.projectTree.clear()

        # Модель турбулентности
        turbulence_item = QTreeWidgetItem(['Модель турбулентности'])
        turbulence_item.addChild(QTreeWidgetItem([
            f'{self.turbulence_params.model.value}'
        ]))

        # Начальные условия
        init_item = QTreeWidgetItem(['Начальные условия'])
        init_item.addChild(QTreeWidgetItem([
            f'u: {self.initial_conditions.u} м/с'
        ]))
        init_item.addChild(QTreeWidgetItem([
            f'v: {self.initial_conditions.v} м/с'
        ]))
        init_item.addChild(QTreeWidgetItem([
            f'p: {self.initial_conditions.p} Па'
        ]))

        if self.turbulence_params.model != TurbulenceModel.LAMINAR:
            init_item.addChild(QTreeWidgetItem([
                f'k: {self.initial_conditions.k} м²/с²'
            ]))
            init_item.addChild(QTreeWidgetItem([
                f'omega: {self.initial_conditions.omega}'
            ]))

        # Граничные условия
        bc_item = QTreeWidgetItem(['Граничные условия'])
        for bc in self.boundary_conditions:
            bc_child = QTreeWidgetItem([bc.type.value])
            bc_child.setData(0, Qt.UserRole, bc)
            # bc_child.addChild(QTreeWidgetItem([f'Type: {bc.bc_type}']))

            bc_child.addChild(QTreeWidgetItem([
                f'u: {bc.u} м/с'
            ]))

            bc_child.addChild(QTreeWidgetItem([
                f'v: {bc.v} м/с'
            ]))

            bc_child.addChild(QTreeWidgetItem([
                f'k: {bc.k} м/с'
            ]))

            bc_child.addChild(QTreeWidgetItem([
                f'omega: {bc.omega} м/с'
            ]))

            bc_item.addChild(bc_child)

        self.ui.projectTree.addTopLevelItem(turbulence_item)
        self.ui.projectTree.addTopLevelItem(init_item)
        self.ui.projectTree.addTopLevelItem(bc_item)

    def on_tree_item_clicked(self, item, column):
        parent = item.parent()

        # Для верхнеуровневых элементов
        if not parent:
            if item.text(0) == 'Модель турбулентности':
                self.edit_turbulence_model()
            elif item.text(0) == 'Начальные условия':
                self.edit_initial_conditions()
            elif item.text(0) == 'Граничные условия':
                self.add_boundary_condition()
            return

        # Для дочерних элементов
        parent_text = parent.text(0)

        if parent_text == 'Начальные условия':
            self.edit_initial_conditions()

        elif parent_text == 'Граничные условия':
            self.edit_boundary_condition(item)

    def add_boundary_condition(self):
        selected_edges = self.selection_service.selected_edges
        if not selected_edges:
            QMessageBox.warning(self, "Ошибка", "Выберите ребра (Alt + клик)!")
            return

        dialog = BoundaryConditionsDialog(edges=selected_edges)
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
            color = Qt.red if edge.boundary_conditions.type == BoundaryConditionType.INLET else Qt.blue
            edge.setPen(QPen(color, 3))

    def edit_turbulence_model(self):
        dialog = TurbulenceDialog(self.turbulence_params, self)
        if dialog.exec():
            self.turbulence_params = dialog.get_data()
            self.update_project_tree()

    def edit_initial_conditions(self):
        dialog = InitialConditionsDialog()
        if dialog.exec():
            self.initial_conditions = dialog.get_data()
            self.update_project_tree()

    def edit_boundary_condition(self, item):
        bc = item.data(0, Qt.UserRole)
        dialog = BoundaryConditionsDialog([edge for edge in self.boundary_edges if edge.boundary_conditions == bc])
        if dialog.exec():
            new_bc = dialog.get_data()
            index = self.boundary_conditions.index(bc)
            self.boundary_conditions[index] = new_bc
            self.update_project_tree()
            self.highlight_edges()

    def show_tree_context_menu(self, position):
        item = self.ui.projectTree.itemAt(position)
        menu = QMenu()

        if item and item.text(0) == 'Граничные условия':
            menu.addAction('Добавить условие', self.add_boundary_condition)
        elif item and item.parent() and item.parent().text(0) == 'Граничные условия':
            menu.addAction('Удалить условие', lambda: self.delete_boundary_condition(item))

        menu.exec(self.ui.projectTree.viewport().mapToGlobal(position))

    def delete_boundary_condition(self, item):
        bc = item.data(0, Qt.UserRole)
        self.boundary_conditions.remove(bc)
        for edge in self.boundary_edges:
            if edge.boundary_conditions == bc:
                self.boundary_edges.remove(edge)
        self.update_project_tree()

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
