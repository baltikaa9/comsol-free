from PySide6.QtWidgets import QWidget

from modules.data.src.dialogs.bezier_dialog import BezierDialog
from modules.data.src.dialogs.dialog import Dialog
from modules.data.src.dialogs.ellipse_dialog import EllipseDialog
from modules.data.src.dialogs.line_dialog import LineDialog
from modules.data.src.dialogs.parametric_dialog import ParametricDialog
from modules.data.src.dialogs.rect_dialog import RectDialog


class DialogFactory:
    @staticmethod
    def create_dialog(dialog_type: str, parent: QWidget) -> Dialog | None:
        match dialog_type:
            case 'line':
                return LineDialog(parent)
            case 'rect':
                return RectDialog(parent)
            case 'ellipse':
                return EllipseDialog(parent)
            case 'parametric':
                return ParametricDialog(parent)
            case 'bezier':
                return BezierDialog(parent)
            case _:
                return None
