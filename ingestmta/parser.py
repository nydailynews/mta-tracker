#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Turn the MTA's XML feed items into something manageable
from __future__ import print_function
import sys
import argparse
import re
import doctest
from bs4 import BeautifulSoup, NavigableString
from collections import defaultdict


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
            Returns a list of ____
            """
        if value['text']:
            self.soup = BeautifulSoup(value['text'], 'html.parser')
        else:
            return None
        # print (value['text'])
        # print (soup.get_text())
        # print (dir(soup))
        # print (soup.prettify())
        spans = self.soup.find_all('span')
        types = ['TitlePlannedWork', 'TitleDelay']
        d = {'TitlePlannedWork': {}, 'TitleDelay': {}}
        for item in spans:
            for type_ in types:
                if type_ in unicode(item):
                    d[type_].update(self.extract_subway_delay(type_, item))
        return d

    def extract_subway_delay(self, delay, span):
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
        return {}

    def _extract_delay(self, span):
        """ Parse delay markup. Delays are embedded in <p> elements.
            Return a dict of affected lines / reasons for the delay
            """
        lines_affected = {}
        p = span.find_all_next('p')
        if len(p) > 0:
            items = p
            check = False
        else:
            # Sometimes the delay isn't in a p element (blergh):
            """<span class="TitleDelay">Delays</span>
<span class="DateStyle">
                     Posted: 07/09/2017 10:26PM
                    </span><br/><br/>
                  Following earlier track maintenance between <strong>Mets-Willets Point</strong> and <strong>33 St-Rawson St</strong>, [7] train service has resumed with delays.
                <br/><br/>"""
            # print (dir(span))
            # print (span.find_parent().contents)
            items = span.find_parent().contents
            check = True
            is_delay = False
            # print (span.find_all_next())
            # print (span.find_all_previous())
        for i, item in enumerate(items):
            # In some situations we're looking through all the item's markup.
            # In those situations we need to make sure we're looking at Delays
            # and not at planned work.
            # TODO: Sus out when an element has a class with Title in the class name and turn on / off the is_delay flag then
            # TODO: Reduce the jank.
            if check:
                if isinstance(item, NavigableString):
                    text = item
                else:
                    text = item.text

                if text == 'Delays':
                    is_delay = True
                elif text in ['Planned Work', 'Service Change', 'Planned Detour']:
                    is_delay = False

                if not is_delay:
                    continue
            else:
                text = item.text

            # The subway lines, if they're in this, will be
            # enclosed in brackets, ala [M] and [F]
            r = re.findall(self.subway_re, text)

            if len(r) > 0:
                for item in r:
                    line = item.lstrip('[').rstrip(']')
                    cause = text.strip()
                    if line not in lines_affected:
                        lines_affected[line] = cause

        return lines_affected

def build_parser(args):
    """ This method allows us to test the args.
        >>> args = build_parser(['--verbose'])
        >>> print (args.verbose)
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

    if args.verbose:
        doctest.testmod(verbose=args.verbose)
