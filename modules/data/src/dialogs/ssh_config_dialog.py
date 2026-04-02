from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)
from src.services.ssh_client import SSHConfig


class SSHConfigDialog(QDialog):
    def __init__(self, config: SSHConfig | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки SSH подключения")
        self.setModal(True)
        self.setMinimumWidth(500)

        self.config = config or SSHConfig()

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Форма с сеткой для лучшего контроля
        grid = QGridLayout()
        grid.setSpacing(10)

        # Пользователь
        grid.addWidget(QLineEdit("Пользователь:"), 0, 0)
        self.user_edit = QLineEdit(self.config.user)
        self.user_edit.setMinimumWidth(300)
        grid.addWidget(self.user_edit, 0, 1)

        # Хост
        grid.addWidget(QLineEdit("Хост:"), 1, 0)
        self.host_edit = QLineEdit(self.config.host)
        grid.addWidget(self.host_edit, 1, 1)

        # Порт
        grid.addWidget(QLineEdit("Порт:"), 2, 0)
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(self.config.port)
        self.port_spin.setMinimumWidth(300)
        grid.addWidget(self.port_spin, 2, 1)

        # Путь к ключу
        grid.addWidget(QLineEdit("Ключ:"), 3, 0)
        key_layout = QHBoxLayout()
        self.key_edit = QLineEdit(self.config.key_path)
        self.key_edit.setMinimumWidth(300)
        key_layout.addWidget(self.key_edit)
        browse_button = QPushButton("Обзор...")
        browse_button.clicked.connect(self._browse_key)
        key_layout.addWidget(browse_button)
        grid.addLayout(key_layout, 3, 1)

        # Удаленная директория
        grid.addWidget(QLineEdit("Удаленная папка:"), 4, 0)
        self.remote_dir_edit = QLineEdit(self.config.remote_dir)
        grid.addWidget(self.remote_dir_edit, 4, 1)

        layout.addLayout(grid)

        # Кнопки OK/Cancel
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _browse_key(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите SSH ключ", str(self.config.key_path or ""), "All Files (*)"
        )
        if file_path:
            self.key_edit.setText(file_path)

    def get_config(self) -> SSHConfig:
        return SSHConfig(
            user=self.user_edit.text(),
            host=self.host_edit.text(),
            port=self.port_spin.value(),
            key_path=self.key_edit.text(),
            remote_dir=self.remote_dir_edit.text(),
        )
