#!/usr/bin/env python
# Turn the MTA's XML feed items into something manageable
import sys
import argparse
import re
import string
import doctest


class ParseMTA:

    def __init__(self):
        """
            >>>
            """
        lines = []

    def make_datetime(self, value):
        """ Turn a string such as '05/23/2017 12:08AM' into a datetime object.
            """
        pass

    def extract_lines(self, value):
        """ Given a line's status, parse the MTA lines mentioned in it.
            Returns a list.
            """
        pass

def main(args):
    """ 
        """
    pass
  

def build_parser(args):
    """ This method allows us to test the args.
        >>> args = build_parser(['--verbose'])
        >>> print args.verbose
        True
        """
    parser = argparse.ArgumentParser(usage='$ python parser.py',
                                     description='Parse the MTA alert feed, return a dict.',
                                     epilog='Examply use: python parser.py')
    parser.add_argument("-v", "--verbose", dest="verbose", default=False, action="store_true")
    args = parser.parse_args(args)
    return args

if __name__ == '__main__':
    args = build_parser(sys.argv[1:])

    if args.verbose == True:
        doctest.testmod(verbose=args.verbose)
    main(args)
