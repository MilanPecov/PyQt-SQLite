from py2exe.build_exe import py2exe
from distutils.core import setup
import os
print os.path.split(__file__)[0]

data_files = [
            ('',            ['Base.adb']),

            ('sqldrivers',  ['dll\qsqlite4.dll']),

            ('imageformats',['dll\qico4.dll',
                             'dll\qjpeg4.dll']),

            ('static',      ['static\style.stylesheet']),

            ('static\icons',['static\icons\Add.ico',
                             'static\icons\Edit.ico',
                             'static\icons\Delete.ico',
                             'static\icons\Restoran.ico',
                             'static\icons\New.ico',
                             'static\icons\User.ico',
                             'static\icons\Open.ico',
                             'static\icons\Report.ico',
                             'static\icons\Check.ico',
                             'static\icons\Exit.ico']),

            ('static\images',['static\images\drinks.jpg',
                              'static\images\cell-blue.jpg',
                              'static\images\cell-gray.jpg',
                              'static\images\Bg-01.png',
                              'static\images\Bg-02.jpg'])
            ]

setup(name = "Restoran",
      version = "1.0",
      description = "softver za vodenje fiskalna kasa",
      author = "Pecov Milan",
      windows = [{"script": "restoran.pyw", "icon_resources": [(1, "static\icons\Restoran.ico")]}],
      options = {"py2exe" : {"includes" : ["sip", "PyQt4.QtSql"]}},
      data_files = data_files)

