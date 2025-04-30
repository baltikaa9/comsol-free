import triangle
from PySide6.QtCore import QEvent
from PySide6.QtGui import QKeyEvent, QPainterPath
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QApplication, QPushButton, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsLineItem
from PySide6.QtWidgets import QGraphicsView
from PySide6.QtWidgets import QMainWindow
from matplotlib import pyplot as plt

from modules.data.src.event_handler import EventHandler
from modules.data.src.grid_scene import GridScene
from modules.data.src.operations.boolean_operations import BooleanOperations
from modules.data.src.operations.transformation_operations import TransformationOperations
from modules.data.src.services.command_service import CommandService
from modules.data.src.services.drawing_service import DrawingService
from modules.data.src.services.selection_service import SelectionService
from modules.data.src.ui.template import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.debug_button = QPushButton("Вывести QPainterPath", self)
        self.debug_button.move(10, 10)  # Положение на окне
        self.debug_button.clicked.connect(self.print_selected_path)
        self.debug_button.show()

        self.scene = GridScene(spacing=50)
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)
        self.ui.graphicsView.setScene(self.scene)
        self.ui.graphicsView.setRenderHints(QPainter.Antialiasing)
        self.grid_spacing = 1
        self.ui.graphicsView.scale(self.grid_spacing, -self.grid_spacing)
        self.ui.graphicsView.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        selection_service = SelectionService(self.scene)
        command_service = CommandService()
        self.event_handler = EventHandler(
            self.scene,
            self.ui.graphicsView,
            selection_service,
            command_service
        )
        self.drawing_service = DrawingService(self, self.scene, command_service, selection_service)
        self.boolean_operations = BooleanOperations(
            self,
            self.scene,
            command_service,
            self.drawing_service,
            selection_service
        )
        self.transformation_operations = TransformationOperations(
            self,
            self.scene,
            command_service,
            selection_service
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

        self.ui.graphicsView.viewport().installEventFilter(self)

    def eventFilter(self, obj, event: QEvent):
        if obj is self.ui.graphicsView.viewport():
            return self.event_handler.event_filter(event)

        return super().eventFilter(obj, event)

    def keyPressEvent(self, event: QKeyEvent):
        self.event_handler.key_press_event(event)

    def print_selected_path(self):
        selected = self.scene.selectedItems()
        if not selected:
            print("Нет выбранных фигур.")
            return

        item = selected[0]
        if hasattr(item, 'path'):
            path: QPainterPath = item.path()
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
            print(f"Тип {type(item)} не поддерживается.")
            return

        polygon = path.toFillPolygon()  # возвращает QPolygonF
        points = [(p.x(), p.y()) for p in polygon]

        # xs, ys = zip(*points)
        # plt.plot(xs, ys, 'o-')
        # plt.show()

        print(points)

        A = dict(vertices=points)

        # 'p' — построить по полигону, 'q' — качество, 'a' — максимальная площадь
        B = triangle.triangulate(A, 'pqa0.1')
        B = triangle.triangulate(A, 'pq')

        plt.triplot(B['vertices'][:, 0], B['vertices'][:, 1])
        plt.show()

        # print("QPainterPath элементы:")
        # for i in range(path.elementCount()):
        #     e = path.elementAt(i)
        #     print(f"  [{i}] x={e.x}, y={e.y}")

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
