from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QTextEdit,
    QVBoxLayout,
)


class SSHWorker(QThread):
    finished = Signal(bool, str)

    def __init__(self, ssh_client, config):
        super().__init__()
        self.ssh_client = ssh_client
        self.config = config

    def run(self):
        success, output = self.ssh_client.upload_and_execute(self.config)
        self.finished.emit(success, output)


class SSHResultDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Результат SSH операции")
        self.setModal(False)
        self.resize(600, 400)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Текстовое поле для вывода
        self.output_text = QTextEdit()
        self.output_text.setFont(QFont("Consolas", 10))
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def set_output(self, success: bool, output: str):
        prefix = "✅ Успешно!\n\n" if success else "❌ Ошибка!\n\n"
        self.output_text.setText(prefix + output)
