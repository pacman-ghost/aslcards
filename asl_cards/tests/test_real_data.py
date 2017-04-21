#!/usr/bin/env python3

import sys
import os
import unittest

base_dir = os.path.split( __file__ )[ 0 ]
sys.path.append( os.path.join( base_dir , ".." ) )
from parse import PdfParser , AslCard

# ---------------------------------------------------------------------

class TestRealData( unittest.TestCase ) :
    """Run tests using the real "ASL Cards" PDF files."""

    def _test_pdf_parser( self , fname , expected_cards ) :
        # parse the specified PDF
        fname2 = os.path.join( base_dir , os.path.join("real-data",fname) )
        if not os.path.isfile( fname2 ) :
            raise RuntimeError( "Missing data file: {}".format( fname2 ) )
        pdf_parser = PdfParser(
            #progress = lambda _,msg: print( msg , file=sys.stderr )
        )
        cards = pdf_parser.parse_file( fname2 )
        # check the results
        if len(cards) != len(expected_cards) :
            raise RuntimeError( "{}: got {} cards, expected {}.".format( fname , len(cards) , len(expected_cards) ) )
        for i in range(0,len(cards)) :
            if cards[i] != expected_cards[i] :
                raise RuntimeError( "{}: Card mismatch ({}): got {}, expected {}.".format( fname , i , cards[i] , expected_cards[i] ) )

    def test_japanese_vehicles( self ) :
        self._test_pdf_parser( "JapaneseVehiclesFeb15.pdf" , [
            AslCard(page_id=1, page_pos=0, tag="Vehicle #1", nationality="Japanese", name="Type 92A") ,
            AslCard(page_id=1, page_pos=1, tag="Vehicle #1", nationality="Japanese", name="Type 92B") ,
            AslCard(page_id=2, page_pos=0, tag="Vehicle #2", nationality="Japanese", name="Type 94") ,
            AslCard(page_id=2, page_pos=1, tag="Vehicle #3", nationality="Japanese", name="Type 95 SO4KI") ,
            AslCard(page_id=3, page_pos=0, tag="Vehicle #4", nationality="Japanese", name="Type 97A TE6KE") ,
            AslCard(page_id=3, page_pos=1, tag="Vehicle #4", nationality="Japanese", name="Type 97B TE6KE") ,
            AslCard(page_id=4, page_pos=0, tag="Vehicle #5", nationality="Japanese", name="Type 95 HA6GO") ,
            AslCard(page_id=4, page_pos=1, tag="Vehicle #6", nationality="Japanese", name="Type 2 KA6MI") ,
            AslCard(page_id=5, page_pos=0, tag="Vehicle #6", nationality="Japanese", name="Type 2 KA:MI w/o") ,
            AslCard(page_id=5, page_pos=1, tag="Vehicle #7", nationality="Japanese", name="Type 89A CHI:RO") ,
            AslCard(page_id=6, page_pos=0, tag="Vehicle #7", nationality="Japanese", name="Type 89B CHI7RO") ,
            AslCard(page_id=6, page_pos=1, tag="Vehicle #8", nationality="Japanese", name="Type 97A CHI7HA") ,
            AslCard(page_id=7, page_pos=0, tag="Vehicle #8", nationality="Japanese", name="Type 97B CHI6HA") ,
            AslCard(page_id=7, page_pos=1, tag="Vehicle #9", nationality="Japanese", name="Type 1 CHI6HE") ,
            AslCard(page_id=8, page_pos=0, tag="Vehicle #10", nationality="Japanese", name="Type 91") ,
            AslCard(page_id=8, page_pos=1, tag="Vehicle #11", nationality="Japanese", name="Type 92") ,
            AslCard(page_id=9, page_pos=0, tag="Vehicle #12", nationality="Japanese", name="Type 1 HO?NI I") ,
            AslCard(page_id=9, page_pos=1, tag="Vehicle #13", nationality="Japanese", name="Type 4 HO?RO") ,
            AslCard(page_id=10, page_pos=0, tag="Vehicle #14", nationality="Japanese", name="Type 1 HO?KI") ,
            AslCard(page_id=10, page_pos=1, tag="Vehicle #15", nationality="Japanese", name="Type 98 SHI?KE") ,
            AslCard(page_id=11, page_pos=0, tag="Vehicle #16", nationality="Japanese", name="Type 92 IBKE") ,
            AslCard(page_id=11, page_pos=1, tag="Vehicle #17", nationality="Japanese", name="Type 95") ,
            AslCard(page_id=12, page_pos=0, tag="Vehicle #18", nationality="Japanese", name="Type 94 Truck") ,
            AslCard(page_id=12, page_pos=1, tag="Vehicle #18", nationality="Japanese", name="Type 97 Truck") ,
        ] )

    def test_chinese_ordnance( self ) :
        self._test_pdf_parser( "ChineseOrdnanceMidApril15.pdf" , [
            AslCard(page_id=1, page_pos=0, tag="Ordnance3#31", nationality="Chinese", name="Type3273GL") ,
            AslCard(page_id=1, page_pos=1, tag="Ordnance3#32", nationality="Chinese", name="Mortaio3da3453 i") ,
            AslCard(page_id=2, page_pos=0, tag="Ordnance0#02", nationality="Chinese", name="5cm0leGrW0360 g") ,
            AslCard(page_id=2, page_pos=1, tag="Ordnance0#02", nationality="Chinese", name="50mm0RM0obr 380 r") ,
            AslCard(page_id=3, page_pos=0, tag="Ordnance1#12", nationality="Chinese", name="Type1891HGL1 j") ,
            AslCard(page_id=3, page_pos=1, tag="Ordnance1#13", nationality="Chinese", name="M2160mm1 a") ,
            AslCard(page_id=4, page_pos=0, tag="Ordnance3#34", nationality="Chinese", name="Stokes33>in3 b") ,
            AslCard(page_id=4, page_pos=1, tag="Ordnance3#34", nationality="Chinese", name="8cm3GrW3343 g") ,
            AslCard(page_id=5, page_pos=0, tag="Ordnance2#24", nationality="Chinese", name="82mm2BM2o 2372 r") ,
            AslCard(page_id=5, page_pos=1, tag="Ordnance2#25", nationality="Chinese", name="M1281mm2 a") ,
            AslCard(page_id=6, page_pos=0, tag="Ordnance5#55", nationality="Chinese", name="M254 2?in5 a") ,
            AslCard(page_id=6, page_pos=1, tag="Ordnance5#56", nationality="Chinese", name="3 7cm5PaK535/365 g") ,
            AslCard(page_id=7, page_pos=0, tag="Ordnance2#26", nationality="Chinese", name="M3A1237mm2 a") ,
            AslCard(page_id=7, page_pos=1, tag="Ordnance2#27", nationality="Chinese", name="37mm2PP2o 215R2 r") ,
            AslCard(page_id=8, page_pos=0, tag="Ordnance2#27", nationality="Chinese", name="Cann 2da270/152 i") ,
            AslCard(page_id=8, page_pos=1, tag="Ordnance2#28", nationality="Chinese", name="7 5cm2Krupp2 g") ,
            AslCard(page_id=9, page_pos=0, tag="Ordnance1#18", nationality="Chinese", name="Obice1da175/131 i") ,
            AslCard(page_id=9, page_pos=1, tag="Ordnance1#19", nationality="Chinese", name="7 5cm1leIG1181 g") ,
            AslCard(page_id=10, page_pos=0, tag="Ordnance2#29", nationality="Chinese", name="76 2mm2PP2o 2272 r") ,
            AslCard(page_id=10, page_pos=1, tag="Ordnance2#210", nationality="Chinese", name="M1A1275mm2 a") ,
            AslCard(page_id=11, page_pos=0, tag="Ordnance #11", nationality="Chinese", name="7 7cm FK 16  g") ,
            AslCard(page_id=11, page_pos=1, tag="Ordnance #11", nationality="Chinese", name="76 2mm o 02/30  r") ,
            AslCard(page_id=12, page_pos=0, tag="Ordnance4#411", nationality="Chinese", name="OQF418pdr4 b") ,
            AslCard(page_id=12, page_pos=1, tag="Ordnance4#412", nationality="Chinese", name="10 5cm4leFH4164 g") ,
            AslCard(page_id=13, page_pos=0, tag="Ordnance1#112", nationality="Chinese", name="Cann 1da1105/281 i") ,
            AslCard(page_id=13, page_pos=1, tag="Ordnance1#112", nationality="Chinese", name="M2A11105mm1 a") ,
            AslCard(page_id=14, page_pos=0, tag="Ordnance1#113", nationality="Chinese", name="122mm1o 10/301 r") ,
            AslCard(page_id=14, page_pos=1, tag="Ordnance1#113", nationality="Chinese", name="122mm1G1o 1381 r") ,
            AslCard(page_id=15, page_pos=0, tag="Ordnance4#414", nationality="Chinese", name="Obice4da4149/134 i") ,
            AslCard(page_id=15, page_pos=1, tag="Ordnance4#415", nationality="Chinese", name="Oerlikon4FF4 g") ,
            AslCard(page_id=16, page_pos=0, tag="Ordnance #15", nationality="Chinese", name="Oerlikon FF  LF") ,
            AslCard(page_id=16, page_pos=1, tag="Ordnance #15", nationality="Chinese", name="Cann Amitr  20/65  i") ,
            AslCard(page_id=17, page_pos=0, tag="Ordnance #15", nationality="Chinese", name="Cann 5mitr  20/65  LF") ,
            AslCard(page_id=17, page_pos=1, tag="Ordnance #15", nationality="Chinese", name="2cm FlaK 30  g") ,
            AslCard(page_id=18, page_pos=0, tag="Ordnance #15", nationality="Chinese", name="2cm FlaK 30  LF") ,
            AslCard(page_id=18, page_pos=1, tag="Ordnance #16", nationality="Chinese", name="3 7cm FlaK 36/37  g") ,
            AslCard(page_id=19, page_pos=0, tag="Ordnance #16", nationality="Chinese", name="Bofors 40mm L/60") ,
            AslCard(page_id=19, page_pos=1, tag="Ordnance #16", nationality="Chinese", name="Bofors 40mm L/60  LF") ,
            AslCard(page_id=20, page_pos=0, tag="Ordnance #17", nationality="Chinese", name="Bofors 76mm M29") ,
            AslCard(page_id=20, page_pos=1, tag="Ordnance #17", nationality="Chinese", name="Bofors 76mm M29  LF") ,
            AslCard(page_id=21, page_pos=0, tag="Ordnance #17", nationality="Chinese", name="8 8cm FlaK 18  g") ,
            AslCard(page_id=21, page_pos=1, tag="Ordnance #17", nationality="Chinese", name="8 8cm FlaK 18  LF") ,
        ] )

# ---------------------------------------------------------------------

if __name__ == "__main__" :
    unittest.main()
