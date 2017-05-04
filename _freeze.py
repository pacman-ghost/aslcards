#!/usr/bin/env python

import sys
import os
import shutil
import glob
import getopt
from cx_Freeze import setup , Executable

from constants import *
import asl_cards

base_dir = os.path.split( os.path.abspath(__file__) )[ 0 ]
build_dir = os.path.join( base_dir , "build" )

# ---------------------------------------------------------------------

def get_extra_files() :
    """Get the extra files to include in the release."""
    def globfiles( fspec ) :
        fnames = glob.glob( fspec )
        return zip( fnames , fnames )
    extra_files = [ "license.txt" ]
    extra_files.extend( globfiles( "index/*.txt" ) )
    extra_files.extend( globfiles( "resources/*.ico" ) )
    extra_files.extend( globfiles( "resources/*.png" ) )
    extra_files.extend( globfiles( "ui/*.ui" ) )
    extra_files.append( ( "asl_cards/natinfo" , "asl_cards/natinfo" ) )
    if sys.platform == "win32" :
        # workaround a cx-freeze bug (already fixed, but after 5.0.1 was released) :wall: >:-/
        # https://bitbucket.org/anthony_tuininga/cx_freeze/issues/207/sqlite3dll-not-shipped
        extra_files.append( os.path.join( sys.base_prefix , "DLLs" , "sqlite3.dll" ) )
    return extra_files

# ---------------------------------------------------------------------

# parse the command-line options
output_fname = None
cleanup = True
opts,args = getopt.getopt( sys.argv[1:] , "o:" , ["output=","noclean"] )
for opt,val in opts :
    if opt in ["-o","--output"] :
        output_fname = val.strip()
    elif opt in ["--noclean"] :
        cleanup = False
    else :
        raise RuntimeError( "Unknown argument: {}".format( opt ) )
if not output_fname :
    raise RuntimeError( "No output file was specified." )

# figure out the format of the release archive
formats = { ".zip": "zip" , ".tar.gz": "gztar" , ".tar.bz": "bztar" , ".tar": "tar" }
output_fmt = None
for extn,fmt in formats.items() :
    if output_fname.endswith( extn ) :
        output_fmt = fmt
        output_fname2 = output_fname[ : -len(extn) ]
        break
if not output_fmt :
    raise RuntimeError( "Unknown release archive format: {}".format( os.path.split(output_fname)[1] ) )

# initialize the build options
build_options = {
    "packages": [ "os" , "sqlalchemy" ] ,
    "excludes": [ "tkinter" ] ,
    "include_files": get_extra_files() ,
}

# cx-freeze doesn't work in a virtualenv on Windows :-/
if sys.platform == "win32" and os.getenv("VIRTUAL_ENV") :
    raise RuntimeError( "Can't freeze on Windows in a virtualenv." )

# freeze the application
# NOTE: It would be nice to be able to use py2exe to compile this for Windows (since it produces
# a single EXE instead of the morass of files cx-freeze generates) but py2exe only works up to
# Python 3.4, since the byte code format changed after that.
# NOTE: We can't call the Linux binary "asl_cards", since we need a directory of the same name :-/
target = Executable(
    "main.py" ,
    base = "Win32GUI" if sys.platform == "win32" else None ,
    targetName = "aslcards.exe" if sys.platform == "win32" else "aslcards" ,
    icon = os.path.join( base_dir , "resources/app.ico" ) ,
)
if os.path.isdir( build_dir ) :
    shutil.rmtree( build_dir )
os.chdir( base_dir )
del sys.argv[1:]
sys.argv.append( "build" )
# nb: cx-freeze doesn't report compile errors or anything like that :-/
setup(
    name = APP_NAME ,
    version = APP_VERSION ,
    description = APP_DESCRIPTION ,
    options = {
        "build_exe": build_options
    } ,
    executables = [ target ]
)
print()

# create the release archive
print( "Generating release archive: {}".format( output_fname ) )
files = os.listdir( build_dir )
if len(files) != 1 :
    raise RuntimeError( "Unexpected freeze output." )
dname = os.path.join( build_dir , files[0] )
os.chdir( dname )
shutil.make_archive( output_fname2 , output_fmt )
file_size = os.path.getsize( output_fname )
print( "- Done: {0:.1f} MB".format( float(file_size) / 1024 / 1024 ) )

# clean up
if cleanup :
    os.chdir( base_dir ) # so we can delete the build directory :-/
    shutil.rmtree( build_dir )
