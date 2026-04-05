import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SSHConfig:
    # Подключение
    user: str = "vasite-landing"
    host: str = "ivsand.ru"
    port: int = 2222
    key_path: str = ""

    # Файлы
    local_file: str = ""  # Data-файл для загрузки
    remote_dir: str = "/home/bitrix/"
    local_exe: str = ""  # Локальный exe (загрузится на сервер, опционально)

    # Команда
    run_command: str = ""  # Команда ({exe} = имя загруженного exe)

    def __post_init__(self):
        if not self.key_path:
            self.key_path = str(Path.home() / ".ssh" / "id_rsa")


class SSHClientService:
    def __init__(self, base_path: str | Path):
        self.base_path = Path(base_path)
        self.cli_path = self._resolve_cli_path()

    def _resolve_cli_path(self) -> Path:
        if sys.platform == "win32":
            return self.base_path / "comsol-cli.exe"
        return self.base_path / "comsol-cli"

    def upload_and_execute(self, config: SSHConfig) -> tuple[bool, str]:
        if not self.cli_path.exists():
            return False, f"CLI не найден: {self.cli_path}"

        if not config.local_file:
            return False, "Не выбран data-файл. Укажите его в настройках SSH."

        full_output = ""

        # 1. Загружаем exe если указан
        exe_name = None
        if config.local_exe:
            if not Path(config.local_exe).exists():
                return False, f"Локальный exe не найден: {config.local_exe}"

            exe_name = Path(config.local_exe).name
            exe_args = [
                str(self.cli_path),
                "-user",
                config.user,
                "-host",
                config.host,
                "-port",
                str(config.port),
                "-key",
                config.key_path,
                "-local",
                config.local_exe,
                "-remote",
                config.remote_dir,
                "-cmd",
                "",
            ]
            try:
                result = subprocess.run(
                    exe_args, capture_output=True, text=True, timeout=120
                )
                full_output += "Загрузка exe:\n" + result.stdout + result.stderr
                if result.returncode != 0:
                    return False, f"Ошибка загрузки exe:\n{full_output}"
            except Exception as e:
                return False, f"Ошибка загрузки exe: {str(e)}"

        # 2. Формируем команду
        remote_exe_path = None
        if exe_name:
            remote_exe_path = config.remote_dir.rstrip("/") + "/" + exe_name

        if config.run_command.strip():
            cmd = config.run_command.strip()
            if exe_name:
                # {exe} = ./имя, {exe_path} = полный путь
                cmd = cmd.replace("{exe}", f"./{exe_name}").replace(
                    "{exe_path}", remote_exe_path
                )
        elif exe_name:
            cmd = f"chmod +x {remote_exe_path} && ./{exe_name}"
        else:
            cmd = "ls -la"

        # Если exe был загружен, но пользователь задал свою команду без chmod — добавим
        if exe_name and "chmod" not in cmd:
            cmd = f"chmod +x {remote_exe_path} && " + cmd

        # 3. Загружаем data-файл и выполняем команду
        args = [
            str(self.cli_path),
            "-user",
            config.user,
            "-host",
            config.host,
            "-port",
            str(config.port),
            "-key",
            config.key_path,
            "-local",
            config.local_file,
            "-remote",
            config.remote_dir,
            "-cmd",
            cmd,
        ]

        try:
            result = subprocess.run(args, capture_output=True, text=True, timeout=120)
            full_output += "\n" + result.stdout + result.stderr
            return result.returncode == 0, full_output
        except subprocess.TimeoutExpired:
            return False, full_output + "\nПревышено время ожидания (120с)"
        except Exception as e:
            return False, full_output + f"\nОшибка: {str(e)}"
