#!/usr/bin/env python
# Describe what this does in one line for people who might run head on this file.
import sys
import argparse
import re
import string
import doctest

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
    parser = argparse.ArgumentParser(usage='$ python logger.py',
                                     description='Get the latest MTA alerts and add any new ones.',
                                     epilog='Examply use: python logger.py')
    parser.add_argument("-v", "--verbose", dest="verbose", default=False, action="store_true")
    args = parser.parse_args(args)
    return args

if __name__ == '__main__':
    args = build_parser(sys.argv[1:])

    if args.verbose == True:
        doctest.testmod(verbose=args.verbose)
    main(args)
