from PySide6.QtGui import QPainterPath
from PySide6.QtWidgets import QGraphicsItem, QGraphicsPathItem
from src.widgets.edge_item import EdgeItem


class BooleanShapeItem(QGraphicsPathItem):
    def __init__(self, path: QPainterPath, p1, p2, op_type: str = "union"):
        super().__init__(path)
        self.edges: list[EdgeItem] = []
        self.op_type = op_type  # 'union', 'difference', 'intersection'
        self.generate_edges(p1, p2)

    @classmethod
    def from_path(cls, path: QPainterPath, edges_data: list) -> "BooleanShapeItem":
        """Восстановление из сохранённого пути без исходных фигур."""
        instance = cls.__new__(cls)
        QGraphicsPathItem.__init__(instance, path)
        instance.op_type = "restored"
        instance.edges = []
    
        for ed in edges_data:
            edge_path = QPainterPath()
            for elem in ed["path"]:
                if elem["t"] == 0:
                    edge_path.moveTo(elem["x"], elem["y"])
                elif elem["t"] == 1:
                    edge_path.lineTo(elem["x"], elem["y"])
    
            edge = EdgeItem(edge_path)
            edge.id = ed["id"]
            edge.setParentItem(instance)
            edge.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
            print(f"[restore] edge {ed['id']} boundingRect: {edge.boundingRect()}")
            instance.edges.append(edge)
    
        return instance

    def generate_edges(self, p1, p2):
        self.edges = p1.edges.copy() + p2.edges.copy()
        for edge in self.edges:
            edge.setParentItem(self)
            edge.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        

    def __repr__(self):
        return f"{self.__class__.__name__}({[edge.path() for edge in self.edges]})"
