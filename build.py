#!/usr/bin/env python
"""Скрипт сборки FreeFlow. Собирает comsol-cli + PyInstaller."""

import os
import shutil
import string
import subprocess
import sys
from pathlib import Path

import cairosvg

SPEC_TEMPLATE = string.Template("""# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['modules/data/main.py'],
    pathex=[],
    binaries=[
        ('bin/comsol-cli', 'bin'),
        ('bin/comsol-cli.exe', 'bin'),
    ],
    datas=[
        ('modules/data/src', 'src'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='freeflow',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None$icon_line
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='freeflow',
)
""")

root = Path(__file__).parent


def update_submodules():
    """Инициализирует и обновляет git-сабмодули."""
    gitmodules = root / ".gitmodules"
    if not gitmodules.exists():
        return
    if not (root / ".git").exists():
        return

    print("🔄 Обновление сабмодулей...")
    subprocess.run(
        ["git", "submodule", "update", "--init", "--recursive"], cwd=root, check=True
    )
    print("✅ Сабмодули обновлены")


def build_cli():
    """Компилирует comsol-cli для Linux и Windows."""
    bin_dir = root / "bin"
    bin_dir.mkdir(exist_ok=True)
    src_dir = root / "modules" / "data" / "comsol-ssh"

    print("🔧 Компиляция comsol-cli для Linux...")
    env_linux = dict(os.environ, CGO_ENABLED="0", GOOS="linux", GOARCH="amd64")
    subprocess.run(
        ["go", "build", "-o", str(bin_dir / "comsol-cli"), "."],
        env=env_linux,
        check=True,
        cwd=src_dir,
    )

    print("🔧 Компиляция comsol-cli для Windows...")
    env_win = dict(os.environ, CGO_ENABLED="0", GOOS="windows", GOARCH="amd64")
    subprocess.run(
        ["go", "build", "-o", str(bin_dir / "comsol-cli.exe"), "."],
        env=env_win,
        check=True,
        cwd=src_dir,
    )

    print("✅ comsol-cli собраны в bin/")


def main():
    icon_spec_line = ""
    # 0. Конвертируем иконку только для Windows
    if sys.platform == "win32":
        print("🎨 Сборка для Windows, готовим иконку...")
        icon_svg_path = root / "modules" / "data" / "src" / "assets" / "icon.svg"
        icon_png_path = root / "modules" / "data" / "src" / "assets" / "icon.png"
        cairosvg.svg2png(url=str(icon_svg_path), write_to=str(icon_png_path), dpi=96)
        print(f"✅ Иконка сохранена в {icon_png_path}")
        icon_spec_line = f",\n    icon='{icon_png_path.as_posix()}'"

    # 1. Обновляем сабмодули
    update_submodules()

    # 2. Собираем comsol-cli если есть Go
    if shutil.which("go"):
        build_cli()
    else:
        print("⚠️ Go не найден, пропускаем comsol-cli")

    # 3. Генерируем spec
    spec_file = root / "freeflow.spec"
    spec_content = SPEC_TEMPLATE.substitute(icon_line=icon_spec_line)
    spec_file.write_text(spec_content)

    # 4. Запускаем PyInstaller
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        str(spec_file),
    ]
    print(f"🔧 Сборка: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
