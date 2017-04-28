import sys
import os

from PyQt5.QtCore import Qt , QPoint , QSize
from PyQt5.QtWidgets import QApplication , QMainWindow , QVBoxLayout , QHBoxLayout , QWidget , QTabWidget , QLabel
from PyQt5.QtWidgets import QDialog , QMessageBox , QAction
from PyQt5.QtGui import QPainter , QPixmap , QIcon , QBrush

import asl_cards.db as db
from constants import *
import globals
from add_card_dialog import AddCardDialog
from startup_widget import StartupWidget

# ---------------------------------------------------------------------

class AslCardWidget( QWidget ) :
    """Simple widget that displays the image for an ASL Card."""

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

    _instance = None

    def __init__( self , db_fname ) :
        # initialize
        super().__init__()
        assert MainWindow._instance is None
        MainWindow._instance = self
        # initialize the window
        self.setWindowTitle( APP_NAME )
        self.setWindowIcon( QIcon("resources/app.ico") )
        # initialize the menu
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu( "&File" )
        self.add_card_action = QAction( "&Add" , self )
        self.add_card_action.setEnabled( False )
        self.add_card_action.setShortcut( "Ctrl+A" )
        self.add_card_action.setStatusTip( "Add an ASL Card." )
        self.add_card_action.triggered.connect( self.on_add_card )
        file_menu.addAction( self.add_card_action )
        action = QAction( "E&xit" , self )
        action.setStatusTip( "Close the program." )
        action.triggered.connect( self.close )
        file_menu.addAction( action )
        # load the window settings
        self.resize( globals.app_settings.value( MAINWINDOW_SIZE , QSize(500,300) ) )
        self.move( globals.app_settings.value( MAINWINDOW_POSITION , QPoint(200,200) ) )
        # show the startup form
        self.setCentralWidget(
            StartupWidget( db_fname , parent=self )
        )

    def start_main_app( self , db_fname ) :
        """Start the main app."""
        # we can now close the startup widget and replace it with the main tab widget
        self.tab_widget = QTabWidget( self )
        self.tab_widget.setTabsClosable( True )
        self.setCentralWidget( self.tab_widget )
        # open the database
        db.open_database( db_fname , False )
        globals.cards = db.load_cards()
        # ask the user to add the first card
        self.add_card_action.setEnabled( True )
        self.on_add_card()

    @staticmethod
    def show_info_msg( msg ) :
        """Show an informational message."""
        QMessageBox.information( MainWindow._instance , APP_NAME , msg )
    @staticmethod
    def show_error_msg( msg ) :
        """Show an error message."""
        QMessageBox.warning( MainWindow._instance , APP_NAME , msg )
    @staticmethod
    def ask( msg , buttons , default ) :
        """Ask the user a question."""
        return QMessageBox.question( MainWindow._instance , APP_NAME , msg , buttons , default )

    def closeEvent( self , evt ) :
        """Handle window close."""
        # confirm the close
        widget = self.centralWidget()
        if type(widget) is StartupWidget :
            # don't allow this if we are analyzing files
            if widget.analyze_thread :
                QApplication.beep()
                evt.ignore()
                return
        else :
            # check if we should confirm the exit
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

    def on_add_card( self ) :
        dlg = AddCardDialog( self )
        rc = dlg.exec()
        if rc == QDialog.Accepted :
            # add a new tab for the selected card
            card = dlg.selected_card
            if not card :
                assert False
                return
            w = AslCardWidget( card )
            index = self.tab_widget.addTab( w , card.name )
            self.tab_widget.setCurrentIndex( index )
