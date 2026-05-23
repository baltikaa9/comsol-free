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
        instance = cls.__new__(cls)
        QGraphicsPathItem.__init__(instance, path)
        instance.op_type = "restored"
        instance.edges = []
    
        for ed in edges_data:
            edge_path = QPainterPath()
            elems = ed["path"]
            i = 0
            while i < len(elems):
                elem = elems[i]
                t = elem["t"]
    
                if t == 0:  # MoveTo
                    edge_path.moveTo(elem["x"], elem["y"])
                    i += 1
                elif t == 1:  # LineTo
                    edge_path.lineTo(elem["x"], elem["y"])
                    i += 1
                elif t == 2:  # CurveTo — Qt хранит три отдельных элемента: ctrl1, ctrl2, end
                    # Следующие два элемента должны быть CurveToData (t==3)
                    if i + 2 < len(elems) and elems[i+1]["t"] == 3 and elems[i+2]["t"] == 3:
                        edge_path.cubicTo(
                            elem["x"],        elem["y"],        # ctrl1
                            elems[i+1]["x"],  elems[i+1]["y"],  # ctrl2
                            elems[i+2]["x"],  elems[i+2]["y"],  # end
                        )
                        i += 3
                    else:
                        i += 1  # повреждённые данные — пропускаем
                else:
                    i += 1  # CurveToData (t==3) без предшествующего CurveTo — пропускаем
    
            edge = EdgeItem(edge_path)
            edge.id = ed["id"]
            edge.setParentItem(instance)
            edge.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
            instance.edges.append(edge)
    
        return instance

    def generate_edges(self, p1, p2):
        self.edges = p1.edges.copy() + p2.edges.copy()
        for edge in self.edges:
            edge.setParentItem(self)
            edge.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        

    def __repr__(self):
        return f"{self.__class__.__name__}({[edge.path() for edge in self.edges]})"
