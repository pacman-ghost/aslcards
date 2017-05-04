import os

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog , QFrame
from PyQt5.QtGui import QPixmap

from constants import *
import globals

# ---------------------------------------------------------------------

class AboutWidget( QDialog ) :
    """Show an About box."""

    def __init__( self , parent ) :
        # initialize
        super().__init__()
        # initialize the widget
        uic.loadUi( os.path.join(globals.base_dir,"ui/about_widget.ui") , self )
        self.setMinimumSize( self.size() )
        self.lbl_app_icon.setPixmap(
            QPixmap( os.path.join( globals.base_dir , "resources/app.ico" ) )
        )
        self.lbl_app_icon.setFrameStyle( QFrame.NoFrame )
        self.lbl_app_name.setText( "<html> {} <small>({})</small> </html>".format( APP_NAME , APP_VERSION ) )
        self.lbl_avatar.setPixmap(
            QPixmap( os.path.join( globals.base_dir , "resources/pacman-ghost.png" ) ) \
            .scaled( self.lbl_avatar.size() )
        )
        self.lbl_avatar.setFrameStyle( QFrame.NoFrame )
        # load the dialog
        try :
            with open( os.path.join( globals.base_dir , "license.txt" ) , "r" ) as fp :
                buf = fp.read()
        except Exception as ex :
            buf = str(ex)
        self.lbl_license.setText( buf )
        self.lbl_license.setFrameStyle( QFrame.NoFrame )
        # connect our handlers
        self.btn_ok.clicked.connect( self.close )

