from PySide6.QtCore import QPointF, QEvent
from PySide6.QtGui import QPainter, QPainterPath, QTransform, QKeyEvent
from PySide6.QtWidgets import (QApplication, QMainWindow, QGraphicsLineItem, QGraphicsEllipseItem,
                               QGraphicsRectItem, QGraphicsView, QGraphicsPathItem, QInputDialog,
                               QGraphicsItem, QMessageBox)

from modules.data.src.commands.add_command import AddCommand
from modules.data.src.commands.delete_command import DeleteCommand
from modules.data.src.commands.rotate_command import RotateCommand
from modules.data.src.editable_bezier import EditableBezierCurveItem
from modules.data.src.event_handler import EventHandler
from modules.data.src.grid_scene import GridScene
from modules.data.src.services.command_service import CommandService
from modules.data.src.services.drawing_service import DrawingService
from modules.data.src.services.selection_service import SelectionService
from modules.data.src.ui.template import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.scene = GridScene(spacing=50)
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)
        self.ui.graphicsView.setScene(self.scene)
        self.ui.graphicsView.setRenderHints(QPainter.Antialiasing)
        self.grid_spacing = 1
        self.ui.graphicsView.scale(self.grid_spacing, -self.grid_spacing)
        self.ui.graphicsView.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.selection_service = SelectionService(self.scene)
        self.command_service = CommandService()
        self.event_handler = EventHandler(self.scene, self.ui.graphicsView, self.selection_service, self.command_service)
        self.drawing_service = DrawingService(self.scene, self, self.command_service, self.selection_service)

        self.ui.actionDrawLineByParams.triggered.connect(self.drawing_service.draw_line_by_params)
        self.ui.actionDrawRectByParams.triggered.connect(self.drawing_service.draw_rect_by_params)
        self.ui.actionDrawCircleByParams.triggered.connect(self.drawing_service.draw_ellipse_by_params)
        self.ui.actionDrawCurveByParams.triggered.connect(self.drawing_service.draw_curve_by_params)
        self.ui.actionDrawParametric.triggered.connect(self.drawing_service.draw_parametric)
        self.ui.actionUnion.triggered.connect(self.perform_union)
        self.ui.actionDifference.triggered.connect(self.perform_difference)
        self.ui.actionIntersection.triggered.connect(self.perform_intersection)
        self.ui.actionMirror.triggered.connect(self.perform_mirror)
        self.ui.actionRotate.triggered.connect(self.perform_rotate)

        self.ui.graphicsView.viewport().installEventFilter(self)

    def eventFilter(self, obj, event: QEvent):
        if obj is self.ui.graphicsView.viewport():
            return self.event_handler.event_filter(event)

        return super().eventFilter(obj, event)

    def keyPressEvent(self, event: QKeyEvent):
        self.event_handler.key_press_event(event)

    def perform_union(self):
        self.boolean_operation('union')

    def perform_difference(self):
        self.boolean_operation('difference')

    def perform_intersection(self):
        self.boolean_operation('intersection')

    def perform_mirror(self):
        selected = self.scene.selectedItems()
        if len(selected) != 1:
            print(f'Выберите одну фигуру для отражения! {len(selected)}')
            return

        item = selected[0]
        axis, ok = QInputDialog.getItem(
            self, 'Выбор оси отражения',
            'Отразить по оси:',
            ['По горизонтали (X)', 'По вертикали (Y)', 'По диагонали (XY)'],
            0, False
        )
        if not ok:
            return

        if axis == 'По горизонтали (X)':
            transform = QTransform().scale(1, -1)
        elif axis == 'По вертикали (Y)':
            transform = QTransform().scale(-1, 1)
        elif axis == 'По диагонали (XY)':
            transform = QTransform().scale(-1, -1)
        else:
            return

        pen = item.pen()

        if isinstance(item, QGraphicsLineItem):
            line = item.line()
            new_line = transform.map(line)
            new_item = QGraphicsLineItem(new_line)
        elif isinstance(item, QGraphicsRectItem):
            rect = item.rect()
            new_rect = transform.mapRect(rect)
            new_item = QGraphicsRectItem(new_rect)
        elif isinstance(item, QGraphicsEllipseItem):
            rect = item.rect()
            new_rect = transform.mapRect(rect)
            new_item = QGraphicsEllipseItem(new_rect)
        elif isinstance(item, QGraphicsPathItem):
            path = item.path()
            new_path = transform.map(path)
            new_item = QGraphicsPathItem(new_path)
        elif isinstance(item, EditableBezierCurveItem):
            points = item.get_control_points()
            new_points = [transform.map(p) for p in points]
            new_item = EditableBezierCurveItem(new_points, pen=pen, scene=self.scene)
        else:
            print(f'Тип фигуры не поддерживается для отражения: {type(item)}')
            return

        new_item.setPen(pen)
        new_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.command_service.execute(AddCommand(self.scene, new_item))
        self.selection_service.select_item(new_item)

    def _item_to_scene_path(self, item):
        """
        Преобразует любой поддерживаемый QGraphicsItem
        в замкнутый QPainterPath в координатах сцены.
        """
        # 1) Берём локальный path
        if isinstance(item, QGraphicsPathItem):
            path = item.path()
        elif isinstance(item, QGraphicsRectItem):
            path = QPainterPath()
            path.addRect(item.rect())
        elif isinstance(item, QGraphicsEllipseItem):
            path = QPainterPath()
            path.addEllipse(item.rect())
        elif isinstance(item, QGraphicsLineItem):
            path = QPainterPath()
            line = item.line()
            path.moveTo(line.p1())
            path.lineTo(line.p2())
        else:
            return None

        # 2) Замыкаем, если надо
        if not path.isEmpty():
            # первая точка
            e0 = path.elementAt(0)
            start = QPointF(e0.x, e0.y)
            end = path.currentPosition()
            if start != end:
                path.closeSubpath()

        # 3) Преобразуем в координаты сцены
        transform = item.sceneTransform()
        return transform.map(path)

    def boolean_operation(self, op_type: str):
        sel = self.selection_service.bool_selection
        if len(sel) != 2:
            QMessageBox.warning(self, 'Ошибка',
                                'Выберите сначала первую фигуру, потом вторую с зажатым Ctrl!')
            return

        p1 = self._item_to_scene_path(sel[0])
        p2 = self._item_to_scene_path(sel[1])

        if p1 is None or p2 is None:
            QMessageBox.warning(self, 'Ошибка',
                                'Булевы операции поддерживаются только для линий, прямоугольников, эллипсов и путей.')
            return

        if op_type == 'union':
            result = p1.united(p2)
        elif op_type == 'difference':
            result = p1.subtracted(p2)
        else:  # 'intersection'
            result = p1.intersected(p2)

        new_item = QGraphicsPathItem(result)
        new_item.setPen(self.drawing_service.default_pen)
        new_item.setFlag(QGraphicsPathItem.ItemIsSelectable, True)
        self.command_service.execute(AddCommand(self.scene, new_item))

        self.command_service.execute(DeleteCommand(self.scene, sel))

        self.scene.clearSelection()
        new_item.setSelected(True)

        sel.clear()

    def perform_rotate(self):
        sel = self.selection_service.bool_selection
        # Должна быть ровно одна фигура
        if len(sel) != 1:
            QMessageBox.warning(
                self, 'Ошибка',
                'Для поворота выберите ровно одну фигуру (обычный клик).'
            )
            return

        item = sel[0]

        # Спрашиваем угол в градусах
        angle, ok = QInputDialog.getDouble(
            self, 'Поворот', 'Угол поворота (градусы):',
            0.0,  # начальное значение
            -3600.0,  # мин
            3600.0,  # макс
            1  # шаг
        )
        if not ok:
            return

        # Определяем точку поворота — центр boundingRect()
        center = item.sceneBoundingRect().center()
        item.setTransformOriginPoint(center)

        self.command_service.execute(RotateCommand(item, angle))


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()