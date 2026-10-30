# Build on Windows with: python -m PyInstaller --noconfirm Turno.spec
from pathlib import Path

ROOT = Path(SPECPATH)
a = Analysis(
    [str(ROOT / 'main.py')],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[(str(ROOT / 'LICENSE'), '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['numpy'],  # Pillow's optional array support is not used by Turno.
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name='Turno',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    icon=str(ROOT / 'build' / 'turno.ico'),
    version=str(ROOT / 'packaging' / 'windows-version.txt'),
)
