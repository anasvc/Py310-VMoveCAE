# -*- mode: python -*-

block_cipher = None


a = Analysis(['VMoveCAE.py'],
             pathex=['D:\\Development\\VMoveCAE\\old-lap\\src-new\\python'],
             binaries=[],
             datas=[],
             hiddenimports=['_CaeEngineWrap_x64_Release', '_CaeInfoWrap_x64_Release'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='VMoveCAE',
          debug=False,
          strip=False,
          upx=True,
          console=False , version='VMoveCAE.version-info', icon='VMoveCAE.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='VMoveCAE')
