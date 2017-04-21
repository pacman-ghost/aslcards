import os
import re
from collections import namedtuple

from pdfminer.pdfinterp import PDFResourceManager , PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams , LTTextBoxHorizontal
from pdfminer.pdfpage import PDFPage

# ---------------------------------------------------------------------

AslCard = namedtuple(
    "AslCard" ,
    [ "page_id" , "page_pos" , "tag" , "nationality" , "name" ]
)

# ---------------------------------------------------------------------

class PdfParser:

    def __init__( self , progress=None ) :
        # initialize
        self.progress = progress

    def parse_file( self , fname ) :
        """Extract the cards from a PDF file."""
        # initialize
        rmgr = PDFResourceManager()
        laparams = LAParams()
        dev = PDFPageAggregator( rmgr , laparams=laparams )
        interp = PDFPageInterpreter( rmgr , dev )
        # process the file
        cards = []
        with open(fname,"rb") as fp :
            self._progress( 0 , "Loading file: {}".format( fname ) )
            pages = list( PDFPage.get_pages( fp ) )
            for page_no,page in enumerate(pages) :
                self._progress( float(page_no)/len(pages) , "Processing page {}...".format( 1+page_no ) )
                page_cards = self._parse_page( cards , interp , page_no , page )
                cards.extend( page_cards )
        self._progress( 1.0 , "Done." )
        return cards

    def _parse_page( self , cards , interp , page_no , page ) :
        """Extract the cards from a PDF page."""
        cards = []
        interp.process_page( page )
        lt_page = interp.device.get_result()
        pending_card = None
        for item in lt_page :
            if type(item) is not LTTextBoxHorizontal : continue
            item_text = item.get_text().strip()
            if item_text.startswith( ("Vehicle","Ordnance") ) :
                vals = item_text.split( "\n" )
                page_pos = 0 if item.y0 > lt_page.height/2 else 1
                if len(vals) >= 3 :
                    card = AslCard(
                        lt_page.pageid , page_pos ,
                        _tidy(vals[0]).replace("# ","#") ,
                        _tidy(vals[1]) ,
                        _tidy(vals[2])
                    )
                    self._progress( None , "Found card: {}".format( card ) )
                    cards.append( card )
                    pending_card = None
                else :
                    pending_card = [
                        lt_page.pageid , page_pos ,
                        _tidy(vals[0]).replace("# ","#") ,
                        _tidy(vals[1])
                    ]
            elif pending_card :
                pending_card.append( _tidy( item.get_text().strip() ) )
                card = AslCard( *pending_card )
                self._progress( None , "Found card: {}".format( card ) )
                cards.append( card )
                pending_card = None
        return cards

    def parse_dir( self , dname , progress=None ) :
        """Parse all PDF's in a directory."""
        fcards = {}
        for fname in os.listdir(dname) :
            if os.path.splitext(fname)[1].lower() != ".pdf" :
                continue
            cards = self.parse_file( os.path.join(dname,fname) )
            fcards[fname] = cards
        return fcards

    def _progress( self , progress , msg ) :
        """Call the progress callback."""
        if self.progress :
            self.progress( progress , msg )

# ---------------------------------------------------------------------

_tidy_regex = re.compile( r"[,.()+-]" )
def _tidy( val ) : return _tidy_regex.sub(" ",val).strip()
