#!/usr/bin/env python3

import sys
import os
import getopt

from PyQt5.QtCore import QSettings , QDir
from PyQt5.QtWidgets import QApplication

from constants import *
import globals
import asl_cards.db as db

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
        settings_fname = os.path.join( globals.base_dir , globals.app_name+".ini" )
        if not os.path.isfile( settings_fname ) :
            settings_fname = os.path.split(settings_fname)[ 1 ]
            if sys.platform != "win32" :
                settings_fname = "." + settings_fname
            settings_fname = os.path.join( QDir.homePath() , settings_fname  )
    if not db_fname :
        # try to locate the database
        db_fname = os.path.join( globals.base_dir , globals.app_name+".db" )
    if not os.path.isfile( db_fname ) :
        raise RuntimeError( "Can't find database: {}".format( db_fname ) )

    # load our settings
    globals.app_settings = QSettings( settings_fname , QSettings.IniFormat )
    fname = os.path.join( os.path.split(settings_fname)[0] , "debug.ini" )
    globals.debug_settings = QSettings( fname , QSettings.IniFormat )

    # open the database
    db.open_database( db_fname )
    globals.cards = db.load_cards()

    # do main processing
    app = QApplication( sys.argv )
    import main_window
    main_window = main_window.MainWindow()
    main_window.show()
    return app.exec_()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def print_help() :
    print( "{} {{options}}".format( os.path.split(sys.argv[0])[1] ) ) # FIXME! frozen?
    print( "  {}".format( APP_DESCRIPTION ) )
    print()
    print( "  -c   --config    Config file." )
    sys.exit()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

if __name__ == "__main__" :
    sys.exit( do_main( sys.argv ) )
