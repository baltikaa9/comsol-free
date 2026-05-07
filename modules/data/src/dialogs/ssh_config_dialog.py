import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)
from src.services.ssh_client import SSHConfig


class SSHConfigDialog(QDialog):
    def __init__(self, config: SSHConfig | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки SSH подключения")
        self.setModal(True)
        self.setMinimumWidth(600)

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
        conn_group = QGroupBox("Подключение")
        conn_layout = QVBoxLayout()

        row = QHBoxLayout()
        row.addWidget(QLabel("Пользователь:"))
        self.user_edit = QLineEdit(self.config.user)
        row.addWidget(self.user_edit)
        conn_layout.addLayout(row)

        row = QHBoxLayout()
        row.addWidget(QLabel("Хост:"))
        self.host_edit = QLineEdit(self.config.host)
        row.addWidget(self.host_edit)
        conn_layout.addLayout(row)

        row = QHBoxLayout()
        row.addWidget(QLabel("Порт:"))
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(self.config.port)
        row.addWidget(self.port_spin)
        row.addStretch()
        conn_layout.addLayout(row)

        row = QHBoxLayout()
        row.addWidget(QLabel("Ключ:"))
        self.key_edit = QLineEdit(self.config.key_path)
        row.addWidget(self.key_edit)
        btn = QPushButton("Обзор...")
        btn.clicked.connect(self._browse_key)
        row.addWidget(btn)
        conn_layout.addLayout(row)

        row = QHBoxLayout()
        row.addWidget(QLabel("Пароль:"))
        self.password_edit = QLineEdit(self.config.password)
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("Оставьте пустым если есть ключ")
        row.addWidget(self.password_edit)
        conn_layout.addLayout(row)

        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)

        # === Файлы ===
        file_group = QGroupBox("Файлы")
        file_layout = QVBoxLayout()

        row = QHBoxLayout()
        row.addWidget(QLabel("Data-файл:"))
        self.local_file_edit = QLineEdit(self.config.local_file)
        self.local_file_edit.setPlaceholderText("structured_mesh.json")
        row.addWidget(self.local_file_edit)
        btn = QPushButton("Обзор...")
        btn.clicked.connect(self._browse_data_file)
        row.addWidget(btn)
        file_layout.addLayout(row)

        row = QHBoxLayout()
        row.addWidget(QLabel("Удаленная папка:"))
        self.remote_dir_edit = QLineEdit(self.config.remote_dir)
        row.addWidget(self.remote_dir_edit)
        file_layout.addLayout(row)

        row = QHBoxLayout()
        row.addWidget(QLabel("Папка на сервере:"))
        self.project_folder_edit = QLineEdit(self.config.project_folder)
        self.project_folder_edit.setPlaceholderText("test123 (будет создана)")
        row.addWidget(self.project_folder_edit)
        file_layout.addLayout(row)

        row = QHBoxLayout()
        row.addWidget(QLabel("Папка проекта:"))
        self.project_path_edit = QLineEdit(self.config.project_path)
        self.project_path_edit.setPlaceholderText("Путь к CUDA-проекту")
        row.addWidget(self.project_path_edit)
        btn = QPushButton("Обзор...")
        btn.clicked.connect(self._browse_project_path)
        row.addWidget(btn)
        file_layout.addLayout(row)

        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # === Исполняемый файл ===
        exe_group = QGroupBox("Исполняемый файл (опционально)")
        exe_layout = QVBoxLayout()

        row = QHBoxLayout()
        row.addWidget(QLabel("Локальный exe:"))
        self.local_exe_edit = QLineEdit(self.config.local_exe)
        self.local_exe_edit.setPlaceholderText("Загрузится на сервер")
        row.addWidget(self.local_exe_edit)
        btn = QPushButton("Обзор...")
        btn.clicked.connect(self._browse_local_exe)
        row.addWidget(btn)
        exe_layout.addLayout(row)

        row = QHBoxLayout()
        row.addWidget(QLabel("Команда:"))
        self.run_command_edit = QLineEdit(self.config.run_command)
        self.run_command_edit.setPlaceholderText("по умолчанию: nvcc && ./shock.out")
        row.addWidget(self.run_command_edit)
        exe_layout.addLayout(row)

        exe_group.setLayout(exe_layout)
        layout.addWidget(exe_group)

        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _browse_key(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите SSH ключ", self.config.key_path or "", "All Files (*)"
        )
        if path:
            self.key_edit.setText(path)

    def _browse_data_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл для загрузки",
            str(Path(self.config.local_file).parent if self.config.local_file else ""),
            "JSON Files (*.json);;All Files (*)",
        )
        if path:
            self.local_file_edit.setText(path)

    def _browse_project_path(self):
        path = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку проекта",
            str(
                Path(self.config.project_path).parent
                if self.config.project_path
                else ""
            ),
        )
        if path:
            self.project_path_edit.setText(path)

    def _browse_local_exe(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите исполняемый файл",
            str(Path(self.config.local_exe).parent if self.config.local_exe else ""),
            "All Files (*)",
        )
        if path:
            self.local_exe_edit.setText(path)

    def get_config(self) -> SSHConfig:
        return SSHConfig(
            name=self.name_edit.text().strip() or "Без имени",
            user=self.user_edit.text(),
            host=self.host_edit.text(),
            port=self.port_spin.value(),
            key_path=self.key_edit.text(),
            password=self.password_edit.text(),
            local_file=self.local_file_edit.text(),
            remote_dir=self.remote_dir_edit.text(),
            project_folder=self.project_folder_edit.text(),
            project_path=self.project_path_edit.text(),
            local_exe=self.local_exe_edit.text(),
            run_command=self.run_command_edit.text(),
        )