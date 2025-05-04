from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPen, QColor, QBrush
from PySide6.QtWidgets import QGraphicsItem

from modules.data.src.widgets.edge_item import EdgeItem
from modules.data.src.widgets.grid_scene import GridScene


class SelectionService:
    def __init__(self, scene: GridScene):
        self.bool_selection: list[QGraphicsItem] = []
        self.selected_edges: list[EdgeItem] = []  # Храним выбранные рёбра
        self.scene = scene

        self.selected_pen = QPen(Qt.red, 0)
        self.selection_pen = QPen(Qt.blue, 0, Qt.DashLine)
        self.selection_brush = QBrush(QColor(0, 0, 255, 50))
        self.selection_rect = None
        self.last_selection_rect = QRectF()

    def clear_and_select_item(self, item):
        self.clear_selection()
        if not isinstance(item, EdgeItem):
            item.setSelected(True)
            self.bool_selection.append(item)

    def select_item(self, item):
        if not isinstance(item, EdgeItem):
            item.setSelected(True)
            self.bool_selection.append(item)

    def clear_selection(self):
        self.scene.clearSelection()
        self.bool_selection.clear()

    def update_selection(self, selection_rect):
        self.clear_selection()
        for item in self.scene.items():
            if item.flags() & QGraphicsItem.ItemIsSelectable:
                if selection_rect.intersects(item.sceneBoundingRect()):
                    self.select_item(item)

    def select_all(self):
        self.clear_selection()
        for item in self.scene.items():
            if item.flags() & QGraphicsItem.ItemIsSelectable:
                self.select_item(item)

    def select_edge(self, edge: QGraphicsItem):
        # Снимаем выделение с других рёбер
        for e in self.selected_edges:
            e.setSelected(False)
        self.selected_edges = [edge]
        edge.setSelected(True)

    def clear_edge_selection(self):
        for edge in self.selected_edges:
            edge.setSelected(False)
        self.selected_edges = []
