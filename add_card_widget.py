import os

from PyQt5 import uic
from PyQt5.QtCore import Qt , pyqtSignal
from PyQt5.QtWidgets import QWidget , QListWidgetItem
from PyQt5.QtGui import QIcon

import asl_cards.db as db
from asl_cards.db import AslCard
from asl_cards import natinfo
from constants import *
import globals

# ---------------------------------------------------------------------

class AddCardWidget( QWidget ) :
    """Allow the user to select an ASL card, based on nationality & card type."""

    last_nationality = -1 # nb: the last nationality selected
    last_card_type = db.TAGTYPE_VEHICLE # nb: the last card type selected

    # define our signals
    accepted_signal = pyqtSignal( AslCard , name="accepted" )
    cancelled_signal = pyqtSignal( name="cancelled" )

    def __init__( self , parent ) :
        # initialize
        super().__init__( parent=parent )
        # initialize the widget
        uic.loadUi( os.path.join(globals.base_dir,"ui/add_card_widget.ui") , self )
        self.lb_cards.setSortingEnabled( True )
        # load the widget
        for nat in globals.cards :
            fname = natinfo.get_flag( nat )
            if fname :
                self.cbo_nationality.addItem( QIcon(fname) , nat )
            else :
                self.cbo_nationality.addItem( nat )
        # connect our handlers
        self.cbo_nationality.currentIndexChanged[str].connect( self.on_nationality_changed )
        self.lb_cards.itemDoubleClicked.connect( self.on_card_doubleclicked )
        self.le_filter.textChanged.connect( self.on_filter_textChanged )
        self.ok_button.clicked.connect( self.on_ok )
        self.cancel_button.clicked.connect( self.on_cancel )
        for rb in [self.rb_vehicles,self.rb_ordnance] :
            rb.clicked.connect( self.on_card_type_changed )
        # select the initial nationality (this will load the rest of the widget)
        if AddCardWidget.last_nationality >= 0 :
            self.cbo_nationality.setCurrentIndex( AddCardWidget.last_nationality )
        else :
            self.cbo_nationality.setCurrentIndex( 0 )
        self.on_nationality_changed( self.cbo_nationality.currentText() )

    def _reload_cards( self , focus ) :
        """Reload the available cards."""
        # initialize
        self.lb_cards.clear()
        # figure out what type of cards to show
        if self.rb_vehicles.isChecked() :
            card_type = db.TAGTYPE_VEHICLE
        elif self.rb_ordnance.isChecked() :
            card_type = db.TAGTYPE_ORDNANCE
        else :
            return
        cards = globals.cards[ self.cbo_nationality.currentText() ]
        cards = cards.get( card_type )
        if cards is None :
            return
        # prepare for filtering
        def filter_val( str ) :
            return str.replace(" ","").lower()
        filter_text = filter_val( self.le_filter.text() )
        # reload the available cards
        for card in cards :
            if filter_text and filter_val(card.name).find( filter_text ) < 0 :
                continue
            item = QListWidgetItem( card.name )
            item.setData( Qt.UserRole , card )
            self.lb_cards.addItem( item )
        self.lbl_cards.setText(
            "<html><b>&Cards:</b>{}</html>".format( " <small><i>(filtered)</i></small>" if filter_text else "" )
        )
        self.lb_cards.setCurrentRow( 0 )
        if focus :
            self.lb_cards.setFocus()

    def on_ok( self ) :
        """Accept the currently selected card."""
        item = self.lb_cards.currentItem()
        card = item.data(Qt.UserRole) if item else None
        self.accepted_signal.emit( card )
        AddCardWidget.last_nationality = self.cbo_nationality.currentIndex()
        AddCardWidget.last_card_type = db.TAGTYPE_VEHICLE if self.rb_vehicles.isChecked() else db.TAGTYPE_ORDNANCE

    def on_cancel( self ) :
        """Cancel the widget."""
        self.cancelled_signal.emit()

    def on_nationality_changed( self , val ) :
        """Update the widget when the active nationality is changed."""
        # reload the available cards for the selected nationality
        cards = globals.cards[ val ]
        self.lb_cards.clear()
        # update the vehicle/ordnance radio boxes
        self.rb_vehicles.setEnabled( db.TAGTYPE_VEHICLE in cards )
        self.rb_ordnance.setEnabled( db.TAGTYPE_ORDNANCE in cards )
        if self.rb_vehicles.isChecked() :
            if not self.rb_vehicles.isEnabled() :
                self.rb_ordnance.setChecked( True )
        elif self.rb_ordnance.isChecked() :
            if not self.rb_ordnance.isEnabled() :
                self.rb_vehicles.setChecked( True )
        else :
            if AddCardWidget.last_card_type == db.TAGTYPE_VEHICLE and self.rb_vehicles.isEnabled() :
                self.rb_vehicles.setChecked( True )
            elif self.rb_ordnance.isEnabled() :
                self.rb_ordnance.setChecked( True )
        # reload the cards
        self.le_filter.setText( "" )
        self._reload_cards( True )

    def on_card_type_changed( self ) :
        """Update the widget when the active card type is changed."""
        self.le_filter.setText( "" )
        self._reload_cards( True )

    def on_filter_textChanged( self , val ) :
        """Update the widget when the filter text is changed."""
        self._reload_cards( False )

    def on_card_doubleclicked( self , item ) :
        # handle the event
        if item :
            self.on_ok()

    def keyPressEvent( self , evt ) :
        # handle the event
        if evt.key() == Qt.Key_Return :
            if not self.lb_cards.currentItem() :
                QApplication.beep()
            self.on_ok()
