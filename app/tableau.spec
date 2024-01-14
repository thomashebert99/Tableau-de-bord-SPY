# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['tableau.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/images', 'assets/images'),
        ('assets/style.css', 'assets'),
        ('data/Scripts', 'data/Scripts'),
        ('data/Raw', 'data/Raw'),
        ('data/Processed', 'data/Processed'),
        ('data/Models', 'data/Models')
        ],
    hiddenimports=[],
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
    name='tableau',
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
    name='tableau',
)
