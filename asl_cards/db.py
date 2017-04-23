import sys
import os
from sqlalchemy import sql , orm , create_engine
from sqlalchemy import Column , ForeignKey , String , Integer , Binary

# ---------------------------------------------------------------------

db_engine = None
db_session = None

# ---------------------------------------------------------------------

from sqlalchemy.ext.declarative import declarative_base
DbBase = declarative_base()

class DbBaseMixin :
    """Add helper functions to database model classes."""
    def _init_db_object( self , **kwargs ) :
        """Initialize ourself from a list of attributes."""
        for k,v in kwargs.items() :
            setattr( self , k ,v )
    def _to_string( self , cls ) :
        keys = orm.class_mapper( cls ).c.keys()
        buf = "|".join(
            "{}={}".format( k , getattr(self,k) ) for k in keys
        )
        return "{}[{}]".format( type(self).__name__ , buf )

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class AslCard( DbBase , DbBaseMixin ) :
    """Models an ASL card."""
    __tablename__ = "card"
    card_id = Column( Integer , primary_key=True , autoincrement=True )
    tag = Column( String(40) )
    nationality = Column( String(40) )
    name = Column( String(40) )
    page_id = Column( Integer )
    page_pos = Column( Integer )
    card_image = orm.relationship( "AslCardImage" , uselist=False , backref="parent_card" , cascade="all,delete" )

    def __init__( self , **kwargs ) : self._init_db_object( **kwargs )
    def __str__( self ) : return self._to_string(AslCard)

class AslCardImage( DbBase , DbBaseMixin ) :
    """Models the image data for an ASL card."""
    __tablename__ = "card_image"
    card_id = Column( Integer , ForeignKey("card.card_id",ondelete="CASCADE") , primary_key=True )
    image_data = Column( Binary() )
    # nb: a relationship for "card_image" is created by AslCard

    def __init__( self , **kwargs ) : self._init_db_object( **kwargs )
    def __str__( self ) :
        return "AslCardImage[card_id={}|#bytes={}]".format( self.card_id , len(self.image_data) )

# ---------------------------------------------------------------------

def open_database( fname ) :
    """Open the database."""

    # open the database
    is_new = not os.path.isfile( fname )
    conn_string = "sqlite:///{}".format( fname )
    global db_engine
    db_engine = create_engine( conn_string , convert_unicode=True )
    #db_engine.echo = True 

    # initialize our session
    global db_session
    db_session = orm.create_session( bind=db_engine , autocommit=False )
    db_session.execute( "PRAGMA foreign_keys = on" ) # nb: foreign keys are disabled by default in SQLite

    # check if we are creating a new database
    if is_new :
        # yup - make it so
        DbBase.metadata.create_all( db_engine )

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def add_cards( cards ) :
    """Build the database from the specified cards."""
    # clear the database
    db_session.query(AslCard).delete()
    # add the cards
    for c in cards :
        db_session.add( c )
    # commit the changes
    db_session.commit()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def dump_database() :
    """Dump the database."""
    # dump the ASL cards
    query = db_session.query( AslCard )
    for card in query.all() :
        print( card )
        if card.card_image :
            print( "- {}".format( card.card_image ) )