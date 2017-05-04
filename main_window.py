import sys
import os

from PyQt5.QtCore import Qt , QPoint , QSize
from PyQt5.QtWidgets import QApplication , QMainWindow , QVBoxLayout , QHBoxLayout , QWidget , QTabWidget , QLabel , QMenu
from PyQt5.QtWidgets import QMessageBox , QAction
from PyQt5.QtGui import QPainter , QPixmap , QIcon , QBrush

import asl_cards.db as db
from asl_cards import natinfo
from constants import *
import globals
from add_card_widget import AddCardWidget
from startup_widget import StartupWidget
from about_widget import AboutWidget

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
        self.setMinimumSize( 600 , 400 )
        # initialize the menu
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu( "&File" )
        self.add_card_action = QAction( "&Add" , self )
        self.add_card_action.setEnabled( False )
        self.add_card_action.setShortcut( "Ctrl+A" )
        self.add_card_action.setStatusTip( "Add an ASL Card." )
        self.add_card_action.triggered.connect( self.on_add_card )
        file_menu.addAction( self.add_card_action )
        self.close_tab_action = QAction( "&Close" , self )
        self.close_tab_action.setShortcut( "Ctrl+W" )
        self.close_tab_action.setStatusTip( "Close the current tab." )
        self.close_tab_action.triggered.connect( self.on_close_tab )
        file_menu.addAction( self.close_tab_action )
        action = QAction( "E&xit" , self )
        action.setStatusTip( "Close the program." )
        action.triggered.connect( self.close )
        file_menu.addAction( action )
        self.help_menu = menu_bar.addMenu( "&Help" )
        about_action = QAction( "&About" , self )
        about_action.setStatusTip( "About this program." )
        about_action.triggered.connect( self.on_about )
        self.help_menu.addAction( about_action )
        # restore the window geometry
        buf = globals.app_settings.value( MAINWINDOW_GEOMETRY )
        if buf :
            self.restoreGeometry( buf )
        else :
            self.resize( 1 , 1 ) # nb: the layout manager will set the correct size
        # show the startup form
        self.tab_widget = None
        self.setCentralWidget(
            StartupWidget( db_fname , parent=self )
        )
        self._update_ui()

    def on_about_to_show_view_menu( self ) :
        # figure out what nationalities are currently open
        nats = []
        for i in range(0,self.tab_widget.count()) :
            widget = self.tab_widget.widget( i )
            if type(widget) is not AslCardWidget : continue
            card = widget.card
            if card.nationality not in nats :
                nats.append( card.nationality )
        # rebuild the View menu
        def cycle( nat ) :
            # cycle to the nationality's next card
            index = start_index = self.tab_widget.currentIndex()
            while True :
                index = (index + 1) % self.tab_widget.count()
                if index == start_index :
                    break
                widget = self.tab_widget.widget( index )
                if type(widget) is AslCardWidget and widget.card.nationality == nat :
                    self.tab_widget.setCurrentIndex( index )
                    break
        self.view_menu.clear()
        for nat in nats :
            action = QAction( "Next {} card".format(nat) , self )
            fname = natinfo.get_flag( nat )
            if fname :
                action.setIcon( QIcon(fname) )
            accel = natinfo.get_accel_for_nat( nat )
            if accel :
                action.setShortcut( "Ctrl+{}".format( accel ) )
            action.triggered.connect( lambda qthack,nat=nat: cycle(nat) )
            self.view_menu.addAction( action )

    def start_main_app( self , db_fname ) :
        """Start the main app."""
        # we can now close the startup widget and replace it with the main tab widget
        self.tab_widget = QTabWidget( self )
        self.tab_widget.setTabsClosable( True )
        self.tab_widget.setMovable( True )
        self.tab_widget.tabCloseRequested.connect( self.on_tab_close_requested )
        self.setCentralWidget( self.tab_widget )
        # open the database
        db.open_database( db_fname , False )
        globals.cards = db.load_cards()
        # show the View menu
        self.view_menu = QMenu( "&View" )
        self.menuBar().insertMenu( self.help_menu.menuAction() , self.view_menu )
        self.view_menu.aboutToShow.connect( self.on_about_to_show_view_menu )
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

    def on_tab_close_requested( self , index ) :
        """Handle the tab close request."""
        self.tab_widget.removeTab( index )

    def closeEvent( self , evt ) :
        """Handle window close."""
        # confirm the close
        widget = self.centralWidget()
        if type(widget) is StartupWidget :
            # don't allow this if we are analyzing files
            if widget.analyze_thread :
                MainWindow.show_info_msg( "Please cancel the analysis first." )
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
        globals.app_settings.setValue( MAINWINDOW_GEOMETRY , self.saveGeometry() )

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
        widget.lb_cards.setFocus()
    def on_add_card_accepted( self , card ) :
        """Handle the user's card selection."""
        index = self._find_add_card_tab()
        assert index is not None
        self.tab_widget.removeTab( index )
        fname = natinfo.get_flag( card.nationality )
        if fname :
            widget = self.tab_widget.insertTab( index , AslCardWidget(card) , QIcon(fname) , card.name )
        else :
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

    def on_about( self ) :
        """Show an About box."""
        AboutWidget( self ).exec_()
