# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['acd_pyqt_v0.2.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['pydicom.encoders.gdcm', 'pydicom.encoders.pylibjpeg'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pandas'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='acd_pyqt_v0.2',
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
    entitlements_file=None,
    icon="icon/icon.ico"
)


coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='acd_pyqt_v0.2')