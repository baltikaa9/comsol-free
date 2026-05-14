from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
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

        # === Название конфигурации ===
        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Название:"))
        self.name_edit = QLineEdit(self.config.name)
        self.name_edit.setPlaceholderText("Например: Рабочий сервер")
        name_row.addWidget(self.name_edit)
        layout.addLayout(name_row)

        # === Подключение ===
        conn_row = QHBoxLayout()
        conn_row.addWidget(QLabel("Подключение:"))
        self.conn_edit = QLineEdit(self._get_connection_string())
        self.conn_edit.setPlaceholderText("user@host:port")
        conn_row.addWidget(self.conn_edit)
        layout.addLayout(conn_row)

        # === Аутентификация ===
        auth_row = QHBoxLayout()
        auth_row.addWidget(QLabel("Аутентификация:"))
        self.auth_combo = QComboBox()
        self.auth_combo.addItems(["SSH ключ", "Пароль"])
        self.auth_combo.setCurrentIndex(0 if not self.config.password else 1)
        self.auth_combo.currentIndexChanged.connect(self._on_auth_change)
        auth_row.addWidget(self.auth_combo)
        layout.addLayout(auth_row)

        # Поле для ключа
        key_row = QHBoxLayout()
        key_row.addWidget(QLabel("Ключ:"))
        self.key_edit = QLineEdit(self.config.key_path)
        self.key_edit.setPlaceholderText("Путь к SSH ключу")
        key_row.addWidget(self.key_edit)
        btn_key = QPushButton("Обзор...")
        btn_key.clicked.connect(self._browse_key)
        key_row.addWidget(btn_key)
        self.key_widget = QWidget()
        self.key_widget.setLayout(key_row)
        layout.addWidget(self.key_widget)

        # Поле для пароля
        pass_row = QHBoxLayout()
        pass_row.addWidget(QLabel("Пароль:"))
        self.pass_edit = QLineEdit(self.config.password)
        self.pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_edit.setPlaceholderText("Пароль SSH")
        pass_row.addWidget(self.pass_edit)
        self.pass_widget = QWidget()
        self.pass_widget.setLayout(pass_row)
        layout.addWidget(self.pass_widget)

        # Скрываем ненужные поля
        self._on_auth_change(self.auth_combo.currentIndex())

        # === Папка с CUDA-проектом ===
        project_row = QHBoxLayout()
        project_row.addWidget(QLabel("CUDA-проект:"))
        self.project_path_edit = QLineEdit(self.config.project_path)
        self.project_path_edit.setPlaceholderText(
            "Путь к папке с исходниками (например, Project_test)"
        )
        project_row.addWidget(self.project_path_edit)
        btn_browse = QPushButton("Обзор...")
        btn_browse.clicked.connect(self._browse_project_path)
        project_row.addWidget(btn_browse)
        layout.addLayout(project_row)

        # === Удаленная директория ===
        remote_row = QHBoxLayout()
        remote_row.addWidget(QLabel("Удаленная папка:"))
        self.remote_dir_edit = QLineEdit(self.config.remote_dir)
        self.remote_dir_edit.setPlaceholderText("Базовая директория на сервере")
        remote_row.addWidget(self.remote_dir_edit)
        layout.addLayout(remote_row)

        # === Команда для выполнения ===
        cmd_row = QHBoxLayout()
        cmd_row.addWidget(QLabel("Команда:"))
        self.run_command_edit = QLineEdit(self.config.run_command)
        self.run_command_edit.setPlaceholderText(
            "Оставьте пустым для compile.ini или авто-компиляции"
        )
        cmd_row.addWidget(self.run_command_edit)
        layout.addLayout(cmd_row)

        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_auth_change(self, index: int):
        """Переключение между ключом и паролем"""
        self.key_widget.setVisible(index == 0)
        self.pass_widget.setVisible(index == 1)

    def _get_connection_string(self) -> str:
        """Формирует строку user@host:port"""
        return f"{self.config.user}@{self.config.host}:{self.config.port}"

    def _parse_connection_string(self, conn_str: str) -> tuple[str, str, int]:
        """Парсит строку user@host:port"""
        # Формат: user@host:port или user@host
        if "@" in conn_str:
            user, host_part = conn_str.split("@", 1)
        else:
            user = self.config.user
            host_part = conn_str

        if ":" in host_part:
            host, port_str = host_part.split(":", 1)
            port = int(port_str)
        else:
            host = host_part
            port = self.config.port

        return user, host, port

    def _browse_key(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите SSH ключ", self.config.key_path or "", "All Files (*)"
        )
        if path:
            self.key_edit.setText(path)

    def _browse_project_path(self):
        path = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку с CUDA-проектом",
            str(
                Path(self.config.project_path).parent
                if self.config.project_path
                else ""
            ),
        )
        if path:
            self.project_path_edit.setText(path)

    def get_config(self) -> SSHConfig:
        conn_str = self.conn_edit.text().strip()
        user, host, port = self._parse_connection_string(conn_str)
        use_key = self.auth_combo.currentIndex() == 0
        return SSHConfig(
            name=self.name_edit.text().strip() or "Без имени",
            user=user,
            host=host,
            port=port,
            key_path=self.key_edit.text().strip() if use_key else "",
            password=self.pass_edit.text().strip() if not use_key else "",
            project_path=self.project_path_edit.text().strip(),
            remote_dir=self.remote_dir_edit.text().strip(),
            run_command=self.run_command_edit.text().strip(),
        )
