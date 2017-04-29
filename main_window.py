import sys
import os

from PyQt5.QtCore import Qt , QPoint , QSize
from PyQt5.QtWidgets import QApplication , QMainWindow , QVBoxLayout , QHBoxLayout , QWidget , QTabWidget , QLabel
from PyQt5.QtWidgets import QMessageBox , QAction
from PyQt5.QtGui import QPainter , QPixmap , QIcon , QBrush

import asl_cards.db as db
from constants import *
import globals
from add_card_widget import AddCardWidget
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
        self.close_tab_action = QAction(" &Close" , self )
        self.close_tab_action.setShortcut( "Ctrl+W" )
        self.close_tab_action.setStatusTip( "Close the current tab." )
        self.close_tab_action.triggered.connect( self.on_close_tab )
        file_menu.addAction( self.close_tab_action )
        action = QAction( "E&xit" , self )
        action.setStatusTip( "Close the program." )
        action.triggered.connect( self.close )
        file_menu.addAction( action )
        self.tab_widget = None
        self._update_ui()
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
        QMessageBox.information( None , APP_NAME , msg )
    @staticmethod
    def show_error_msg( msg ) :
        """Show an error message."""
        QMessageBox.warning( None , APP_NAME , msg )
    @staticmethod
    def ask( msg , buttons , default ) :
        """Ask the user a question."""
        return QMessageBox.question( None , APP_NAME , msg , buttons , default )

    def _update_ui( self ) :
        """Update the window's UI."""
        self.close_tab_action.setEnabled( self.tab_widget.count() > 0 if self.tab_widget else False )

    def _find_add_card_tab( self ) :
        """Find the "add card" tab."""
        if self.tab_widget :
            for i in range(0,self.tab_widget.count()) :
                if type( self.tab_widget.widget(i) ) is AddCardWidget :
                    return i
        return None

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
                rc = self.ask( "Do you want to the close the program?" ,
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
        """Ask the user to select a new ASL card to show."""
        # check if the "add card" tab is already open
        index = self._find_add_card_tab()
        if index is not None :
            # yup - switch to it
            self.tab_widget.setCurrentIndex( index )
            return
        # nope - open it
        widget = AddCardWidget( self )
        widget.accepted_signal.connect( self.on_add_card_accepted )
        widget.cancelled_signal.connect( self.on_add_card_cancelled )
        index = self.tab_widget.insertTab(
            self.tab_widget.currentIndex() + 1 ,
            widget , "(new card)"
        )
        self.tab_widget.setCurrentIndex( index )
        self._update_ui()
        widget.setFocus() # FIXME! s.b. to first child control
    def on_add_card_accepted( self , card ) :
        """Handle the user's card selection."""
        index = self._find_add_card_tab()
        assert index is not None
        self.tab_widget.removeTab( index )
        widget = self.tab_widget.insertTab( index , AslCardWidget(card) , card.name )
        self.tab_widget.setCurrentIndex( index )
        self._update_ui()
    def on_add_card_cancelled( self ) :
        """Cancel the "add card" widget."""
        index = self._find_add_card_tab()
        assert index is not None
        self.tab_widget.removeTab( index )
        self._update_ui()

    def on_close_tab( self ) :
        """Close the current tab."""
        index = self.tab_widget.currentIndex()
        if index < 0 :
            QApplication.beep()
            return
        self.tab_widget.removeTab( index )
        self._update_ui()
