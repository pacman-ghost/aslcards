#!/usr/bin/env python3
""" CLI for the asl_cards module. """

import sys
import os
import getopt

from parse import PdfParser
import db

# ---------------------------------------------------------------------

def main( args ) :

    # parse the arguments
    db_fname = None
    parse_targets = []
    max_pages = -1
    extract_images = True
    log_progress = False
    dump = False
    try :
        opts , args = getopt.getopt( args , "f:d:ph?" , ["db=","file=","dir=","maxpages=","noimages","progress","dump","help"] )
    except getopt.GetoptError as err :
        raise RuntimeError( "Can't parse arguments: {}".format( err ) )
    for opt,val in opts :
        if opt in ["--db"] :
            db_fname = val
        elif opt in ["-f","--file"] :
            parse_targets.append( val )
        elif opt in ["-d","--dir"] :
            parse_targets.append( val )
        elif opt in ["--maxpages"] :
            max_pages = int( val )
        elif opt in ["--noimages"] :
            extract_images = False
        elif opt in ["-d","--dump"] :
            dump = True
        elif opt in ["-p","--progress"] :
            log_progress = True
        elif opt in ["-h","--help","-?"] :
            print_help()
        else :
            raise RuntimeError( "Unknown argument: {}".format( opt ) )
    if not db_fname : raise RuntimeError( "No database was specified." )

    # initialize
    db.open_database( db_fname )

    # do the requested processing
    pdf_parser = PdfParser( progress_callback if log_progress else None )
    if parse_targets :
        cards = []
        for pt in parse_targets :
            cards.extend (
                pdf_parser.parse( pt , max_pages=max_pages , images=extract_images )
            )
        db.add_cards( cards )
    elif dump :
        db.dump_database()
    else :
        raise RuntimeError( "No action." )

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def progress_callback( progress , msg ) :
    if progress is not None :
        print( "{:3}% | {}".format(int(100*progress),msg) , file=sys.stderr , flush=True )
    else :
        print( "     | {}".format(msg) , file=sys.stderr , flush=True )

# ---------------------------------------------------------------------

def print_help() :
    print( "{} {{options}}".format( os.path.split(sys.argv[0])[1] ) )
    print()
    print( "      --db         Database file." )
    print( "  -f  --file       PDF file to parse." )
    print( "  -d  --dir        Directory with PDF's to parse." )
    print( "      --maxpages   Maximum number of pages to pages." )
    print( "      --noimages   Don't extract card images." )
    print( "      --dump       Dump the database." )
    print( "      --progress   Log progress during lengthy operations." )
    print()

# ---------------------------------------------------------------------

if __name__ == "__main__" :
    main( sys.argv[1:] )
