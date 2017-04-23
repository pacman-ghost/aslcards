#!/usr/bin/env python
# FIXME: Get py2exe working for Windows builds (since it produces a single EXE).

import sys
from cx_Freeze import setup , Executable

from constants import *

# ---------------------------------------------------------------------

# initialize
extra_files = [
    "resources/app.ico"
]
build_options = {
    "packages": [ "os" ] ,
    "excludes": [ "tkinter" ] ,
    "include_files": extra_files ,
}

# freeze the application
# FIXME! set the app icon
target = Executable(
    "main.py" ,
    base = "Win32GUI" if sys.platform == "win32" else None ,
    targetName = "asl_cards.exe" if sys.platform == "win32" else "asl_cards" ,
)
setup(
    name = APP_NAME ,
    version = APP_VERSION ,
    description = APP_DESCRIPTION ,
    options = {
        APP_NAME: build_options
    } ,
    executables = [ target ]
)
