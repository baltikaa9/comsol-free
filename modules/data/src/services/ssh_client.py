import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable


@dataclass
class SSHConfig:
    """Упрощённая конфигурация для CUDA-проектов."""

    name: str = "Default"
    # Подключение
    user: str = "baltika"
    host: str = "localhost"
    port: int = 22
    key_path: str = ""
    password: str = ""  # Пароль (если нет ключа)

    # Папка проекта (CUDA-исходники)
    project_path: str = ""  # Локальная папка с исходниками (например, Project_test)

    # Папка на сервере
    remote_dir: str = "/home/baltika/projects"  # Базовая директория на сервере

    # Команда для выполнения (опционально)
    run_command: str = ""  # Если пусто - используем compile.ini или авто-компиляцию

    def __post_init__(self):
        if not self.key_path:
            self.key_path = str(Path.home() / ".ssh" / "id_ed25519")

    @property
    def effective_remote_dir(self) -> str:
        """Возвращает путь к папке проекта на сервере."""
        base = self.remote_dir.rstrip("/")
        return f"{base}/"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "SSHConfig":
        return cls(**data)


class SSHConfigManager:
    """Класс для управления списком конфигураций в JSON файле."""

    def __init__(self, config_path: str | Path):
        self.config_path = Path(config_path)
        self.configs: list[SSHConfig] = []
        self.load()

    def load(self):
        if not self.config_path.exists():
            self.configs = [SSHConfig()]
            self.save()
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.configs = []
                    for item in data:
                        # Заполняем дефолтные значения если их нет
                        item.setdefault("user", "baltika")
                        item.setdefault("host", "localhost")
                        item.setdefault("port", 22)
                        item.setdefault(
                            "key_path", str(Path.home() / ".ssh" / "id_ed25519")
                        )
                        item.setdefault("password", "")
                        item.setdefault("run_command", "")
                        self.configs.append(SSHConfig.from_dict(item))
                else:
                    self.configs = [SSHConfig()]
        except Exception:
            self.configs = [SSHConfig()]

    def save(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(
                [c.to_dict() for c in self.configs], f, indent=4, ensure_ascii=False
            )

    def add_config(self, config: SSHConfig):
        self.configs.append(config)
        self.save()

    def update_config(self, name: str, updated_config: SSHConfig):
        for i, config in enumerate(self.configs):
            if config.name == name:
                self.configs[i] = updated_config
                break
        self.save()

    def remove_config(self, name: str):
        self.configs = [c for c in self.configs if c.name != name]
        self.save()

    def get_config(self, name: str) -> SSHConfig | None:
        for c in self.configs:
            if c.name == name:
                return c
        return None


class SSHClientService:
    def __init__(self, base_path: str | Path):
        self.base_path = Path(base_path)
        self.cli_path = self._resolve_cli_path()
        self.proc = None

    def _resolve_cli_path(self) -> Path:
        if sys.platform == "win32":
            return self.base_path / "comsol-cli.exe"
        return self.base_path / "comsol-cli"

    def _build_cli_args(
        self, config: SSHConfig, local_file: str, remote_dir: str, cmd: str
    ) -> list[str]:
        """Формирует аргументы CLI: -key или -pass."""
        args = [
            str(self.cli_path),
            "-user",
            config.user,
            "-host",
            config.host,
            "-port",
            str(config.port),
            "-local",
            local_file,
            "-remote",
            remote_dir,
            "-cmd",
            cmd,
        ]
        if config.password:
            args.extend(["-pass", config.password])
        else:
            args.extend(["-key", config.key_path])
        return args

    def stop_cli(self):
        """Останавливает запущенный CLI процесс."""
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()

    def _run_cli(
        self,
        args: list[str],
        on_output: Callable[[str], None] | None = None,
        is_retry: bool = False,
    ) -> tuple[bool, str]:
        """Запускает CLI с потоковым выводом."""
        full_output = ""
        try:
            self.proc = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )

            for line in self.proc.stdout:
                line = line.rstrip("\n")
                full_output += line + "\n"
                if on_output:
                    on_output(line)

            self.proc.wait()
            returncode = self.proc.returncode

            # Если команда не найдена (exit code 127), пробуем найти её через which
            # Но только один раз (чтобы избежать бесконечной рекурсии)
            if returncode == 127 and not is_retry:
                # Извлекаем команду из вывода
                for line in full_output.split("\n"):
                    if "command not found" in line or "not found" in line.lower():
                        # Ищем имя команды в строке
                        parts = line.split()
                        for part in parts:
                            if (
                                part
                                and not part.startswith("-")
                                and not part.startswith("/")
                            ):
                                cmd_name = part.strip()
                                # Ищем через which
                                which_cmd = (
                                    f"which {cmd_name} 2>/dev/null || echo not_found"
                                )
                                which_args = self._build_cli_args(
                                    object(),  # type: ignore
                                    local_file="",
                                    remote_dir="/tmp",
                                    cmd=which_cmd,
                                )
                                which_success, which_output = self._run_cli(
                                    which_args, is_retry=True
                                )
                                if (
                                    which_success
                                    and which_output.strip() != "not_found"
                                ):
                                    # Команда найдена, пробуем выполнить с полным путём
                                    full_output += f"\nНайдена команда {cmd_name}: {which_output.strip()}\n"
                                    # Перезапускаем с полным путём
                                    new_args = self._replace_cmd_in_args(
                                        args, cmd_name, which_output.strip()
                                    )
                                    if new_args:
                                        return self._run_cli(
                                            new_args, on_output, is_retry=True
                                        )
                                break

            return returncode == 0, full_output
        except Exception as e:
            return False, full_output + f"\nОшибка: {str(e)}"

    def _replace_cmd_in_args(
        self, args: list[str], old_cmd: str, new_cmd: str
    ) -> list[str] | None:
        """Заменяет команду в аргументах на новый путь."""
        try:
            new_args = args.copy()
            for i, arg in enumerate(new_args):
                if arg == "-cmd" and i + 1 < len(new_args):
                    # Заменяем команду в строке
                    cmd_str = new_args[i + 1]
                    # Простая замена - заменяем имя команды в начале строки
                    if cmd_str.strip().startswith(old_cmd):
                        new_args[i + 1] = cmd_str.replace(old_cmd, new_cmd, 1)
                    return new_args
            return None
        except:
            return None

    def _prepare_project_archive(
        self, config: SSHConfig, mesh_file: str | None = None
    ) -> tuple[str, str] | None:
        """
        Создаёт временный архив содержимого папки проекта + сетку внутри.
        Возвращает (путь к архиву, имя папки на сервере) или None.
        """
        if not config.project_path:
            return None

        project_dir = Path(config.project_path)
        if not project_dir.is_dir():
            return None

        folder_name = project_dir.name

        tmp_dir = Path(tempfile.mkdtemp(prefix="freeflow_"))
        archive_path = str(tmp_dir / f"{folder_name}.tar.gz")

        # Копируем СОДЕРЖИМОЕ папки во временное место (не саму папку)
        tmp_project = tmp_dir / folder_name
        tmp_project.mkdir(parents=True, exist_ok=True)

        # Копируем все файлы и папки из project_dir в tmp_project
        for item in project_dir.iterdir():
            if item.is_file():
                shutil.copy2(item, tmp_project / item.name)
            elif item.is_dir():
                shutil.copytree(item, tmp_project / item.name)

        # Копируем сетку внутрь папки dat/
        if mesh_file:
            mesh_src = Path(mesh_file)
            if mesh_src.exists():
                dat_dir = tmp_project / "dat"
                dat_dir.mkdir(exist_ok=True)
                shutil.copy2(mesh_src, dat_dir / mesh_src.name)
                print(f"  Сетка скопирована: {mesh_src.name}")

        # Архивируем содержимое tmp_project - добавляем каждый элемент напрямую
        # Это важно: файлы попадут в корень архива, а не в папку folder_name
        with tarfile.open(archive_path, "w:gz") as tar:
            for item in tmp_project.iterdir():
                # arcname=item.name означает, что файл попадёт в корень архива
                tar.add(item, arcname=item.name)

        return archive_path, folder_name

    def upload_and_execute(
        self,
        config: SSHConfig,
        mesh_file: str | None = None,
        on_output: Callable[[str], None] | None = None,
    ) -> tuple[bool, str]:
        """
        Загружает проект и запускает расчёт.

        :param config: Конфигурация SSH
        :param mesh_file: Путь к файлу сетки (structured_mesh.json)
        :param on_output: Колбек для вывода
        :return: (успех, вывод)
        """
        if not self.cli_path.exists():
            return False, f"CLI не найден: {self.cli_path}"

        if not config.project_path:
            return False, "Не указана папка с CUDA-исходниками"

        project_dir = Path(config.project_path)
        if not project_dir.is_dir():
            return False, f"Папка проекта не найдена: {config.project_path}"

        # Ищем compile.ini для получения команды компиляции
        compile_ini = project_dir / "compile.ini"
        compile_cmd = None
        if compile_ini.exists():
            with open(compile_ini, "r") as f:
                compile_cmd = f.read().strip()
            print(f"  Команда из compile.ini: {compile_cmd}")

        archive_info = self._prepare_project_archive(config, mesh_file)
        if not archive_info:
            return False, "Не удалось подготовить архив проекта"

        archive_path = archive_info[0]
        remote_dir = config.effective_remote_dir

        print(f"  Загрузка в {remote_dir}...")

        # 1. Создаём папку на сервере
        mkdir_args = self._build_cli_args(
            config,
            local_file="",
            remote_dir=remote_dir,
            cmd=f"mkdir -p {remote_dir}",
        )
        success, output = self._run_cli(mkdir_args, on_output)
        if not success:
            return False, f"Ошибка создания папки:\n{output}"

        # 2. Загружаем архив
        upload_args = self._build_cli_args(
            config, local_file=archive_path, remote_dir=remote_dir, cmd=""
        )
        success, output = self._run_cli(upload_args, on_output)
        if not success:
            return False, f"Ошибка загрузки архива:\n{output}"

        # 3. Распаковываем - файлы попадут прямо в remote_dir
        archive_name = Path(archive_path).name
        extract_cmd = f"cd {remote_dir} && tar xzf {archive_name} && rm {archive_name}"

        extract_args = self._build_cli_args(
            config, local_file="", remote_dir=remote_dir, cmd=extract_cmd
        )
        success, output = self._run_cli(extract_args, on_output)
        if not success:
            return False, f"Ошибка распаковки:\n{output}"

        # 4. Компиляция и запуск
        if config.run_command.strip():
            # Используем пользовательскую команду
            cmd = f"cd {remote_dir} && {config.run_command.strip()}"
        elif compile_cmd:
            # Используем команду из compile.ini
            cmd = f"cd {remote_dir} && {compile_cmd}"
        else:
            # Автоматическая компиляция .cu файлов
            cmd = f"cd {remote_dir} && {nvcc_path} *.cu -arch=sm_70 -o shock.out && ./shock.out"

        run_args = self._build_cli_args(
            config, local_file="", remote_dir=remote_dir, cmd=cmd
        )
        return self._run_cli(run_args, on_output)
