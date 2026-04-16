from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QTextEdit,
    QVBoxLayout,
)


class SSHWorker(QThread):
    new_line = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, ssh_client, config):
        super().__init__()
        self.ssh_client = ssh_client
        self.config = config
        self._output = ""

    def run(self):
        def on_output(line: str):
            self._output += line + "\n"
            self.new_line.emit(line)

        success, output = self.ssh_client.upload_and_execute(
            self.config, on_output=on_output
        )
        self.finished.emit(success, output)

    def stop(self):
        """Останавливает выполнение воркера и дочернего процесса."""
        if self.isRunning():
            self.ssh_client.stop_cli()
            self.quit()
            self.wait()


class SSHResultDialog(QDialog):
    def __init__(self, worker: SSHWorker, parent=None):
        super().__init__(parent)
        self.worker = worker
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

    def reject(self):
        """Переопределяем, чтобы остановить воркер при закрытии."""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
        super().reject()

    def append_line(self, line: str):
        """Добавляет строку в реальном времени."""
        self.output_text.append(line)
        # Автопрокрутка вниз
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def set_final(self, success: bool, output: str):
        """Финальный статус."""
        prefix = "\n\n✅ Успешно!" if success else "\n\n❌ Ошибка!"
        self.output_text.append(prefix)
        self.output_text.append("=" * 50)
