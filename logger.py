#!/usr/bin/env python
# Download and log the MTA's status updates. We only log changes.
import sys
import argparse
import re
import string
import doctest
from filewrapper import FileWrapper
import random
import xml.etree.ElementTree as ET
from parser import ParseMTA

def main(args):
    """ 
        """
    rando = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    url = 'http://web.mta.info/status/serviceStatus.txt?%s' % rando
    fh = FileWrapper('mta.xml')
    fh.open()
    fh.write(fh.request(url))
    fh.close()
    e = ET.parse('mta.xml')
    r = e.getroot()
    # <Element 'subway' at 0x106c251d0>, <Element 'bus' at 0x106c321d0>, <Element 'BT' at 0x106c3e150>, <Element 'LIRR' at 0x106c3ef10>, <Element 'MetroNorth' at 0x106ca9050>
    return e, r
  

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
