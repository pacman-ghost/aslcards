""" Manage information about each nationality.
"""

import sys
import os
import json

_nat_info = None
_base_dir = None

# ---------------------------------------------------------------------

def _make_key( nat ) :
    """Get the JSON key for a nationality.

    We require the JSON keys to be lower-case, with no spaces (not strictly necessary, but not a bad idea :-/).
    """
    return nat.lower().replace( " " , "-" ) if nat else None

def display_name_from_key( key ) :
    """Get the nationality display string from a JSON key."""
    return key.replace( "-" , " " ).capitalize()

# ---------------------------------------------------------------------

def load( base_dir ) :
    """Load the nationality information."""
    global _base_dir , _nat_info
    _base_dir = os.path.abspath( base_dir )
    fname = os.path.join( base_dir , "natinfo.json" )
    if os.path.isfile( fname ) :
        with open( fname , "r" ) as fp :
            _nat_info = json.load( fp )
    else :
        _nat_info = {}

def dump() :
    """Dump the nationality information."""
    for nat in sorted(_nat_info.keys()) :
        print( "{}:".format( nat ) )
        print( "- flag = {}".format( get_flag(nat) ) )
        print( "- accel = {}".format( get_accel_for_nat(nat) ) )

def get_flag( nat ) :
    """Locate the flag image file for a nationality.

    These are set in the JSON data file at $/{nat}/flag. If there is no entry, the default is $/flags/${nat}.png
    """
    key = _make_key( nat )
    try :
        fname = _nat_info[ key ][ "flag" ]
    except ( KeyError , TypeError ) :
        fname = "{}.png".format( key )
    fname = os.path.join( _base_dir , os.path.join("flags", fname) )
    return fname if os.path.isfile(fname) else None

def get_nats_for_accel( ch ) :
    """Get the nationalities for an accelerator key."""
    if ch is None : return None
    ch = ch.strip().lower()
    if not ch : return None
    return [ nat for nat,vals in _nat_info.items() if vals.get("accelerator","").lower() == ch ]

def get_accel_for_nat( nat ) :
    """Get the accelerator key for a nationality."""
    key = _make_key( nat )
    try :
        return _nat_info[ key ][ "accelerator" ].lower()
    except ( KeyError , TypeError ) :
        return None
