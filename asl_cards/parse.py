import sys
import os
import re
import itertools
import tempfile
import locale
from collections import namedtuple

from PyQt5.QtWidgets import QMessageBox

from pdfminer.pdfinterp import PDFResourceManager , PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams , LTTextBoxHorizontal
from pdfminer.pdfpage import PDFPage

import ghostscript
from PIL import Image , ImageChops

from asl_cards.db import AslCard , AslCardImage

# ---------------------------------------------------------------------

class AnalyzeCancelledException( RuntimeError ) :
    def __init__( self ) :
        super().__init__( "Cancelled." )

# ---------------------------------------------------------------------

class PdfParser:

    def __init__( self , index_dir , progress=None , progress2=None , on_ask=None , on_error=None ) :
        # initialize
        self.index_dir = index_dir
        self.progress = progress # nb: for tracking file progress
        self.progress2 = progress2 # nb: for tracking page progress within a file
        self.on_ask = on_ask # nb: for asking the user something during processing
        self.on_error = on_error # nb: for showing the user an error message
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
        for file_no,fname in enumerate(fnames) :
            if self.cancelling : raise AnalyzeCancelledException()
            try :
                file_cards = self._do_parse_file( float(file_no)/len(fnames) , fname , max_pages , images )
            except AnalyzeCancelledException as ex :
                raise
            except Exception as ex :
                # notify the caller of the error
                if not self.on_error :
                    raise
                self.on_error(
                    "An error occured while processing {}:\n\n{}\n\nThis file will be ignored.".format(
                        os.path.split(fname)[1] , str(ex)
                    )
                )
                continue
            if file_cards :
                cards.extend( file_cards )
        self._progress( 1.0 , "Done." )
        # filter out placeholder cards
        cards = [ c for c in cards if c.nationality != "_unused_" and c.name != "_unused_" ]
        return cards

    def _do_parse_file( self , pval , fname , max_pages , images ) :
        cards = []
        # check if we have an index for this file
        # NOTE: We originally tried to get the details of each card by parsing the PDF files but unfortunately,
        # the text was coming out garbled. We allow corrections to be supplied in an external file, but if we're
        # going to do that, we might as well not bother parsing the PDF :-/ (especially since it's so insanely slow).
        split = os.path.split( fname )
        index_fname = os.path.join(
            self.index_dir if self.index_dir else "" ,
            os.path.splitext(split[1])[0]+".txt"
        )
        if os.path.isfile( index_fname ) :
            # yup - just generate the AslCard's from that
            # NOTE: It would be nice to store these files as JSON, or something similar, but we want
            # to keep them easy for end-users to change, if some values need to be tweaked.
            self._progress( pval , "Reading card details from {}...".format( os.path.split(index_fname)[1] ) )
            for line_buf in open(index_fname,"r") :
                line_buf = line_buf.strip()
                if line_buf == "" or line_buf.startswith(("#","'",";","//")) :
                    continue
                fields = line_buf.split( "|" )
                if len(fields) != 3 :
                    raise RuntimeError( "Invalid index line: {}".format( line_buf ) )
                fields = [ f.strip() for f in fields ]
                ncards = len( cards )
                cards.append( AslCard(
                    card_tag = fields[0] ,
                    nationality = fields[1] ,
                    name = fields[2] ,
                    page_id = 1 + ncards/2 ,
                    page_pos = ncards % 2
                ) )
        else :
            # ask the user if they want to try parsing the PDF
            if self.on_ask :
                rc = self.on_ask(
                    "Can't find an index file for {}.\n\nDo you want to try parsing the PDF (slow and unreliable)?".format(
                        os.path.split( fname )[ 1 ]
                    ) ,
                    QMessageBox.Yes | QMessageBox.No , QMessageBox.No
                )
                if rc != QMessageBox.Yes :
                    return None
            # extract each AslCard from the file
            # NOTE: Some of the PDF's have cards that have not been filled out - we detect this correctly (because
            # they don't have a "Vehicle" or "Ordnance" tag, but we barf later because the image extractor thinks
            # they're a valid card, and so we get a different number of cards vs. images.
            # It's not really worth fixing this, since we're now using index files instead of extracting the info
            # from the PDF's (because extraction is giving such poor results :-/).
            self._progress( pval , "Analyzing {}...".format( os.path.split(fname)[1] ) )
            rmgr = PDFResourceManager()
            laparams = LAParams()
            dev = PDFPageAggregator( rmgr , laparams=laparams )
            interp = PDFPageInterpreter( rmgr , dev )
            with open(fname,"rb") as fp :
                pages = list( PDFPage.get_pages( fp ) )
                for page_no,page in enumerate(pages) :
                    if self.cancelling : raise AnalyzeCancelledException()
                    self._progress2( float(page_no) / len(pages) )
                    page_cards = self._parse_page( cards , interp , page_no , page )
                    cards.extend( page_cards )
                    if max_pages > 0 and 1+page_no >= max_pages :
                        break
        # extract the card images
        if images :
            self._progress( pval , "Extracting images from {}...".format( os.path.split(fname)[1] ) )
            card_images = self._extract_images( fname , max_pages )
            if len(cards) != len(card_images) :
                raise RuntimeError(
                    "Card mismatch in {}: found {} cards, {} card images.".format(
                        fname , len(cards) , len(card_images)
                    )
                )
            for i in range(0,len(cards)) :
                if self.cancelling : raise AnalyzeCancelledException()
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
            if self.cancelling : raise AnalyzeCancelledException()
            if type(item) is not LTTextBoxHorizontal : continue
            item_text = item.get_text().strip()
            if item_text.startswith( ("Vehicle","Ordnance") ) :
                info_boxes.append( [item] )
        # get the details from each info box
        for item in lt_page :
            if self.cancelling : raise AnalyzeCancelledException()
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
            if self.cancelling : raise AnalyzeCancelledException()
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
        return card_images

    def _crop_image( self , img , bbox , fname ) :
        # crop the image
        rgn = img.crop( bbox )
        # trim the cropped region
        bgd_col = img.getpixel( (0,0) )
        bgd_img = Image.new( img.mode , img.size , bgd_col )
        diff = ImageChops.difference( rgn , bgd_img )
        #diff = ImageChops.add(diff, diff, 2.0, -100)
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
