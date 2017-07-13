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
import dicts

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

class Logger:
    """ We're logging how long it has been since each line's previous
        service alert, and to do that we need to keep track of which lines
        have active service alerts and the timestamp on that alert.
        """

    def __init__(self, *args):
        """
            >>>
            """
        # Get the results from the last time we ran this.
        try:
            fh = open('_output/current.json', 'rb')
            self.previous = json.load(fh)
            fh.close()
        except:
            pass

        self.args = args
        self.db = Storage('mta')
        self.mta = ParseMTA()

    def initialize_db(self):
        """
            >>>
            """
        print "INITIAL"
        os.remove('mta.db')
        self.db = Storage('mta')
        self.db.setup()
        return True

    def get_files(self, files_from_args):
        """
            >>>
            """
        if files_from_args == []:
            # If we didn't pass any arguments to logger, we download the current XML
            rando = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
            url = 'http://web.mta.info/status/serviceStatus.txt?%s' % rando
            fh = FileWrapper('_input/mta.xml')
            fh.open()
            fh.write(fh.request(url))
            fh.close()
            files = ['mta.xml']
        else:
            files = files_from_args
            if '*' in args.files[0]:
                # Wildcard matching on filenames so we can process entire directories
                pass
            if files_from_args[0][-1] == '/':
                # If the arg ends with a forward slash that means it's a dir
                files = os.listdir(files_from_args[0])
        return files

    def compare(self):
        """ Compare the previous json of alerts with the current. Store the
            diffs in a new object.
            >>>
            """
        pass

    def parse_file(self, fn, *args):
        """ Pull out the data we need from the MTA's XML.
            You'd think XML would be well structured. You'd be about half right.
            >>>
            """
        type_ = 'subway'
        if hasattr(args, 'type_'):
            type_ = args.type_

        self.stop_check = dicts.lines
        items = {}
        e = ET.parse('_input/%s' % fn)
        r = e.getroot()
        # Options beside subway:
        # bus, BT, LIRR, MetroNorth
        lines = {}
        for l in r.find(type_):
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
                item['status_detail'] = self.mta.extract(item)
                items[item['status']].append(item)
                if hasattr(self.args, 'verbose'):
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
                            if hasattr(self.args, 'verbose'):
                                print line, dt, len(lines[line].datetimes)

        return lines
        

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

    log = Logger()
    if args.initial:
        log.initialize_db()
    files = log.get_files(args.files)
        
    for fn in files:
        lines = log.parse_file(fn)

    for line, item in lines.iteritems():
        print line, item
        # Make sure this is a new record
        # We only want to update the database on new records.
        for prev in log.previous:
            if line == prev['line']:
                prev_record = prev
        if prev['start'] != 0:
            prev_dt = log.db.q.convert_to_datetime(prev['start'])

        # Update the current table in the database
        params = { 'line': line, 'start': item.datetimes[0] }
        log.db.q.update_current(**params)

        # Remove the line from the list of lines we check to see if there's a finished alert.
        if line in log.stop_check['MTA']:
            log.stop_check['MTA'].remove(line)

    # Check the previous file to see if there are active alerts with lines
    # matching a line in our stop_check file. If there are, we need to update
    # the stop value of that line's record in the database, because that means
    # an alert has ended.
    for prev in log.previous:
        if prev['line'] in log.stop_check['MTA']:
            params = { 'line': prev['line'], 'stop': datetime.now() }
            log.db.q.update_current(**params)
    log.db.conn.commit()

    # Write the current data to json.
    fields = log.db.q.get_table_fields('current')
    rows = log.db.q.select_current()
    fh = open('_output/current.json', 'wb')
    json.dump(log.db.q.make_dict(fields, rows), fh)
    fh.close()
    log.db.conn.close()
  

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
