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
        self.assertIsNone( natinfo.get_flag( "german" ) )
        self.assertTrue( natinfo.get_flag("american").endswith( "/flags/american.png" ) )
        self.assertTrue( natinfo.get_flag("japanese").endswith( "/flags/japanese-flag.gif" ) )
        self.assertIsNone( natinfo.get_flag( "_unknown_" ) )
        self.assertIsNone( natinfo.get_flag( "" ) )
        self.assertIsNone( natinfo.get_flag( None ) )

    def test_accelerators( self ) :
        """Test nationality accelerators."""
        # test getting the nationalities that use a given accelerator key
        self.assertEqual( natinfo.get_nats_for_accel("G") , ["german"] )
        self.assertEqual( natinfo.get_nats_for_accel("g") , ["german"] )
        self.assertEqual( natinfo.get_nats_for_accel("a") , ["american","australian"] )
        self.assertEqual( natinfo.get_nats_for_accel("russian") , [] )
        self.assertEqual( natinfo.get_nats_for_accel("_") , [] )
        self.assertIsNone( natinfo.get_nats_for_accel( "" ) )
        self.assertIsNone( natinfo.get_nats_for_accel( None ) )
        # test getting the accelerator key for a given nationality
        self.assertEqual( natinfo.get_accel_for_nat("german") , "g" )
        self.assertEqual( natinfo.get_accel_for_nat("american") , "a" )
        self.assertEqual( natinfo.get_accel_for_nat("australian") , "a" )
        self.assertIsNone( natinfo.get_accel_for_nat( "" ) )
        self.assertIsNone( natinfo.get_accel_for_nat( None ) )


# ---------------------------------------------------------------------

if __name__ == "__main__" :
    unittest.main()
