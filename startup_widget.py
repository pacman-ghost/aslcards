import os

from PyQt5 import uic
from PyQt5.QtCore import Qt , QMetaObject , QThread , pyqtSignal , pyqtSlot , Q_ARG , Q_RETURN_ARG
from PyQt5.QtWidgets import QWidget , QFrame , QFileDialog , QMessageBox
from PyQt5.QtGui import QPixmap , QIcon , QMovie

from asl_cards.parse import PdfParser
import asl_cards.db as db

from constants import *
import globals

# ---------------------------------------------------------------------

class AnalyzeThread( QThread ) :

    # define our signals
    progress_signal = pyqtSignal( float , str , name="progress" )
    progress2_signal = pyqtSignal( float , name="progress2" )
    completed_signal = pyqtSignal( str , name="completed" )

    def __init__( self , cards_dir , image_res , db_fname ) :
        # initialize
        super().__init__()
        self.cards_dir = cards_dir
        self.image_res = image_res
        self.db_fname = db_fname

    def run( self ) :
        """Run the worker thread."""
        try :
            # initialize
            if os.path.isfile( self.db_fname ) :
                os.unlink( self.db_fname )
            db.open_database( self.db_fname , True )
            # parse the files
            total_cards = 0
            def on_file_completed( fname , cards ) :
                # save the extracted cards
                db.add_cards( cards )
                nonlocal total_cards
                total_cards += len(cards)
                del cards[:]
            self.parser = PdfParser(
                os.path.join( globals.base_dir , "index" ) ,
                progress = lambda pval,msg: self.progress_signal.emit( -1 if pval is None else pval , msg ) ,
                progress2 = lambda pval: self.progress2_signal.emit( pval ) ,
                on_file_completed = on_file_completed ,
                on_ask = self.on_ask ,
                on_error = self.on_error ,
            )
            cards = self.parser.parse( self.cards_dir , image_res=self.image_res )
            assert len(cards) == 0 # nb: on_file_completed() del'ed everything
            if total_cards <= 0 :
                raise RuntimeError( "No cards were found." )
        except Exception as ex :
            # notify slots that something went wrong
            if globals.debug_settings.value("Debug/LogAnalyzeExceptions",type=bool) :
                import traceback
                traceback.print_exc()
            self.completed_signal.emit( str(ex) )
        else :
            # notify slots that we've finished
            self.completed_signal.emit( "" )

    def on_error( self , msg ) :
        """Show the user an error message."""
        # NOTE: We are running in a worker thread, so we need to delegate showing the message box
        # to the GUI thread.
        QMetaObject.invokeMethod(
            StartupWidget._instance , "on_error" , Qt.BlockingQueuedConnection ,
            Q_ARG( str , msg )
        )

    def on_ask( self , msg , btns , default ) :
        """Ask the user a question."""
        # NOTE: We are running in a worker thread, so we need to delegate showing the message box
        # to the GUI thread.
        retarg = Q_RETURN_ARG( QMessageBox.StandardButton )
        QMetaObject.invokeMethod(
            StartupWidget._instance , "on_ask" , Qt.BlockingQueuedConnection ,
            retarg ,
            Q_ARG( str , msg ) ,
            Q_ARG( QMessageBox.StandardButtons , btns ) ,
            Q_ARG( QMessageBox.StandardButton , default ) ,
        )
        # FIXME! How do we get the return value?! :-/
        return StartupWidget._on_ask_retval

# ---------------------------------------------------------------------

class StartupWidget( QWidget ) :
    """This form lets the user initialize a new database, or load an existing one."""

    _instance = None

    def __init__( self , db_fname , parent=None ) :
        # initialize
        super(StartupWidget,self).__init__( parent=parent )
        assert StartupWidget._instance is None
        StartupWidget._instance = self
        self.analyze_thread = None
        # FUDGE! Workaround recursive import's :-/
        global MainWindow
        from main_window import MainWindow
        # initialize the widget
        uic.loadUi( os.path.join(globals.base_dir,"ui/startup_widget.ui") , self )
        self.setMinimumSize( self.size() )
        self.frm_analyze_progress.hide()
        # NOTE: The animation was created at loading.io:
        #   color1=#047ab3 ; color2=#83bfdc ; bgd=#ffffff ; speed=2
        self.progress_animation = QMovie( os.path.join( globals.base_dir , "resources/progress.gif" ) )
        self.lbl_progress.setFrameStyle( QFrame.NoFrame )
        self.lbl_progress.setScaledContents( True )
        self.lbl_progress.setMovie( self.progress_animation )
        # initialize the widget
        self.lbl_analyze_icon.setPixmap(
            QPixmap( os.path.join( globals.base_dir , "resources/analyze.png" ) )
        )
        self.lbl_analyze_icon.setFrameStyle( QFrame.NoFrame )
        self.btn_cards_dir.setIcon(
            QIcon( os.path.join( globals.base_dir , "resources/dir_dialog.png" ) )
        )
        self.btn_save_db_fname.setIcon(
            QIcon( os.path.join( globals.base_dir , "resources/file_dialog.png" ) )
        )
        self.btn_analyze.setIcon(
            QIcon( os.path.join( globals.base_dir , "resources/analyze.png" ) )
        )
        self.btn_analyze.setText( " " + self.btn_analyze.text() )
        self.btn_cancel_analyze.setIcon(
            QIcon( os.path.join( globals.base_dir , "resources/stop.png" ) )
        )
        self.btn_cancel_analyze.setText( " " + self.btn_cancel_analyze.text() )
        # initialize the widget
        self.lbl_load_db_icon.setPixmap(
            QPixmap( os.path.join( globals.base_dir , "resources/load_db.png" ) )
        )
        self.lbl_load_db_icon.setFrameStyle( QFrame.NoFrame )
        self.btn_load_db_fname.setIcon(
            QIcon( os.path.join( globals.base_dir , "resources/file_dialog.png" ) )
        )
        self.btn_load_db.setIcon(
            QIcon( os.path.join( globals.base_dir , "resources/load_db.png" ) )
        )
        self.btn_load_db.setText( " " + self.btn_load_db.text() )
        # load the widget
        self.cbo_resolution.addItem( "150 dpi" )
        self.cbo_resolution.addItem( "300 dpi" )
        self.cbo_resolution.addItem( "600 dpi" )
        self.cbo_resolution.setCurrentIndex( 1 )
        if os.path.isfile( db_fname ) :
            self.le_load_db_fname.setText( db_fname )
        else :
            self.le_save_db_fname.setText( db_fname )
        # connect our handlers
        self.btn_cards_dir.clicked.connect( self.on_btn_cards_dir )
        self.btn_save_db_fname.clicked.connect( self.on_btn_save_db_fname )
        self.btn_analyze.clicked.connect( self.on_analyze )
        self.btn_load_db_fname.clicked.connect( self.on_btn_load_db_fname )
        self.btn_load_db.clicked.connect( self.on_btn_load_db )

    def on_btn_cards_dir( self ) :
        """Let the user browse to where the "ASL Cards" files are."""
        dname = self.le_cards_dir.text().strip()
        dname = QFileDialog.getExistingDirectory( self , "ASL Cards" , dname , QFileDialog.ShowDirsOnly )
        if not dname :
            return
        self.le_cards_dir.setText( dname )
        self.le_save_db_fname.setFocus()

    def on_btn_save_db_fname( self ) :
        """Let the user browse to where to save the database."""
        fname = self.le_save_db_fname.text().strip()
        fname = QFileDialog.getSaveFileName(
            self , "Save results" ,
            fname , "Database files (*.db)"
        )[ 0 ]
        if not fname :
            return
        self.le_save_db_fname.setText( fname )
        self.btn_analyze.setFocus()

    def on_analyze( self ) :
        """Analyze the ASL Card files."""
        # validate the "ASL Cards" directory
        cards_dir = self.le_cards_dir.text().strip()
        if not cards_dir :
            MainWindow.show_error_msg( "Please specify where the \"ASL Cards\" PDF files are." )
            self.le_cards_dir.setFocus()
            return
        if not os.path.isdir( cards_dir ) :
            MainWindow.show_error_msg( "Can't find the \"ASL Cards\" directory." )
            self.le_cards_dir.setFocus()
            return
        # validate the database filename
        fname = self.le_save_db_fname.text().strip()
        if not fname :
            MainWindow.show_error_msg( "Please choose where you want to save the results." )
            self.le_save_db_fname.setFocus()
            return
        # unload other settings
        image_res = int( self.cbo_resolution.currentText().split()[ 0 ] )
        # run the analysis (in a worker thread)
        self.frm_open_db.hide()
        self.frm_analyze_progress.show()
        self.progress_animation.start()
        self._update_analyze_ui( False )
        self.btn_cancel_analyze.setEnabled( True )
        self.btn_cancel_analyze.clicked.connect( self.on_cancel_analyze )
        self.analyze_thread = AnalyzeThread( cards_dir , image_res , fname )
        self.analyze_thread.progress_signal.connect( self.on_analyze_progress )
        self.analyze_thread.progress2_signal.connect( self.on_analyze_progress2 )
        self.analyze_thread.completed_signal.connect( self.on_analyze_completed )
        self.analyze_thread.start()

    def on_analyze_progress( self , pval , msg ) :
        """Update the analysis progress in the UI."""
        if pval >= 0 :
            self.pb_files.setValue( int( 100*pval + 0.5 ) )
        self.pb_files.setFormat( msg )
        self.pb_pages.setValue( 0 )
    def on_analyze_progress2( self , pval ) :
        """Update the analysis progress in the UI."""
        self.pb_pages.setValue( int( 100*pval + 0.5 ) )

    @pyqtSlot( str )
    def on_error( self , msg ) :
        """Show an error message box."""
        MainWindow.show_error_msg( msg )

    @pyqtSlot( str , QMessageBox.StandardButtons , QMessageBox.StandardButton , result=QMessageBox.StandardButton )
    def on_ask( self , msg , buttons , default ) :
        """Ask the user a question."""
        StartupWidget._on_ask_retval = MainWindow.ask( msg , buttons , default )
        return StartupWidget._on_ask_retval

    def on_cancel_analyze( self ) :
        """Cancel the analyze worker thread."""
        if not self.analyze_thread or self.analyze_thread.parser.cancelling :
            return
        rc = MainWindow.ask( "Cancel the analysis?" , QMessageBox.Ok|QMessageBox.Cancel , QMessageBox.Cancel )
        if rc != QMessageBox.Ok :
            return
        self.analyze_thread.parser.cancelling = True
        self.pb_files.setFormat( "Cancelling, please wait..." )
        self.btn_cancel_analyze.setEnabled( False )

    def on_analyze_completed( self , ex ) :
        # clean up
        self.analyze_thread = None
        self.progress_animation.stop()
        # check if the analysis failed
        if ex :
            MainWindow.show_error_msg( "Analyze failed:\n\n{}".format( ex  ) )
            self._update_analyze_ui( True )
            self.frm_analyze_progress.hide()
            self.le_cards_dir.setFocus()
            return
        # the analysis completed successully - start the main app
        self.pb_files.setValue( 100 )
        self.pb_pages.setValue( 100 )
        MainWindow.show_info_msg( "The \"ASL Cards\" files were analyzed successully." )
        self.parent().start_main_app( self.le_save_db_fname.text().strip() )

    def _update_analyze_ui( self , enable ) :
        # update the UI
        widgets = [ self.lbl_cards_dir , self.le_cards_dir, self.btn_cards_dir ]
        widgets.extend( [ self.lbl_resolution , self.cbo_resolution , self.lbl_resolution_hint ] )
        widgets.extend( [ self.lbl_save_db_fname , self.le_save_db_fname , self.btn_save_db_fname ] )
        widgets.append( self.btn_analyze )
        for w in widgets :
            w.setEnabled( enable )

    def on_btn_load_db_fname( self ) :
        """Let the user browse to a database to load."""
        fname = self.le_load_db_fname.text().strip()
        fname = QFileDialog.getOpenFileName(
            self , "Load database" ,
            fname , "Database files (*.db)"
        )[ 0 ]
        if not fname :
            return
        self.le_load_db_fname.setText( fname )
        self.btn_load_db.setFocus()

    def on_btn_load_db( self ) :
        """Load the database and start the main application."""
        fname = self.le_load_db_fname.text().strip()
        if not fname :
            MainWindow.show_error_msg( "Please choose a database to open." )
            self.le_load_db_fname.setFocus()
            return
        if not os.path.isfile( fname ) :
            MainWindow.show_error_msg( "Can't find this database file." )
            self.le_load_db_fname.setFocus()
            return
        # notify the main window it can start the main app
        self.parent().start_main_app( fname )
