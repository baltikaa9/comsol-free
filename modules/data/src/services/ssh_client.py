import shutil
import subprocess
import sys
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass
class SSHConfig:
    # Подключение
    user: str = "vasite-landing"
    host: str = "ivsand.ru"
    port: int = 2222
    key_path: str = ""
    password: str = ""  # Пароль (если нет ключа)

    # Файлы
    local_file: str = ""  # Data-файл для загрузки
    remote_dir: str = "/home/bitrix/"  # Базовая удаленная папка
    local_exe: str = ""  # Локальный exe (загрузится на сервер, опционально)

    # Папка проекта
    project_folder: str = ""  # Имя папки для создания на сервере (опционально)
    project_path: str = ""  # Путь к папке проекта (CUDA и т.д.)

    # Команда
    run_command: str = ""  # Команда ({exe} = имя загруженного exe)

    def __post_init__(self):
        if not self.key_path:
            self.key_path = str(Path.home() / ".ssh" / "id_rsa")

    @property
    def effective_remote_dir(self) -> str:
        """Возвращает путь с учётом project_folder, всегда с / в конце."""
        base = self.remote_dir.rstrip("/")
        if self.project_folder:
            return f"{base}/{self.project_folder}/"
        return f"{base}/"


class SSHClientService:
    def __init__(self, base_path: str | Path):
        self.base_path = Path(base_path)
        self.cli_path = self._resolve_cli_path()

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

    def _run_cli(
        self, args: list[str], on_output: Callable[[str], None] | None = None
    ) -> tuple[bool, str]:
        """Запускает CLI с потоковым выводом. Только stdout CLI, без лишних сообщений."""
        full_output = ""
        try:
            proc = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            for line in proc.stdout:
                line = line.rstrip("\n")
                full_output += line + "\n"
                if on_output:
                    on_output(line)

            proc.wait()
            return proc.returncode == 0, full_output
        except Exception as e:
            return False, full_output + f"\nОшибка: {str(e)}"

    def _prepare_project_archive(self, config: SSHConfig) -> tuple[str, str] | None:
        """
        Создаёт временный архив папки проекта + data-файл внутри.
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

        # Копируем папку во временное место
        tmp_project = tmp_dir / folder_name
        shutil.copytree(project_dir, tmp_project)

        # Копируем data-файл внутрь
        if config.local_file:
            data_src = Path(config.local_file)
            if data_src.exists():
                shutil.copy2(data_src, tmp_project / data_src.name)

        # Архивируем
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(tmp_project, arcname=folder_name)

        return archive_path, folder_name

    def upload_and_execute(
        self, config: SSHConfig, on_output: Callable[[str], None] | None = None
    ) -> tuple[bool, str]:
        if not self.cli_path.exists():
            return False, f"CLI не найден: {self.cli_path}"

        archive_info = self._prepare_project_archive(config)

        # === РЕЖИМ: Папка проекта ===
        if archive_info:
            archive_path, folder_name = archive_info

            # Определяем целевую папку
            if config.project_folder:
                remote_dir = config.effective_remote_dir
            else:
                # Папка не указана → используем имя папки проекта
                base = config.remote_dir.rstrip("/")
                remote_dir = f"{base}/{folder_name}/"

            # 1. Создаём папку на сервере
            mkdir_args = self._build_cli_args(
                config,
                local_file="",
                remote_dir=remote_dir,
                cmd=f"mkdir -p {remote_dir}",
            )
            self._run_cli(mkdir_args, on_output)

            # 2. Загружаем архив
            upload_args = self._build_cli_args(
                config, local_file=archive_path, remote_dir=remote_dir, cmd=""
            )
            success, output = self._run_cli(upload_args, on_output)
            if not success:
                return False, f"Ошибка загрузки архива:\n{output}"

            # 3. Распаковываем СОДЕРЖИМОЕ прямо в папку (без обёртки)
            archive_name = Path(archive_path).name
            extract_cmd = (
                f"cd {remote_dir} && "
                f"tar xzf {archive_name} --strip-components=1 && "
                f"rm {archive_name}"
            )

            extract_args = self._build_cli_args(
                config, local_file="", remote_dir=remote_dir, cmd=extract_cmd
            )
            self._run_cli(extract_args, on_output)

            # 4. Компиляция и запуск
            if config.run_command.strip():
                cmd = f"cd {remote_dir} && {config.run_command.strip()}"
            else:
                # Ищем .cu файл автоматически
                cu_files = list(Path(config.project_path).glob("*.cu"))
                if cu_files:
                    cu_name = cu_files[0].name
                    out_name = cu_files[0].stem + ".out"
                    cmd = f"cd {remote_dir} && nvcc {cu_name} -arch=sm_70 -o {out_name} && ./{out_name}"
                else:
                    cmd = f"cd {remote_dir} && ls -la"

            run_args = self._build_cli_args(
                config, local_file="", remote_dir=remote_dir, cmd=cmd
            )
            return self._run_cli(run_args, on_output)

        # === РЕЖИМ: Один файл (старый) ===
        if not config.local_file:
            return False, "Не выбран файл или папка проекта."

        remote_dir = config.effective_remote_dir

        # 0. Создаём папку проекта если указана
        if config.project_folder:
            mkdir_args = self._build_cli_args(
                config,
                local_file="",
                remote_dir=remote_dir,
                cmd=f"mkdir -p {remote_dir}",
            )
            self._run_cli(mkdir_args, on_output)

        # 1. Загружаем exe если указан
        exe_name = None
        if config.local_exe:
            if not Path(config.local_exe).exists():
                return False, f"Локальный exe не найден: {config.local_exe}"

            exe_name = Path(config.local_exe).name
            exe_args = self._build_cli_args(
                config, local_file=config.local_exe, remote_dir=remote_dir, cmd=""
            )
            success, output = self._run_cli(exe_args, on_output)
            if not success:
                return False, f"Ошибка загрузки exe:\n{output}"

        # 2. Формируем команду
        remote_exe_path = None
        if exe_name:
            remote_exe_path = remote_dir.rstrip("/") + "/" + exe_name

        if config.run_command.strip():
            cmd = config.run_command.strip()
            if exe_name:
                cmd = cmd.replace("{exe}", f"./{exe_name}").replace(
                    "{exe_path}", remote_exe_path
                )
        elif exe_name:
            cmd = f"chmod +x {remote_exe_path} && ./{exe_name}"
        else:
            cmd = "ls -la"

        # 3. Загружаем data-файл и выполняем команду
        args = self._build_cli_args(
            config, local_file=config.local_file, remote_dir=remote_dir, cmd=cmd
        )

        return self._run_cli(args, on_output)
