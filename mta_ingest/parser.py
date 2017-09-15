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
import xml.etree.ElementTree as ET


class ParseMTA(object):
    def __init__(self, *args):
        """
            >>> args = build_parser(['test.xml'])
            >>> p = ParseMTA(args)
            """
        self.args = args[0]
        self.lines = []
        self.subway_re = '\[[0-9A-Z]+\]'

    def make_datetime(self, value):
        """ Turn a string such as '05/23/2017 12:08AM' into a datetime object.
            """
        pass

    def parse_file(self, fn, transit_type):
        """ Given a filename, turn an xml file into an object and return entries
            for the specified transit_type.
            >>> args = build_parser(['test.xml'])
            >>> p = ParseMTA(args)
            >>> entries = p.parse_file('test.xml', 'subway')
            >>> print(entries[0].find('name').text)
            123
            """
        e = ET.parse('_input/%s' % fn)
        r = e.getroot()
        # Options for transit_type: subway, bus, BT, LIRR, MetroNorth
        return r.find(transit_type)

    def extract(self, value):
        """ Given an entry derived loosely from the MTA's XML, return the relevant parts.
            An item, defined in logger.py, looks something like:
            item = {
                'status': l.find('status').text,
                'status_detail': {},
                'lines': l.find('name').text,  # This is generic, the actual lines affected may be some of these, or others.
                'datetime': '%s %s' % (l.find('Date').text, l.find('Time').text),
                'text': l.find('text').text
            }
            >>> args = build_parser(['test.xml'])
            >>> p = ParseMTA(args)
            >>> entries = p.parse_file('test.xml', 'subway')
            >>> item = { 'text': entries[0].find('text').text }
            >>> lines = p.extract(item)
            >>> print(lines.keys())
            ['TitleDelay', 'TitlePlannedWork', 'TitleServiceChange']
            """
        if value['text']:
            self.soup = BeautifulSoup(value['text'], 'html.parser')
        else:
            return None
        # print(soup.get_text())
        # print(dir(soup))
        # print(soup.prettify())
        spans = self.soup.find_all('span')
        types = ['TitlePlannedWork', 'TitleDelay', 'TitleServiceChange']

        d = {'TitlePlannedWork': {}, 'TitleDelay': {}, 'TitleServiceChange': {}}
        for item in spans:
            for type_ in types:
                if type_ in unicode(item):
                    d[type_].update(self.extract_status(type_, item))
        if self.args.verbose:
            print("The results of ParseMTA().extract():", d)
        return d

    def extract_status(self, status, span):
        """ Given a type of delay, extract the data from the markup that usually
            runs with that delay. Returns a dict.
            >>> args = build_parser(['test.xml'])
            >>> p = ParseMTA(args)
            >>> entries = p.parse_file('test.xml', 'subway')
            >>> item = { 'text': entries[0].find('text').text }
            >>> lines = p.extract(item)
            >>> print(lines['TitleDelay']['5'])
            [u'Following earlier NYPD activity at Wall St , [4] and [5] train service has resumed.']
            """
        if status == 'TitleDelay':
            return self._extract_delay(span)
        #elif status == 'TitlePlannedWork':
        #    return self._extract_planned_work(span)
        return {}

    def _extract_planned_work(self, span):
        """ Parse a planned work markup. Return a dict.
            """
        return {}

    def _extract_delay(self, span):
        """ Parse delay markup. Delays are sometimes embedded in <p> elements.
            Return a dict of affected lines / list of delay causes.
            Ex: {u'3': [u'Following an earlier incident involving track repairs...
            """
        lines_affected = {}
        # We can't trust that the delay is always in a p element (blergh):
        """<span class="TitleDelay">Delays</span>
<span class="DateStyle">
                 Posted: 07/09/2017 10:26PM
                </span><br/><br/>
              Following earlier track maintenance between <strong>Mets-Willets Point</strong> and <strong>33 St-Rawson St</strong>, [7] train service has resumed with delays.
            <br/><br/>"""
        items = span.find_parent().contents
        is_delay = False

        # In some situations we're looking through all the item's markup.
        # In those situations we need to make sure we're looking at Delays
        # and not at planned work.

        # ** WE COULD:
        # Loop through every item, and each time there's more than one consecutive blank line, axe those.
        # Take the remaining pieces and put them in another list, then loop through that.
        # That should give us whole-delay entries, alongside the titles, and the 
        # So, we've got this situation with the subway.
        # In some situations we get the delays split up into three strings like this:
        cleaned = []
        blank_count = 0
        current_string = ''
        for i, item in enumerate(items):
            if isinstance(item, NavigableString) or isinstance(item, unicode) or isinstance(item, str):
                # Triggered when the text is not directly in a <p> / <strong> / <span> element.
                #if is_delay and self.args.verbose:
                #    print("%d*" % i, item.strip())
                text = item.strip()
            else:
                #if is_delay and self.args.verbose:
                #    print(i, item.text.strip())
                text = item.text.strip()

            has_keyphrase = False
            for keyphrase in ['Planned Work', 'Service Change', 'Planned Detour', 'Service Change']:
                if keyphrase in text:
                    has_keyphrase = True

            if text == 'Delays':
                is_delay = True
            elif has_keyphrase:
                if self.args.verbose:
                    print(text)
                    print('%%%%%%%%')
                is_delay = False
            #else:
            #    print('********')
            #    print(text)
            #    print('********')
            if not is_delay:
                continue

            # This code splices the strings together that have been separated,
            # and separates the separate sentences.
            # This gives us a list such as
            # [u'Delays Posted:\xa008/02/2017\xa0 8:39PM', u'Following earlier signal problems at 8 Av...
            # which is easier for us to parse than the list we had before.
            if text == '':
                blank_count += 1
            elif text not in ['Know Before You Go.Sign up for My MTA Alerts at http://www.mymtaalerts.com', 'Allow additional travel time.We apologize for the inconvenience']:
                blank_count = 0
                if current_string != '':
                    current_string += ' '
                current_string += text

            if blank_count > 1 and current_string != '':
                blank_count = 0
                cleaned.append(current_string)
                current_string = ''

        if self.args.verbose:
            print("NOTICE: Cleaned text:", cleaned)
        """
6* Following an earlier signal problems at
7 Van Cortlandt Park-242 St
8* , [1] train service has resumed with delays.

or this:
6* Due to an earlier incident involving a train with mechanical problems at
7 Rockaway Blvd
8* , [A] train service has resumed with delays.

or this:
3 Posted: 07/25/2017 12:13PM
4
5
6* Following an earlier incident at
7 Canal St
8* , [A], [C] and [F] train service has resumed with delays.

or this:
4
5
6* Following an earlier incident involving a train with mechanical problems at
7 Canal St
8* , [4], [5] and [6] train service has resumed with delays.

or this:
6*
7 Due to signal problems at 52 St, 34 St-bound [7] trains are running with delays.
8*
9 Allow additional travel time.

or this:
32* Following earlier signal problems at
33 96 St
34* , [2] and [3] train service has resumed with delays.

and this:
19*
20 Due to signal problems at 125 St, northbound [1] trains are running with delays.
21*
        """

        for i, item in enumerate(cleaned):
            # TODO: Sus out when an element has a class with Title in the class name and turn on / off the is_delay flag then
            # TODO: Reduce the jank.

            # The subway lines, if they're in this, will be
            # enclosed in brackets, ala [M] and [F]
            r = re.findall(self.subway_re, item)

            if len(r) > 0:
                for i in r:
                    line = i.lstrip('[').rstrip(']')
                    if self.args.verbose:
                        print(line,)
                    # Compare the line and its delay cause to make sure
                    # it's not already accounted for.
                    if line not in lines_affected:
                        lines_affected[line] = [item]
                    elif line in lines_affected and item not in lines_affected[line]:
                        lines_affected[line].append(item)

        if self.args.verbose:
            print("RETURNING THESE AFFECTED LINES from _extract_delay()\n", lines_affected)
        return lines_affected

def build_parser(args):
    """ This method allows us to test the args.
        >>> args = build_parser(['--verbose'])
        >>> print(args.verbose)
        True
        """
    parser = argparse.ArgumentParser(usage='$ python parser.py',
                                     description='Parse the MTA alert feed, return a dict.',
                                     epilog='Example use: python parser.py')
    parser.add_argument("-v", "--verbose", dest="verbose", default=False, action="store_true")
    parser.add_argument("--test", dest="test", default=False, action="store_true")
    parser.add_argument("files", nargs="*", help="Path to files to ingest manually")
    args = parser.parse_args(args)
    return args


if __name__ == '__main__':
    args = build_parser(sys.argv[1:])

    if args.test:
        doctest.testmod(verbose=args.verbose)
