# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all submodules
hidden_imports = collect_submodules('trading_bot')
hidden_imports.extend([
    'pandas',
    'numpy',
    'talib',
    'talib.stream',  # Added to fix PyInstaller TA-Lib error
    'python-binance',
    'apscheduler',
    'rich',
    'python-dotenv',
    'google.generativeai',
    'apscheduler.triggers.interval',
    'apscheduler.triggers.cron',
    'apscheduler.triggers.date',
    'apscheduler.triggers.combining',
    'apscheduler.triggers.calendarinterval',
])

# Collect all data files
datas = collect_data_files('trading_bot')
datas.extend([
    ('trading_bot/config/*.py', 'trading_bot/config'),
    ('trading_bot/core/*.py', 'trading_bot/core'),
    ('trading_bot/strategies/*.py', 'trading_bot/strategies'),
    ('trading_bot/ai/*.py', 'trading_bot/ai'),
    ('trading_bot/ui/*.py', 'trading_bot/ui'),
])

a = Analysis(
    ['trading_bot/main.py'],
    pathex=[os.path.abspath(SPECPATH)],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TradingBot',
    debug=True,  # Keep debug mode for now
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
) 