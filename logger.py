#!/usr/bin/env python
# 
import sys
import argparse
import re
import string
import doctest
from filewrapper import FileWrapper

def main(args):
    """ 
        """
    url = 'http://web.mta.info/status/serviceStatus.txt'
    fh = FileWrapper('mta.xml')
    fh.open()
    fh.write(fh.request(url))
    fh.close()
  

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
