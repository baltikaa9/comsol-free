from abc import abstractmethod

from PySide6.QtWidgets import QDialog


class Dialog(QDialog):
    @abstractmethod
    def get_data(self) -> dict:
        ...