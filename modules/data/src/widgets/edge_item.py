from PySide6.QtWidgets import QGraphicsLineItem

class EdgeItem(QGraphicsLineItem):
    __id_counter = 0  # Счетчик для генерации уникальных ID

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = EdgeItem.__id_counter
        EdgeItem.__id_counter += 1
