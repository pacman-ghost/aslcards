import sys
import os
import unittest

base_dir = os.path.split( __file__ )[ 0 ]

sys.path.append( "../.." ) # fudge! need this to allow a script to run within a package :-/
from asl_cards.parse import PdfParser

# ---------------------------------------------------------------------

class TestCaseBase( unittest.TestCase ) :
    """Base for all test classes."""

    def _test_pdf_parser( self , fname , expected_cards ) :
        # parse the specified PDF
        fname2 = os.path.join( base_dir , fname )
        if not os.path.isfile( fname2 ) :
            raise RuntimeError( "Missing data file: {}".format( fname2 ) )
        pdf_parser = PdfParser(
            None ,
            #progress = lambda _,msg: print( msg , file=sys.stderr , flush=True )
        )
        cards = pdf_parser.parse( fname2 , image_res=None )
        # check the results
        if len(cards) != len(expected_cards) :
            raise RuntimeError( "{}: got {} cards, expected {}.".format( fname , len(cards) , len(expected_cards) ) )
        if len(cards) == 0 :
            return
        # get the attributes we're interested in
        card = expected_cards[0]
        attrs = [ a for a in dir(card) if not a.startswith("_") and not callable(getattr(card,a)) ]
        attrs.remove( "card_image" ) # this is messing things up :-/
        # compare the extracted cards with the expected results
        for i in range(0,len(cards)) :
            if not all( getattr(cards[i],a) == getattr(expected_cards[i],a) for a in attrs ) :
                raise RuntimeError( "{}: Card mismatch ({}): got {}, expected {}.".format( fname , i , cards[i] , expected_cards[i] ) )
