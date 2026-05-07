from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QListWidget,
    QPushButton, QDialogButtonBox, QMessageBox, QLabel
)
from PySide6.QtCore import Qt

from src.services.ssh_client import SSHConfig, SSHConfigManager
from src.dialogs.ssh_config_dialog import SSHConfigDialog  # твой существующий


class SSHSettingsDialog(QDialog):
    """
    Диалог управления SSH конфигурациями.
    Слева — список, справа — кнопки Edit/Add/Copy/Remove.
    Редактирование через существующий SSHConfigDialog.
    """

    def __init__(self, manager: SSHConfigManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.setWindowTitle("Конфигурации SSH")
        self.setMinimumSize(400, 350)
        self._build_ui()
        self._refresh_list()
        if self.config_list.count() > 0:
            self.config_list.setCurrentRow(0)

    def _build_ui(self):
        root = QHBoxLayout(self)

        # ── Левая колонка: список ──────────────────────────────────────────
        left = QVBoxLayout()
        left.addWidget(QLabel("Конфигурации:"))

        self.config_list = QListWidget()
        self.config_list.setMinimumWidth(200)
        self.config_list.itemDoubleClicked.connect(self._edit_config)
        left.addWidget(self.config_list)

        root.addLayout(left)

        # ── Правая колонка: кнопки ─────────────────────────────────────────
        right = QVBoxLayout()
        right.setAlignment(Qt.AlignTop)

        self.btn_add    = QPushButton("Добавить...")
        self.btn_edit   = QPushButton("Изменить...")
        self.btn_copy   = QPushButton("Копировать")
        self.btn_remove = QPushButton("Удалить")

        for btn in (self.btn_add, self.btn_edit, self.btn_copy, self.btn_remove):
            btn.setFixedWidth(120)
            right.addWidget(btn)

        right.addStretch()

        # OK / Cancel
        self.btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.btn_box.accepted.connect(self.accept)
        self.btn_box.rejected.connect(self.reject)
        right.addWidget(self.btn_box)

        root.addLayout(right)

        # ── Сигналы ────────────────────────────────────────────────────────
        self.btn_add.clicked.connect(self._add_config)
        self.btn_edit.clicked.connect(self._edit_config)
        self.btn_copy.clicked.connect(self._copy_config)
        self.btn_remove.clicked.connect(self._remove_config)

    def _refresh_list(self, select_name: str = None):
        self.config_list.clear()
        for cfg in self.manager.configs:
            self.config_list.addItem(cfg.name)
        if select_name:
            items = self.config_list.findItems(select_name, Qt.MatchExactly)
            if items:
                self.config_list.setCurrentItem(items[0])
        elif self.config_list.count() > 0:
            self.config_list.setCurrentRow(0)

    def _current_config(self) -> SSHConfig | None:
        row = self.config_list.currentRow()
        if 0 <= row < len(self.manager.configs):
            return self.manager.configs[row]
        return None

    def _add_config(self):
        dlg = SSHConfigDialog(parent=self)
        if dlg.exec() == QDialog.Accepted:
            cfg = dlg.get_config()
            if not cfg.name:
                cfg.name = f"Конфигурация {len(self.manager.configs) + 1}"
            self.manager.add_config(cfg)
            self._refresh_list(select_name=cfg.name)

    def _edit_config(self):
        cfg = self._current_config()
        if not cfg:
            return
        dlg = SSHConfigDialog(config=cfg, parent=self)
        if dlg.exec() == QDialog.Accepted:
            updated = dlg.get_config()
            self.manager.update_config(cfg.name, updated)
            self._refresh_list(select_name=updated.name)

    def _copy_config(self):
        cfg = self._current_config()
        if not cfg:
            return
        copy = SSHConfig(**cfg.to_dict())
        copy.name = f"{cfg.name} (копия)"
        self.manager.add_config(copy)
        self._refresh_list(select_name=copy.name)

    def _remove_config(self):
        cfg = self._current_config()
        if not cfg:
            return
        if len(self.manager.configs) == 1:
            QMessageBox.warning(self, "Удаление", "Нельзя удалить последнюю конфигурацию.")
            return
        reply = QMessageBox.question(
            self, "Удалить?", f"Удалить конфигурацию «{cfg.name}»?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.manager.remove_config(cfg.name)
            self._refresh_list()

    def selected_config(self) -> SSHConfig | None:
        """Возвращает выбранную конфигурацию (для использования при запуске)."""
        return self._current_config()