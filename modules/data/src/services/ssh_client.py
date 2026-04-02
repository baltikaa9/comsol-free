import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SSHConfig:
    user: str = ""
    host: str = ""
    port: int = 0
    key_path: str = ""
    remote_dir: str = "/home/bitrix/"

    def __post_init__(self):
        if not self.key_path:
            self.key_path = str(Path.home() / ".ssh" / "id_rsa")


class SSHClientService:
    def __init__(self, base_path: str | Path):
        self.base_path = Path(base_path)
        self.cli_path = self._resolve_cli_path()

    def _resolve_cli_path(self) -> Path:
        """Определяет путь к бинарнику в зависимости от ОС."""
        if sys.platform == "win32":
            cli_path = self.base_path / "comsol-cli.exe"
        else:
            cli_path = self.base_path / "comsol-cli"

        return cli_path

    def upload_and_execute(
        self, local_file: str, config: SSHConfig, command: str = "ls -la"
    ) -> tuple[bool, str]:
        """
        Загружает файл на сервер и выполняет команду.

        Returns:
            tuple[bool, str]: (успех, вывод stdout/stderr)
        """
        if not self.cli_path.exists():
            return False, f"CLI не найден: {self.cli_path}"

        key_path = config.key_path

        args = [
            str(self.cli_path),
            "-user",
            config.user,
            "-host",
            config.host,
            "-port",
            str(config.port),
            "-key",
            key_path,
            "-local",
            local_file,
            "-remote",
            config.remote_dir,
            "-cmd",
            command,
        ]

        try:
            result = subprocess.run(args, capture_output=True, text=True, timeout=60)
            output = result.stdout + result.stderr
            success = result.returncode == 0
            return success, output
        except subprocess.TimeoutExpired:
            return False, "Превышено время ожидания (60с)"
        except Exception as e:
            return False, f"Ошибка: {str(e)}"
