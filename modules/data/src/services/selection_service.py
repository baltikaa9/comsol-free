from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPen, QColor, QBrush
from PySide6.QtWidgets import QGraphicsItem

from src.widgets.edge_item import EdgeItem
from src.widgets.grid_scene import GridScene


class SelectionService:
    def __init__(self, scene: GridScene):
        self.scene = scene
        self.bool_selection: list[QGraphicsItem] = []
        self.selected_edges: list[EdgeItem] = []  # Храним выбранные рёбра

        self.selected_pen = QPen(Qt.red, 0)
        self.selection_pen = QPen(Qt.blue, 0, Qt.DashLine)
        self.selection_brush = QBrush(QColor(0, 0, 255, 50))
        self.selection_rect = None
        self.last_selection_rect = QRectF()

    def add_edge(self, edge):
        if edge not in self.selected_edges:
            self.selected_edges.append(edge)
            self.highlight_edge(edge)

    def remove_edge(self, edge):
        if edge in self.selected_edges:
            self.selected_edges.remove(edge)

    def clear_edges(self):
        # Восстанавливаем цвета и очищаем список
        for edge in self.selected_edges:
            edge.setPen(QPen(Qt.black))
        self.selected_edges.clear()
        # self.original_colors.clear()

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
            if item.flags() & QGraphicsItem.ItemIsSelectable and not isinstance(item, EdgeItem):
                self.select_item(item)

    def highlight_edge(self, edge):
        color = Qt.blue
        edge.setPen(QPen(color, 0))
