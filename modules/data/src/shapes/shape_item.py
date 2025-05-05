from abc import ABC
from abc import abstractmethod


class ShapeItem(ABC):
    @abstractmethod
    def generate_edges(self):
        """Генерирует рёбра/сегменты фигуры"""
        pass