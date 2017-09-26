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
        if self.args.verbose:
            print("""\n\nWELCOME TO THE MTA PARSER.
You're here because you're curious.

We're taking the MTA's XML and making it even more machine-readable. To do this we have to concatenate strings.
To increase the visibility of how these strings are assembled, we assign a symbol to each string operation.

Here's the legend for those symbols:
    +++ means "This string was added to the current string"
    >>> means "This is the current string"
    ***  means "This current string is finished, this is what it is, and we're moving on to the next."
    XXX means "This string has been skipped and will not be added to the current string."
""")

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
            print("NOTICE: The results of ParseMTA().extract():", d)
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

        # WHAT WE'RE DOING:
        # Loop through every item, and each time there's more than one consecutive blank line, axe those.
        # Take the remaining pieces and put them in another list, then loop through that.
        # That should give us whole-delay entries, alongside the titles
        cleaned = []
        blank_count = 0
        current_string = ''
        for i, item in enumerate(items):
            if isinstance(item, NavigableString) or isinstance(item, unicode) or isinstance(item, str):
                # Triggered when the text is not directly in a <p> / <strong> / <span> element.
                text = item.strip()
            else:
                text = item.text.strip()

            has_keyphrase = False
            for keyphrase in ['Planned Work', 'Service Change', 'Planned Detour', 'Service Change']:
                if keyphrase in text:
                    has_keyphrase = True

            if text == 'Delays':
                is_delay = True
            elif has_keyphrase:
                #if self.args.verbose:
                #    print('%%%%%%%%')
                #    print(text)
                #    print('%%%%%%%%')
                is_delay = False
            #else:
            #    print('********')
            #    print(text)
            #    print('********')
            if not is_delay:
                continue

            # Clean up some of the boilerplate the MTA sticks in there
            if 'Allow additional travel time.' in text or 'www.mymtaalerts.com' in text:
                pass

            # This code splices the strings together that have been separated,
            # and separates the separate sentences.
            # This gives us a list such as
            # [u'Delays Posted:\xa008/02/2017\xa0 8:39PM', u'Following earlier signal problems at 8 Av...
            # which is easier for us to parse than the list we had before.
            if text == '':
                blank_count += 1
            elif text not in ['Allow additional travel time', 'We Apologize for the inconvenience.', 'Know Before You Go!!', 'Sign up for MY MTA Alerts at www.mymtaalerts.com', 'Know Before You Go!Sign up at MY MTA Alerts www.mymtaalerts.com', 'Know Before You Go.Sign up for My MTA Alerts at http://www.mymtaalerts.com', 'Allow additional travel time.We apologize for the inconvenience','Allow additional travel time.We apologize for any inconvenience.','Allow additional travel time.','Allow additional travel time. Know Before You Go!','Sign Up for My MTA Alerts at www.mymtaalerts.com', 'Allow additional travel time.We apologize for any inconvenience', 'Know Before You Go!Sign up for MY MTA Alerts at mymtaalerts.com', 'Allow additional travel time.Know Before You Go!', 'Sign up for My MTA Alerts at www.mymtaalerts.com']:
                blank_count = 0
                if current_string != '':
                    current_string += ' '
                current_string += text
                if self.args.verbose:
                    print('    +++', text)
            else:
                blank_count += 1
                if self.args.verbose:
                    print('    XXX', text)

            # We only count an entry as finished when there's at least one blank line between items
            if blank_count > 1 and current_string != '':
                blank_count = 0
                if self.args.verbose:
                    print('    ***', current_string)
                cleaned.append(current_string)
                current_string = ''
            else:
                if self.args.verbose:
                    if text != '':
                        print('    >>>',current_string)

        if self.args.verbose:
            print("\n\nNOTICE: Cleaned text:", cleaned)

        for i, item in enumerate(cleaned):
            # The subway lines, if they're in this, will be
            # enclosed in brackets, ala [M] and [F]
            r = re.findall(self.subway_re, item)

            if len(r) > 0:
                for i in r:
                    line = i.lstrip('[').rstrip(']')
                    # Compare the line and its delay cause to make sure
                    # it's not already accounted for.
                    if line not in lines_affected:
                        lines_affected[line] = [item]
                    elif line in lines_affected and item not in lines_affected[line]:
                        lines_affected[line].append(item)

        if self.args.verbose:
            print("NOTICE: Affected lines from _extract_delay()", lines_affected.keys())
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
