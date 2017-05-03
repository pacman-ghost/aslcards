#!/usr/bin/env python

# NOTE: It would be nice to be able to use py2exe to compile this for Windows (since it produces
# a single EXE instead of the morass of files cx-freeze generates) but py2exe only works up to
# Python 3.4, since the byte code format changed after that.

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
extra_files.extend( get_extra_files( "index/*.txt" ) )
extra_files.extend( get_extra_files( "resources/*.ico" ) )
extra_files.extend( get_extra_files( "resources/*.png" ) )
extra_files.extend( get_extra_files( "ui/*.ui" ) )
extra_files.append( ( "asl_cards/natinfo" , "asl_cards/natinfo" ) )
if sys.platform == "win32" :
    # workaround a cx-freeze bug (already fixed, but after 5.0.1 was released) :wall: >:-/
    # https://bitbucket.org/anthony_tuininga/cx_freeze/issues/207/sqlite3dll-not-shipped
    extra_files.append( os.path.join( sys.base_prefix , "DLLs" , "sqlite3.dll" ) )
build_options = {
    "packages": [ "os" , "sqlalchemy" ] ,
    "excludes": [ "tkinter" ] ,
    "include_files": extra_files ,
}

# freeze the application
# NOTE: We can't call the Linux binary "asl_cards", since we need a directory of the same name :-/
target = Executable(
    "main.py" ,
    base = "Win32GUI" if sys.platform == "win32" else None ,
    targetName = "aslcards.exe" if sys.platform == "win32" else "aslcards" ,
    icon = os.path.join( base_dir , "resources/app.ico" ) ,
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
