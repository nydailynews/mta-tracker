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
        self.lines = []
        self.subway_re = '\[[0-9A-Z]+\]'

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
        #print value['text']
        #print soup.get_text()
        #print dir(soup)
        #print soup.prettify()
        spans = self.soup.find_all('span')
        delays = ['TitlePlannedWork', 'TitleDelay']
        d = {'TitlePlannedWork': [], 'TitleDelay': []}
        for item in spans:
            for delay in delays:
                if delay in unicode(item):
                    d[delay].extend(self.extract_subway_delay(delay, item))
        return d

    def extract_subway_delay(self, delay, span):
        """ Given a type of delay, extract the data from the markup that usually
            runs with that delay. Returns a list.
            """
        if delay == 'TitlePlannedWork':
            return self._extract_planned_work(span)
        elif delay == 'TitleDelay':
            return self._extract_delay(span)

    def _extract_planned_work(self, span):
        """ Parse a planned work markup. Return a dict.
            """
        return []

    def _extract_delay(self, span):
        """ Parse delay markup. Return a list of affected lines.
            """
        lines_affected = []
        for item in span.findAllNext():
            # The subway lines, if they're in this, will be
            # enclosed in brackets, ala [M] and [F]
            #print item.text
            r = re.findall(self.subway_re, item.text)

            if len(r) > 0:
                for item in r:
                    lines_affected.append(item.lstrip('[').rstrip(']'))

        return list(set(lines_affected))

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
