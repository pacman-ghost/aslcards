#!/usr/bin/env python3

import sys
import os
import unittest

from pdfminer.pdfparser import PDFSyntaxError

from _test_case_base import TestCaseBase
from asl_cards.parse import AslCard

# ---------------------------------------------------------------------

class TestSyntheticData( TestCaseBase ) :
    """Run tests using the synthetic PDF files.

    We test with some generated test files, since the real "ASL Cards" files need to purchased,
    so we can't keep them in source control.
    """

    def _test_pdf_parser( self , fname , expected_cards ) :
        """Test the PDF parser."""
        super()._test_pdf_parser( os.path.join("synthetic-data",fname) , expected_cards )

    def test_null_file( self ) :
        # try parsing a zero-byte file
        self.assertRaises(
            PDFSyntaxError ,
            self._test_pdf_parser , "null.pdf" , None
        )

    def test_empty_file( self ) :
        # try parsing an empty file
        self._test_pdf_parser( "empty.pdf" , [] )

    def test_1card_file( self ) :
        # try parsing a file with 1 card
        self._test_pdf_parser( "1-card.pdf" , [
            AslCard( page_id=1 , page_pos=0 , card_tag="Vehicle #1" , nationality="Moldovia" , name="Big Tank" ) ,
        ] )

    def test_2card_file( self ) :
        # try parsing a file with 2 cards
        self._test_pdf_parser( "2-cards.pdf" , [
            AslCard( page_id=1 , page_pos=0 , card_tag="Vehicle #1" , nationality="Moldovia" , name="Big Tank" ) ,
            AslCard( page_id=1 , page_pos=1 , card_tag="Vehicle #2" , nationality="Moldovia" , name="Little Tank" ) ,
        ] )

    def test_3card_file( self ) :
        # try parsing a file with 3 cards
        self._test_pdf_parser( "3-cards.pdf" , [
            AslCard( page_id=1 , page_pos=0 , card_tag="Vehicle #1" , nationality="Moldovia" , name="Big Tank" ) ,
            AslCard( page_id=1 , page_pos=1 , card_tag="Vehicle #2" , nationality="Moldovia" , name="Little Tank" ) ,
            AslCard( page_id=2 , page_pos=0 , card_tag="Ordnance #1" , nationality="Moldovia" , name="Big Gun" ) ,
        ] )

    def test_bad_spacing( self ) :
        # try parsing cards with bad spacing
        self._test_pdf_parser( "bad-spacing.pdf" , [
            AslCard( page_id=1 , page_pos=0 , card_tag="Vehicle #1" , nationality="" , name="" ) ,
            AslCard( page_id=1 , page_pos=1 , card_tag="Vehicle #2" , nationality="Moldovia" , name="" ) ,
        ] )

# ---------------------------------------------------------------------

if __name__ == "__main__" :
    unittest.main()
