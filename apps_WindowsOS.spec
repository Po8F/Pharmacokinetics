# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/apps.py'],
    pathex=['src'],
    binaries=[],
    datas=[('image/placeholder_image.png', './image'),
           ('.venv/Lib/site-packages/gradio', 'gradio'),
           ('.venv/Lib/site-packages/gradio_client', 'gradio_client')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
    module_collection_mode={'gradio': 'py',}
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PharmacokineticAnalysis_windows',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # 啟用 UPX 壓縮
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)