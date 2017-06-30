#!/usr/bin/env python
# Turn the MTA's XML feed items into something manageable
import sys
import argparse
import re
import string
import doctest
from bs4 import BeautifulSoup


class ParseMTA(object):

    def __init__(self):
        """
            >>>
            """
        lines = []
        subway_re = \[[0-9A-Z]+\]

    def make_datetime(self, value):
        """ Turn a string such as '05/23/2017 12:08AM' into a datetime object.
            """
        pass

    def extract(self, value):
        """ Given a line object, return the relevant parts.
            """
        lines = self.extract_lines(value)
        has_delays = 0
        has_planned_work = 0
        return lines
        
    def extract_lines(self, value):
        """ Given a line's status, parse the MTA lines mentioned in it.
            Returns a list.
            """
        if value['text']:
            self.soup = BeautifulSoup(value['text'], 'html.parser')
        else:
            return None
        #return 
        print
        print
        #print value['text']
        #print soup.get_text()
        #print dir(soup)
        #print soup.prettify()
        spans = self.soup.find_all('span')
        delays = ['TitlePlannedWork', 'TitleDelay']
        for item in spans:
            d = {}
            #print value['text']
            for delay in delays:
                if delay in unicode(item):
                    d = self.extract_line_delay(delay, item)
            print d
            #print item

    def extract_line_delay(self, delay, span):
        """ Given a type of delay, extract the data from the markup that usually
            runs with that delay. Returns a dict.
            """
        if delay == 'TitlePlannedWork':
            return self._extract_planned_work(span)
        elif delay == 'TitleDelay':
            return self._extract_delay(span)

    def _extract_planned_work(self, span):
        """ Parse a planned work markup. Return a dict.
            """
        return None

    def _extract_delay(self, span):
        """ Parse delay markup. Return a dict.
            """
        print 'asdfasdf'
        print dir(span)
        for item in span.next_siblings:
            # The subway lines, if they're in this, will be
            # enclosed in brackets, ala [M] and [F]
            print dir(item)
            print '8888888888'
        try:
            print ''.join(span.findNextSiblings())
        except:
            print span

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
