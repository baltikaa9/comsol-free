from PySide6.QtCore import QLineF
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtWidgets import QGraphicsLineItem

from modules.data.src.widgets.edge_item import LineEdgeItem


class LineItem(QGraphicsLineItem):
    def __init__(self, line: QLineF):
        super().__init__(line)
        self.edges: list = []
        self.generate_edges()

    def generate_edges(self):
        line = self.line()
        self.edges = [LineEdgeItem(line.p1(), line.p2())]
        self.edges[0].setParentItem(self)
        self.edges[0].setFlag(QGraphicsItem.ItemIsSelectable, True)