from PySide6.QtCore import QEvent
from PySide6.QtCore import QPointF
from PySide6.QtCore import QRectF
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush
from PySide6.QtGui import QColor
from PySide6.QtGui import QKeyEvent
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QBoxLayout
from PySide6.QtWidgets import QGraphicsEllipseItem
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtWidgets import QGraphicsLineItem
from PySide6.QtWidgets import QGraphicsRectItem
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLineEdit

from modules.data.src.commands.delete_command import DeleteCommand
from modules.data.src.commands.move_command import MoveCommand
from modules.data.src.services.command_service import CommandService
from modules.data.src.services.selection_service import SelectionService
from modules.data.src.widgets.edge_item import EdgeItem
from modules.data.src.widgets.graphics_view import GraphicsView
from modules.data.src.widgets.grid_scene import GridScene


class EventHandler:
    def __init__(
            self,
            main_window,
            scene: GridScene,
            graphics_view: GraphicsView,
            properties_layout: QBoxLayout,
            selection_service: SelectionService,
            command_service: CommandService,
    ):
        self.main_window = main_window
        self.scene = scene
        self.graphics_view = graphics_view
        self.properties_layout = properties_layout
        self.selection_service = selection_service
        self.command_service = command_service

        self.moving_items = False
        self.move_start_pos = QPointF()
        self.move_initial_pos = QPointF()

        self.start_point = None
        self.temp_item = None
        self.curve_points = []
        self.temp_curve_item = None

    def mouse_press(self, event: QMouseEvent) -> bool:
        scene_pos = self.graphics_view.mapToScene(event.position().toPoint())
        self.start_point = scene_pos
        self.selection_service.last_selection_rect = QRectF()

        if event.button() != Qt.MouseButton.LeftButton:
            return False

        item = self.scene.itemAt(scene_pos, self.graphics_view.transform())
        ctrl_pressed = event.modifiers() & Qt.KeyboardModifier.ControlModifier
        alt_pressed = event.modifiers() & Qt.KeyboardModifier.AltModifier
        if item:
            if ctrl_pressed:
                if item not in self.selection_service.bool_selection:
                    self.selection_service.bool_selection.append(item)
                item.setSelected(not item.isSelected())
            elif alt_pressed:
                items = self.graphics_view.items(event.pos())
                for item in items:
                    if isinstance(item, EdgeItem):
                        self.selection_service.select_edge(item)
                        return True
            else:
                self.selection_service.clear_selection()
                self.selection_service.bool_selection = [item]
                item.setSelected(True)
            self.moving_items = True
            self.move_initial_pos = scene_pos
            self.move_start_pos = scene_pos
            self.__update_properties(item)
        else:
            self.selection_service.selection_rect = QGraphicsRectItem()
            self.selection_service.selection_rect.setPen(self.selection_service.selection_pen)
            self.selection_service.selection_brush = QBrush(QColor(0, 0, 255, 50))
            self.selection_service.selection_rect.setBrush(self.selection_service.selection_brush)
            self.scene.addItem(self.selection_service.selection_rect)
        return True

    def mouse_move(self, event: QMouseEvent) -> bool:
        scene_pos = self.graphics_view.mapToScene(event.position().toPoint())
        if self.moving_items:
            selected = self.scene.selectedItems()
            if selected:
                delta = scene_pos - self.move_start_pos
                for item in selected:
                    item.moveBy(delta.x(), delta.y())
                self.move_start_pos = scene_pos
                self.__update_properties(selected[0])
            return True
        elif self.selection_service.selection_rect:
            rect = QRectF(self.start_point, scene_pos).normalized()
            self.selection_service.selection_rect.setRect(rect)
            if rect != self.selection_service.last_selection_rect:
                self.selection_service.update_selection(rect)
                self.selection_service.last_selection_rect = rect
            return True

        current_pos = scene_pos
        rect = QRectF(self.start_point, current_pos).normalized()
        if isinstance(self.temp_item, QGraphicsLineItem):
            self.temp_item.setLine(self.start_point.x(), self.start_point.y(),
                                   current_pos.x(), current_pos.y())
        elif isinstance(self.temp_item, QGraphicsRectItem):
            self.temp_item.setRect(rect)
        elif isinstance(self.temp_item, QGraphicsEllipseItem):
            self.temp_item.setRect(rect)
        return True

    def mouse_release(self, event: QMouseEvent) -> bool:
        if self.selection_service.selection_rect:
            self.scene.removeItem(self.selection_service.selection_rect)
            self.selection_service.selection_rect = None
        if self.moving_items:
            selected = self.scene.selectedItems()
            if selected:
                scene_pos = self.graphics_view.mapToScene(event.position().toPoint())
                delta = scene_pos - self.move_initial_pos
                if delta.x() != 0 or delta.y() != 0:
                    self.command_service.append(MoveCommand(selected, delta))
            self.moving_items = False

        return True

    def event_filter(self, event: QEvent) -> bool:
        if event.type() == QEvent.Type.MouseButtonPress:
            return self.mouse_press(event)
        elif event.type() == QEvent.Type.MouseMove:
            if event.buttons() & Qt.MouseButton.LeftButton:
                return self.mouse_move(event)
            return False
        elif event.type() == QEvent.Type.MouseButtonRelease:
            if event.button() == Qt.MouseButton.MiddleButton:
                return False
            return self.mouse_release(event)
        return False

    def key_press_event(self, event: QKeyEvent):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_A:
            self.selection_service.select_all()
        elif event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Z:
            self.command_service.undo()
            self.selection_service.clear_selection()
        elif event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Y:
            self.command_service.redo()
            self.selection_service.clear_selection()
        elif event.key() == Qt.Key.Key_Delete:
            selected = self.scene.selectedItems()
            if selected:
                self.command_service.execute(DeleteCommand(self.scene, selected))

    def __update_properties(self, item: QGraphicsItem):
        # Очистить layout
        while self.properties_layout.count():
            child = self.properties_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Пример: добавить поля для позиции
        x_edit = QLineEdit(str(item.x()), readOnly=True)
        y_edit = QLineEdit(str(item.y()), readOnly=True)
        self.properties_layout.addWidget(QLabel('X:'))
        self.properties_layout.addWidget(x_edit)
        self.properties_layout.addWidget(QLabel('Y:'))
        self.properties_layout.addWidget(y_edit)

    # def handle_item_selected(self, item):
    #     if isinstance(item, (QGraphicsPathItem, QGraphicsLineItem)):
    #         self.assign_boundary_condition(item)
    #
    # def assign_boundary_condition(self, geometry_item):
    #     dialog = BoundaryConditionsDialog(self.main_window.turbulence_params.model)
    #     if dialog.exec():
    #         bc = BoundaryConditions(
    #             name=f'BC_{len(self.main_window.boundary_conditions) + 1}',
    #             bc_type=dialog.get_bc_type(),
    #             values=dialog.get_values(),
    #         )
    #         geometry_item.setData(0, bc)  # Привязываем BC к геометрии
    #         self.main_window.boundary_conditions.append(bc)
    #         self.main_window.update_project_tree()
