# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = ['uuid']
imports = ['pymssql']
for im in imports:
    tmp_ret = collect_all(im)
    try:
        datas += tmp_ret[0]; 
        binaries += tmp_ret[1]; 
        hiddenimports += tmp_ret[2]
    except Exception as e:
        print (e.message)


block_cipher = None


a = Analysis(['__init__.py'],
             pathex=[],
             binaries=binaries,
             datas=datas,
             hiddenimports=hiddenimports,
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
             
# Avoid warning
to_remove = ["_AES", "_ARC4", "_DES", "_DES3", "_SHA256", "_counter", "mssql", "pymssql", "_pymssql"]     

for val in to_remove:
    for b in a.binaries:
          nb = b[0]
          if str(nb).endswith(val) or str(nb).startswith(val):
                print("removed  " + b[0])
                a.binaries.remove(b)
        
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='histdump',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon='icon.ico')
