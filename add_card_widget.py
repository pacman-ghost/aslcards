import os

from PyQt5 import uic
from PyQt5.QtCore import Qt , pyqtSignal
from PyQt5.QtWidgets import QWidget , QListWidgetItem

import asl_cards.db as db
from asl_cards.db import AslCard
from constants import *
import globals

# ---------------------------------------------------------------------

class AddCardWidget( QWidget ) :
    """Allow the user to select an ASL card, based on nationality & card type."""

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
        for nationality in globals.cards :
            self.cbo_nationality.addItem( nationality )
        # connect our handlers
        self.cbo_nationality.currentIndexChanged[str].connect( self.on_nationality_changed )
        self.lb_cards.itemDoubleClicked.connect( self.on_card_doubleclicked )
        self.ok_button.clicked.connect( self.on_ok )
        self.cancel_button.clicked.connect( self.on_cancel )
        for rb in [self.rb_vehicles,self.rb_ordnance] :
            rb.clicked.connect( self.on_card_type_changed )
        # select the initial nationality (this will load the rest of the widget)
        self.cbo_nationality.setCurrentIndex( 0 )
        self.on_nationality_changed( self.cbo_nationality.itemText(0) )

    def on_ok( self ) :
        """Accept the currently selected card."""
        item = self.lb_cards.currentItem()
        card = item.data(Qt.UserRole) if item else None
        self.accepted_signal.emit( card )

    def on_cancel( self ) :
        """Cancel the widget."""
        self.cancelled_signal.emit()

    def on_nationality_changed( self , val ) :
        """Update the widget when the active nationality is changed."""
        # reload the available cards for the selected nationality
        cards = globals.cards[ val ]
        self.lb_cards.clear()
        # update the vehicle/ordnance radio boxes
        if self.rb_vehicles.isChecked() :
            curr_rb = self.rb_vehicles
        elif self.rb_ordnance.isChecked() :
            curr_rb = self.rb_ordnance
        else :
            curr_rb = None
        self.rb_vehicles.setEnabled( db.TAGTYPE_VEHICLE in cards )
        self.rb_ordnance.setEnabled( db.TAGTYPE_ORDNANCE in cards )
        if curr_rb is None or not curr_rb.isEnabled() :
            for rb in [self.rb_vehicles,self.rb_ordnance] :
                if rb.isEnabled() :
                    rb.setChecked( True )
                    break
        # reload the cards
        self.on_card_type_changed()

    def on_card_type_changed( self ) :
        """Update the widget when the active card type is changed."""
        self.lb_cards.clear()
        # figure out what type of cards to show
        if self.rb_vehicles.isChecked() :
            card_type = db.TAGTYPE_VEHICLE
        elif self.rb_ordnance.isChecked() :
            card_type = db.TAGTYPE_ORDNANCE
        else :
            return
        # reload the available cards
        cards = globals.cards[ self.cbo_nationality.currentText() ]
        cards = cards.get( card_type )
        if cards is None :
            assert False
            return
        for card in cards :
            item = QListWidgetItem( card.name )
            item.setData( Qt.UserRole , card )
            self.lb_cards.addItem( item )
        self.lb_cards.setCurrentRow( 0 )
        self.lb_cards.setFocus()

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
