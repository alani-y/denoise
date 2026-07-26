# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for the denoiser app.

Build with:  build.bat
or directly: pyinstaller build.spec

Produces a single-file executable: dist/Denoiser.exe
"""

import sys
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# cv2 sometimes needs its data files explicitly collected (varies by
# opencv-python-headless version / platform). This is a no-op if there's
# nothing to collect.
cv2_datas = collect_data_files("cv2")

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=cv2_datas,
    hiddenimports=[
        "cv2",
        "yaml",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Trim unused heavy stuff that sometimes gets pulled in
        # transitively and bloats the exe.
        "matplotlib",
        "tkinter",
        "PyQt5",
        "PySide2",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="Denoiser",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,           # keep a console window so users see progress/errors
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,               # e.g. icon="app.ico" if you add one later
)
