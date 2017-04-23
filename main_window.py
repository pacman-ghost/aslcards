import sys
import os

from PyQt5.QtCore import Qt , QPoint , QSize
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon

from constants import *
import globals

# ---------------------------------------------------------------------

class MainWindow( QMainWindow ) :

    def __init__( self ) :
        super().__init__()
        # initialize the window
        self.setWindowTitle( APP_NAME )
        self.setWindowIcon( QIcon("resources/app.ico") )
        # load the window settings
        self.resize( globals.app_settings.value( MAINWINDOW_SIZE , QSize(500,300) ) )
        self.move( globals.app_settings.value( MAINWINDOW_POSITION , QPoint(200,200) ) )

    def closeEvent( self , evt ) :
        """Handle window close."""
        # confirm the close
        if globals.app_settings.value( CONFIRM_EXIT , True , type=bool ) :
            rc = QMessageBox.question( self , "Confirm close" ,
                "Do you want to the close the program?" ,
                QMessageBox.Ok | QMessageBox.Cancel ,
                QMessageBox.Cancel
            )
            if rc != QMessageBox.Ok :
                evt.ignore()
        # save the window settings
        # FIXME! handle fullscreen
        globals.app_settings.setValue( MAINWINDOW_POSITION ,  self.pos() )
        globals.app_settings.setValue( MAINWINDOW_SIZE ,  self.size() )

    def keyPressEvent( self , evt ) :
        """Handle key-presses."""
        if evt.key() == Qt.Key_Escape and globals.debug_settings.value("Debug/AllowEscapeToClose",type=bool) :
            self.close()
