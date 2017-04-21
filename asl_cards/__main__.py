#!/usr/bin/env python3
""" CLI for the asl_cards module. """

import sys
import os
import getopt

from parse import PdfParser

# ---------------------------------------------------------------------

def main( args ) :
    # parse the arguments
    try :
        opts , args = getopt.getopt( args , "f:d:h?" , ["file=","dir=","help"] )
    except getopt.GetoptError as err :
        raise RuntimeError( "Can't parse arguments: {}".format( err ) )
    for opt,val in opts :
        if opt in ("-f","--file") :
            pdf_parser = PdfParser( progress_callback )
            cards = pdf_parser.parse_file( val )
            for c in cards :
                print( c )
        elif opt in ("-d","--dir") :
            pdf_parser = PdfParser( progress_callback )
            fcards = pdf_parser.parse_dir( val )
            for fname,cards in fcards.items() :
                print( "{}:".format( fname ) )
                for c in cards :
                    print( "- {}".format( c ) )
        elif opt in ("-h","--help","-?") :
            print_help()
        else :
            raise RuntimeError( "Unknown argument: {}".format( opt ) )

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
    print( "  -f  --file   PDF file to parse." )
    print( "  -d  --dir    Directory with PDF's to parse." )
    print()

# ---------------------------------------------------------------------

if __name__ == "__main__" :
    main( sys.argv[1:] )
