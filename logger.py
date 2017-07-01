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
import json

class Logger:
    """ We're logging how long it has been since each line's previous
        service alert, and to do that we need to keep track of which lines
        have active service alerts and the timestamp on that alert.
        """

    def __init__(self):
        """
            >>>
            """
        fh = FileWrapper('previous.json')
        previous_alerts = json.load(fh.read())

    def compare(self):
        """ Compare the previous json of alerts with the current. Store the
            diffs in a new object.
            >>>
            """
        pass

class Line:
    """ A class for managing data specific to a particular line of transit service.
        We log delays and planned work per-line. This class helps with that.
        """

    def __init__(self):
        """
            >>>
            """
        pass

def main(args):
    """ 
        """
    mta = ParseMTA()
    if args.files == []:
        # If we didn't pass any arguments to logger, we download the current XML
        rando = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        url = 'http://web.mta.info/status/serviceStatus.txt?%s' % rando
        fh = FileWrapper('mta.xml')
        fh.open()
        fh.write(fh.request(url))
        fh.close()
        files = ['mta.xml']
    else:
        files = args.files
        if '*' in args.files[0]:
            # Wildcard matching on filenames so we can process entire directories
            pass

    items = {}
    for fn in files:
        e = ET.parse(fn)
        r = e.getroot()
        for l in r.find('subway'):
            item = {
                'status': l.find('status').text,
                'status_detail': {},
                'lines': l.find('name').text, # This is generic, the actual lines affected may be some of these, or others.
                'datetime': '%s %s' % (l.find('Date').text, l.find('Time').text),
                'text': l.find('text').text
            }
            if item['status']:
                # Add the entry to the items dict if it's not there.
                # Possible statuses: PLANNED WORK, DELAYS, GOOD SERVICE
                if not hasattr(items, item['status']):
                    items[item['status']] = []

                # Pull out the actual lines affected if we can
                item['status_detail'] = mta.extract(item)
                items[item['status']].append(item)
                #print '%(status)s: %(lines)s (%(datetime)s)' % item

    for item in items['DELAYS']:
        for line in item['status_detail']['TitleDelay']:
            print line, item['datetime']
  

def build_parser(args):
    """ This method allows us to test the args.
        >>> args = build_parser(['--verbose'])
        >>> print args.verbose
        True
        """
    parser = argparse.ArgumentParser(usage='$ python logger.py',
                                     description='Get the latest MTA alerts and add any new ones.',
                                     epilog='Example use: python logger.py')
    parser.add_argument("-v", "--verbose", dest="verbose", default=False, action="store_true")
    parser.add_argument("files", nargs="*", help="Path to files to ingest manually")
    args = parser.parse_args(args)
    return args

if __name__ == '__main__':
    args = build_parser(sys.argv[1:])

    if args.verbose == True:
        doctest.testmod(verbose=args.verbose)
    main(args)
