from py2exe.build_exe import py2exe
from distutils.core import setup

data_files = [
            ('db',          ['db\Base.adb']),
            ('sqldrivers',  ['dll\qsqlite4.dll']),
            ('imageformats',['dll\qico4.dll',
                             'dll\qjpeg4.dll']),
            ('icons',       ['icons\Add.ico',
                             'icons\Edit.ico',
                             'icons\Delete.ico',
                             'icons\Restoran.ico',
                             'icons\drinks.jpg',
                             'icons\New.ico',
                             'icons\User.ico',
                             'icons\Open.ico',
                             'icons\Report.ico',
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