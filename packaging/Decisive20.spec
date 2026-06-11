# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

SPEC_LOCATION = Path(SPECPATH).resolve()
SPEC_DIR = SPEC_LOCATION if SPEC_LOCATION.is_dir() else SPEC_LOCATION.parent
ROOT = SPEC_DIR.parent

a = Analysis(
    [str(ROOT / "decisive20" / "launcher.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        (str(ROOT / "scenarios"), "scenarios"),
        (str(ROOT / "decisive20" / "web" / "static"), "decisive20/web/static"),
    ],
    hiddenimports=[
        "uvicorn.lifespan.on",
        "uvicorn.loops.auto",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets.auto",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Decisive20",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Decisive20",
)
