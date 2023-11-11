# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

current_path = os.getcwd()

MODE = 'gui' # gui | cli

a = Analysis(['execute.py'],
             pathex=['./dcinisde_cleaner/', current_path],
             binaries=[],
             datas=[
                 (os.path.join(current_path, 'dcinside_cleaner/gui/ui_main_window.ui'), '.')
             ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='dcinside-cleaner-' + MODE,
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=MODE!='gui' )
