import os

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog , QListWidgetItem

import asl_cards.db as db
from constants import *
import globals

# ---------------------------------------------------------------------

class AddCardDialog( QDialog ) :
    """Allow the user to select an ASL card, based on nationality & card type."""

    def __init__( self , parent ) :
        # initialize
        self.selected_card = None
        super(AddCardDialog,self).__init__( parent=parent )
        # initialize the dialog
        uic.loadUi( os.path.join(globals.base_dir,"ui/add_card_dialog.ui") , self )
        self.setMinimumSize( self.size() )
        self.lb_cards.setSortingEnabled( True )
        w = self.buttons_widget
        self.xmargin = w.x()
        self.ymargin = self.size().height() - (w.y() + w.height())
        # load the dialog
        for nationality in globals.cards :
            self.cbo_nationality.addItem( nationality )
        # connect our handlers
        self.cbo_nationality.currentIndexChanged[str].connect( self.on_nationality_changed )
        self.ok_button.clicked.connect( self.on_ok )
        for rb in [self.rb_vehicles,self.rb_ordnance] :
            rb.clicked.connect( self.on_card_type_changed )
        # select the initial nationality (this will load the rest of the dialog)
        self.cbo_nationality.setCurrentIndex( 0 )
        self.on_nationality_changed( self.cbo_nationality.itemText(0) )

    def on_ok( self ) :
        # accept the currently selected card
        item = self.lb_cards.currentItem()
        self.selected_card = item.data(Qt.UserRole) if item else None
        self.accept()

    def on_nationality_changed( self , val ) :
        """Update the dialog when the active nationality is changed."""
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
        """Update the dialog when the active card type is changed."""
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

    def resizeEvent( self , evt ) :
        # handle the event
        w = self.buttons_widget
        self.buttons_widget.setGeometry(
            self.xmargin , self.size().height() - self.ymargin - w.height() ,
            self.size().width() - 2*self.xmargin , w.height()
        )
        w = self.lb_cards
        w.resize( self.size().width() - 2*self.xmargin , self.buttons_widget.y() - w.y() )
