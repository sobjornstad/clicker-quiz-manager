# -*- mode: python -*-

block_cipher = None


a = Analysis(['runcqm.py'],
             pathex=['C:\\Users\\Soren\\Desktop\\cqm-1.1.1\\clicker-quiz-manager'],
             binaries=None,
             datas=[('docs/manual.html', 'docs'),
			        ('docs/resources/*.html', 'docs/resources'),
					('docs/resources/css/*.css', 'docs/resources/css'),
			        ('db/resources/*.tex', 'db/resources'),
					('db/resources/*.html', 'db/resources'),
					],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None,
             excludes=None,
             win_no_prefer_redirects=None,
             win_private_assemblies=None,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='runcqm',
          debug=False,
          strip=None,
          upx=True,
          console=False )
