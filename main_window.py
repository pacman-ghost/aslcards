import sys
import os

from PyQt5.QtCore import Qt , QPoint , QSize
from PyQt5.QtWidgets import QMainWindow , QVBoxLayout , QHBoxLayout , QWidget , QTabWidget , QLabel
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPainter , QPixmap , QIcon , QBrush

import asl_cards.db as db
from constants import *
import globals

# ---------------------------------------------------------------------

class AslCardWidget( QWidget ) :

    def __init__( self , card ) :
        # initialize
        super().__init__()
        self.card = card
        self.pixmap = QPixmap()
        self.pixmap.loadFromData( card.card_image.image_data )

    def paintEvent( self , evt ) :
        qp = QPainter()
        qp.begin( self )
        qp_size = evt.rect().size()
        # draw the AslCard image
        qp.setRenderHint( QPainter.Antialiasing )
        pixmap_size = self.pixmap.size()
        pixmap_size.scale( qp_size , Qt.KeepAspectRatio )
        pixmap = self.pixmap.scaled( pixmap_size , Qt.KeepAspectRatio , Qt.SmoothTransformation )
        qp.drawPixmap(
            (qp_size.width()-pixmap_size.width())/2 , (qp_size.height()-pixmap_size.height())/2 ,
            pixmap
        )
        qp.end()

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
        # initialize the window controls
        self.tab_widget = QTabWidget( self )
        self.tab_widget.setTabsClosable( True )
        self.tab_widgets = []

        for i in range(0,3) : # FIXME!
            card = globals.cards["Chinese"]["ordnance"][ i ]
            w = AslCardWidget( card )
            self.tab_widget.addTab( w , card.name )
            self.tab_widgets.append( w )

        self.setCentralWidget( self.tab_widget )

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
