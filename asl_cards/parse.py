import sys
import os
import re
import itertools
import tempfile
import locale
from collections import namedtuple

from pdfminer.pdfinterp import PDFResourceManager , PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams , LTTextBoxHorizontal
from pdfminer.pdfpage import PDFPage

import ghostscript
from PIL import Image , ImageChops

from asl_cards.db import AslCard , AslCardImage

# ---------------------------------------------------------------------

class PdfParser:

    def __init__( self , progress=None  , progress2=None ) :
        # initialize
        self.progress = progress # nb: for tracking file progress
        self.progress2 = progress2 # nb: for tracking page progress within a file
        self.cancelling = False

    def parse( self , target , max_pages=-1 , images=True ) :
        """Extract the cards from a PDF file."""
        # locate the files we're going to parse
        if os.path.isfile( target ) :
            fnames = [ target ]
        else :
            fnames = [
                os.path.join( target , f )
                for f in os.listdir( target )
                if os.path.splitext( f )[1].lower() == ".pdf"
            ]
        # parse each file
        cards = []
        for fname in fnames :
            if self.cancelling : raise RuntimeError("Cancelled.")
            cards.extend( self._do_parse_file( fname , max_pages , images ) )
        return cards

    def _do_parse_file( self , fname , max_pages , images ) :
        # extract the details of each card
        rmgr = PDFResourceManager()
        laparams = LAParams()
        dev = PDFPageAggregator( rmgr , laparams=laparams )
        interp = PDFPageInterpreter( rmgr , dev )
        cards = []
        with open(fname,"rb") as fp :
            self._progress( 0 , "Analyzing {}...".format( os.path.split(fname)[1] ) )
            pages = list( PDFPage.get_pages( fp ) )
            for page_no,page in enumerate(pages) :
                if self.cancelling : raise RuntimeError("Cancelled.")
                self._progress2( float(page_no) / len(pages) )
                page_cards = self._parse_page( cards , interp , page_no , page )
                cards.extend( page_cards )
                if max_pages > 0 and 1+page_no >= max_pages :
                    break
        self._progress( 1.0 , "Done." )
        # extract the card images
        if images :
            card_images = self._extract_images( fname , max_pages )
            if len(cards) != len(card_images) :
                raise RuntimeError( "Found {} cards, {} card images.".format( len(cards) , len(card_images) ) )
            for i in range(0,len(cards)) :
                if self.cancelling : raise RuntimeError("Cancelled.")
                cards[i].card_image = AslCardImage( image_data=card_images[i] )
        return cards

    def _parse_page( self , cards , interp , page_no , page ) :
        """Extract the cards from a PDF page."""
        cards = []
        interp.process_page( page )
        lt_page = interp.device.get_result()
        # locate the info box for each card (in the top-left corner)
        info_boxes = []
        for item in lt_page :
            if self.cancelling : raise RuntimeError("Cancelled.")
            if type(item) is not LTTextBoxHorizontal : continue
            item_text = item.get_text().strip()
            if item_text.startswith( ("Vehicle","Ordnance") ) :
                info_boxes.append( [item] )
        # get the details from each info box
        for item in lt_page :
            if self.cancelling : raise RuntimeError("Cancelled.")
            if type(item) is not LTTextBoxHorizontal : continue
            # check if the next item could be part of an info box - it must be within the left/right boundary
            # of the first item (within a certain tolerance), and below it (but not too far)
            eps = 50 # left/right tolerance
            for info_box in info_boxes :
                if item.x0 >= info_box[0].x0 - eps and item.x1 <= info_box[0].x1 + eps \
                    and item.y1 < info_box[0].y1 and info_box[0].y0 - item.y1 < 50 :
                    # yup - save it
                    info_box.append( item )
        # generate an AslCard from each info box
        for info_box in info_boxes :
            card = self._make_asl_card( lt_page , info_box )
            cards.append( card )
        return cards

    def _make_asl_card( self , lt_page , items ) :
        # sort the items vertically
        items.sort( key=lambda i: i.y0 , reverse=True )
        # split out each line of item text
        item_texts = list( itertools.chain.from_iterable(
            i.get_text().strip().split("\n") for i in items
        ) )
        # ignore short lines
        item_texts = [ s for s in item_texts if len(s) >= 5 ]
        # generate the AslCard
        page_pos = 0 if items[0].y0 > lt_page.height/2 else 1
        return AslCard(
            card_tag = _tidy( item_texts[0] ).replace( "# ", "#" ) ,
            nationality = _tidy(item_texts[1]) if len(item_texts) > 1 else "" ,
            name = _tidy(item_texts[2]) if len(item_texts) > 2 else "" ,
            page_id = lt_page.pageid ,
            page_pos = page_pos ,
        )

    def _extract_images( self , fname , max_pages ) :
        """Extract card images from a file."""
        # extract each page from the PDF as an image
        fname_template = os.path.join( tempfile.gettempdir() , "asl_cards-%d.png" )
        resolution = 300 # pixels/inch
        args = [
            "_ignored_" , "-dQUIET" , "-dSAFER" , "-dNOPAUSE" ,
            "-sDEVICE=png16m" , "-r"+str(resolution) ,
            "-sOutputFile="+fname_template ,
        ]
        if max_pages > 0 :
            args.append( "-dLastPage={}".format(max_pages) )
        args.extend( [ "-f" , fname ] )
        # FIXME! clean up left-over temp files before we start
        args = [ s.encode(locale.getpreferredencoding()) for s in args ]
        # FIXME! stop GhostScript from issuing warnings (stdout).
        self._progress( 0 , "Extracting images from {}...".format( os.path.split(fname)[1] ) )
        ghostscript.Ghostscript( *args )
        # figure out how many files were created (so we can show progress)
        npages = 0
        for i in range(0,99999) :
            fname = fname_template % (1+i)
            if not os.path.isfile( fname ) :
                break
            npages += 1
        # extract the cards from each page
        card_images = []
        for page_no in range(0,npages) :
            if self.cancelling : raise RuntimeError("Cancelled.")
            # open the next page image
            self._progress2( float(page_no) / npages )
            fname = fname_template % (1+page_no)
            img = Image.open( fname )
            img_width , img_height = img.size
            # extract the cards (by splitting the page in half)
            fname2 = list( os.path.split( fname ) )
            fname2[1] = os.path.splitext( fname2[1] )
            ypos = img_height * 48 / 100
            buf1 , size1 = self._crop_image(
                img , (0,0,img_width,ypos) ,
                os.path.join( fname2[0] , fname2[1][0]+"a"+fname2[1][1] )
            )
            buf2 , size2 = self._crop_image(
                img , (0,ypos+1,img_width,img_height) ,
                os.path.join( fname2[0] , fname2[1][0]+"b"+fname2[1][1] )
            )
            # check if this is the last page, and it has just 1 card on it
            if page_no == npages-1 and size1[1] < 1000 and size2[1] < 1000 :
                # yup - extract it
                buf , _ = self._crop_image(
                    img , (0,0,img_width,img_height) ,
                    os.path.join( fname2[0] , fname2[1][0]+"a"+fname2[1][1] )
                )
                card_images.append( buf )
            else :
                # nope - save the extracted cards
                card_images.append( buf1 )
                card_images.append( buf2 )
            # clean up
            os.unlink( fname )
        self._progress( 1.0 , "Done." )
        return card_images

    def _crop_image( self , img , bbox , fname ) :
        # crop the image
        rgn = img.crop( bbox )
        # trim the cropped region
        bgd_col = img.getpixel( (0,0) )
        bgd_img = Image.new( img.mode , img.size , bgd_col )
        diff = ImageChops.difference( rgn , bgd_img )
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox :
            rgn = rgn.crop( bbox )
        # save the cropped image
        rgn.save( fname )
        with open( fname , "rb" ) as fp :
            buf = fp.read()
        os.unlink( fname )
        return buf , rgn.size

    def _progress( self , pval , msg ) :
        """Call the progress callback."""
        if self.progress :
            self.progress( pval , msg )
    def _progress2( self , pval ) :
        """Call the progress callback."""
        if self.progress2 :
            self.progress2( pval )

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

_tidy_regex = re.compile( r"[,.()+-]" )
def _tidy( val ) : return _tidy_regex.sub(" ",val).strip()
