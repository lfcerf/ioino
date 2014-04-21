#!/usr/bin/env python
# -*- coding: utf-8 -*-

##This file is part of pyArduinoScope
#############################################################################
#############################################################################
##                                                                         ##
##                                   setup                                 ##
##                                                                         ##
#############################################################################
#############################################################################

## Copyright (C) 2012 Cédrick FAURY

#    pyArduinoScope is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
    
#    pyArduinoScope is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pyArduinoScope; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

##################################################################################################
#
#    Script pour générer un pack avec executable :
#    c:\python26\python setup.py build
#
##################################################################################################

import sys, os
from glob import glob
from cx_Freeze import setup, Executable

## Remove the build folder, a bit slower but ensures that build contains the latest
import shutil
shutil.rmtree("build", ignore_errors=True)

# Inculsion des fichiers de données
#################################################################################################
includefiles = [('Microsoft.VC90.CRT', "Microsoft.VC90.CRT"),
                     'gpl.txt', 
                     ]
#includefiles.extend(glob(r"*.xlsx"))
#includefiles.extend(glob(r"*.xls"))
#includefiles.extend(glob(r"*.xlsm"))


# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os"], 
                     "excludes": ["tkinter",
                                  '_gtkagg', '_tkagg', 'bsddb', 'curses', 'pywin.debugger',
                                  'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
                                  'Tkconstants', 'pydoc', 'doctest', 'test', 'sqlite3',
                                  "PyQt4", "PyQt4.QtGui","PyQt4._qt",
                                  "matplotlib",
                                  "numpy",
                                  ],
                     "include_files": includefiles,
                     'bin_excludes' : ['libgdk-win32-2.0-0.dll', 'libgobject-2.0-0.dll', 'tcl85.dll',
                                              'tk85.dll', "UxTheme.dll", "mswsock.dll", "POWRPROF.dll",
                                              "QtCore4.dll", "QtGui4.dll" ]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
#if sys.platform == "win32":
#    base = "Win32GUI"

cible = Executable(
    script = "pyArduinoScope.py",
    base = base,
    compress = True,
#    icon = os.path.join("", 'logo.ico'),
    initScript = None,
    copyDependentFiles = True,
    appendScriptToExe = False,
    appendScriptToLibrary = False
    )


setup(  name = "pyArduinoScope",
        version = "0.3",
        author = "Cedrick FAURY",
        description = u"pyArduinoScope",
        options = {"build_exe": build_exe_options},
#        include-msvcr = True,
        executables = [cible])
