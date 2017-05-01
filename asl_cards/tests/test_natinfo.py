#!/usr/bin/env python3

import sys
import os
import unittest

from _test_case_base import TestCaseBase
from asl_cards import natinfo

# ---------------------------------------------------------------------

class TestNatInfo( TestCaseBase ) :
    """Test nationality info."""

    @classmethod
    def setUpClass( cls ) :
        # load the nationality info
        base_dir = os.path.split( __file__ )[ 0 ]
        fname = os.path.join( base_dir , "natinfo-data" )
        natinfo.load( fname )

    def test_flags( self ) :
        """Test locating the flag image files for each nationality."""
        self.assertIsNone( natinfo.get_flag( "xxx" ) )
        self.assertIsNone( natinfo.get_flag( "german" ) )
        self.assertTrue( natinfo.get_flag("american").endswith( "/flags/american.png" ) )
        self.assertTrue( natinfo.get_flag("japanese").endswith( "/flags/japanese-flag.gif" ) )

# ---------------------------------------------------------------------

if __name__ == "__main__" :
    unittest.main()
