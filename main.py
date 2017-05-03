#!/usr/bin/env python3

import sys
import os
import getopt

from PyQt5.QtCore import QSettings , QDir
from PyQt5.QtWidgets import QApplication

from asl_cards import natinfo
from constants import *
import globals

# ---------------------------------------------------------------------

def do_main( args ) :

    # initialize
    QApplication.setOrganizationName( APP_VENDOR )
    QApplication.setOrganizationDomain( APP_HOME_URL )
    QApplication.setApplicationName( APP_NAME )

    # initialize
    globals.base_dir , app_name = os.path.split(
        os.path.abspath( sys.executable if hasattr(sys,"frozen") else __file__ )
    )
    globals.app_name = os.path.splitext( app_name )[ 0 ]

    # parse the command-line arguments
    settings_fname = None
    db_fname = None
    opts , args = getopt.getopt( args[1:] , "c:d:h?" , ["config=","db=","help"] )
    for opt,val in opts :
        if opt in ["-c","--config"] :
            settings_fname = val
        elif opt in ["-d","--db"] :
            db_fname = val
        elif opt in ["-h","--help","-?"] :
            print_help()
        else :
            raise RuntimeError( "Unknown argument: {}".format( opt ) )
    if not settings_fname :
        # try to locate the settings file
        fname = globals.app_name+".ini" if sys.platform == "win32" else "."+globals.app_name
        settings_fname = os.path.join( globals.base_dir , fname )
        if not os.path.isfile( settings_fname ) :
            settings_fname = os.path.join( QDir.homePath() , fname  )
    if not db_fname :
        # use the default location
        db_fname = os.path.join( globals.base_dir , globals.app_name+".db" )

    # load our settings
    globals.app_settings = QSettings( settings_fname , QSettings.IniFormat )
    fname = os.path.join( os.path.split(settings_fname)[0] , "debug.ini" )
    globals.debug_settings = QSettings( fname , QSettings.IniFormat )

    # initialize
    natinfo.load(
        os.path.join( globals.base_dir , "asl_cards/natinfo" )
    )

    # do main processing
    app = QApplication( sys.argv )
    from main_window import MainWindow
    main_window = MainWindow( db_fname )
    main_window.show()
    if os.path.isfile( db_fname ) :
        main_window.start_main_app( db_fname )
    return app.exec_()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def print_help() :
    print( "{} {{options}}".format( globals.app_name ) )
    print( "  {}".format( APP_DESCRIPTION ) )
    print()
    print( "  -c   --config    Config file." )
    print( "  -d   --db        Database file." )
    sys.exit()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

if __name__ == "__main__" :
    sys.exit( do_main( sys.argv ) )
