#!/usr/bin/env python
# FIXME: Get py2exe working for Windows builds (since it produces a single EXE).

import sys
import os
import glob
from cx_Freeze import setup , Executable

from constants import *

base_dir = os.path.split( os.path.abspath(__file__) )[ 0 ]
os.chdir( base_dir )

import asl_cards

# ---------------------------------------------------------------------

def get_extra_files( fspec ) :
    """Locate extra files to include in the release."""
    fnames = glob.glob( fspec )
    return zip( fnames , fnames )

# initialize
extra_files = []
extra_files.extend( get_extra_files( "resources/*.ico" ) )
extra_files.extend( get_extra_files( "resources/*.png" ) )
extra_files.extend( get_extra_files( "ui/*ui" ) )
build_options = {
    "packages": [ "os" , "sqlalchemy" ] ,
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
        "build_exe": build_options
    } ,
    executables = [ target ]
)
