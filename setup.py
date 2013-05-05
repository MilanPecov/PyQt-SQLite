from py2exe.build_exe import py2exe
from distutils.core import setup

data_files = [
            ('db',          ['db\Base.adb']),
            ('sqldrivers',  ['D:\Python27\Lib\site-packages\PyQt4\plugins\sqldrivers\qsqlite4.dll']),
            ('imageformats',['D:\Python27\Lib\site-packages\PyQt4\plugins\imageformats\qico4.dll']),
            ('icons',       ['icons\Add.ico',
                             'icons\Edit.ico',
             		     'icons\Delete.ico',
                             'icons\Restoran.ico',
             		     'icons\Chart.ico',
             		     'icons\Check.ico',
             		     'icons\Exit.ico'])
            ]

setup(name = "Restoran",
      version = "1.0",
      description = "Softver za vodenje fiskalna kasa",
      author = "Pecov Milan",
      windows = [{"script": "restoran.pyw", "icon_resources": [(1, "Restoran.ico")]}],
      options = {"py2exe" : {"includes" : ["sip", "PyQt4.QtSql"]}},
      data_files = data_files)