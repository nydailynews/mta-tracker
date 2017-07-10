#!/usr/bin/env python
# Download and log the MTA's status updates. We only log changes.
import argparse
import doctest
import json
import os
import random
import string
import sys
import xml.etree.ElementTree as ET
from datetime import datetime

from filewrapper import FileWrapper
from parser import ParseMTA
from sqliter import Storage, Query


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

    def __init__(self, line):
        """
            >>> l = Line('A')
            >>> print l.line
            A
            """
        self.lines = {}
        self.datetimes = []
        self.intervals = []
        self.line = line
        self.last_alert = ''

    def parse_dt(self, dt):
        """ Take a datetime such as 06/01/2017 10:31PM and turn it into
            a datetime object.
            >>> l = Line('L')
            >>> dt = '06/01/2017 10:31PM'
            >>> print l.parse_dt(dt)
            2017-06-01 22:31:00
            """
        return datetime.strptime(dt, '%m/%d/%Y %I:%M%p')

    def build_intervals(self):
        """ Populate the self.intervals list with the time between each service alert.
            >>>
            """
        pass

def main(args):
    """ There are two situations we run this from the command line: 
        1. When building archives from previous day's service alerts and
        2. When keeping tabs on the current days's service alerts.

        Most of what we do here for each is the same, but with #2 we only
        process one file, and we have to look up stored information to ensure
        the intervals values are current.
        >>> args = build_parser(['--verbose'])
        >>> main(args)
        """
    mta = ParseMTA()

    if args.initial:
        print "INITIAL"
        os.remove('mta.db')
        db = Storage('mta')
        db.setup()
    else:
        db = Storage('mta')
    
    dir_ = ''
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
        if args.files[0][-1] == '/':
            # If the arg ends with a forward slash that means it's a dir
            files = os.listdir(args.files[0])
            dir_ = '_input/'
        
    lines = {}
    for fn in files:
        items = {}
        e = ET.parse('%s%s' % (dir_, fn))
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
                if args.verbose:
                    if item['status'] == 'DELAYS':
                        print '%(status)s: %(lines)s (%(datetime)s)' % item

            # Assemble this file's delays into its individual lines
            if 'DELAYS' in items:
                for item in items['DELAYS']:
                    for line in item['status_detail']['TitleDelay']:
                        if line not in lines:
                            lines[line] = Line(line)
                        dt = lines[line].parse_dt(item['datetime'])
                        if dt not in lines[line].datetimes:
                            lines[line].datetimes.append(dt)
                            if args.verbose:
                                print line, dt, len(lines[line].datetimes)

    for item in lines.iteritems():
        line = item[1]
        # Update the current table in the database
        params = { 'line': item[0], 'alert': line.datetimes[0] }
        db.q.update_current(**params)
    db.conn.commit()
    db.conn.close()
  

def build_parser(args):
    """ This method allows us to test the args.
        >>> args = build_parser(['--verbose'])
        >>> print args.verbose
        True
        """
    parser = argparse.ArgumentParser(usage='$ python logger.py',
                                     description='Get the latest MTA alerts and add any new ones.',
                                     epilog='Example use: python logger.py')
    parser.add_argument("-i", "--initial", dest="initial", default=False, action="store_true")
    parser.add_argument("-v", "--verbose", dest="verbose", default=False, action="store_true")
    parser.add_argument("--test", dest="test", default=False, action="store_true")
    parser.add_argument("files", nargs="*", help="Path to files to ingest manually")
    args = parser.parse_args(args)
    return args

if __name__ == '__main__':
    args = build_parser(sys.argv[1:])

    if args.test== True:
        doctest.testmod(verbose=args.verbose)
    main(args)
