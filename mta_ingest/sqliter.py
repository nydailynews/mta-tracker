#!/usr/bin/env python
#from __future__ import print_function
import sys
import argparse
import doctest
import sqlite3
from datetime import datetime
import dicts


class Storage:
    """ Manage data storage and retrieval."""

    def __init__(self, dbname):
        """
            >>> s = Storage('test')
            >>> print s.dbname
            test
            """
        self.dbname = dbname
        self.conn = sqlite3.connect('%s.db' % dbname)
        self.c = self.conn.cursor()
        self.q = Query(self.c)

    def setup(self):
        """ Create the tables.
            >>> s = Storage('test')
            >>> s.setup()
            True
            """
        # INDEXNAME, TABLENAME, COLUMNNAME
        # self.c.execute('CREATE INDEX ? ON ?(?)', value)
        self.c.execute('''CREATE TABLE IF NOT EXISTS current 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, datestamp DATESTAMP DEFAULT CURRENT_TIMESTAMP, line TEXT, type TEXT, start DATETIME, stop DATETIME, cause TEXT)''')
        self._setup_current()

        self.c.execute('''CREATE TABLE IF NOT EXISTS raw
             (id INTEGER PRIMARY KEY AUTOINCREMENT, datestamp DATESTAMP DEFAULT CURRENT_TIMESTAMP, start DATETIME, stop DATETIME, line TEXT, type TEXT, is_rush INT, is_weekend INT, cause TEXT)''')
        #self.c.execute('''CREATE TABLE IF NOT EXISTS minute
        #     (id INTEGER PRIMARY KEY AUTOINCREMENT, datestamp DATESTAMP DEFAULT CURRENT_TIMESTAMP, datetime DATE, line TEXT, type TEXT, cause TEXT)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS archive
             (id INTEGER PRIMARY KEY AUTOINCREMENT, datestamp DATESTAMP DEFAULT CURRENT_TIMESTAMP, start DATETIME, stop DATETIME, line TEXT, type TEXT, is_rush INT, is_weekend INT, sincelast INT, cause TEXT)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS averages 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, datestamp DATESTAMP DEFAULT CURRENT_TIMESTAMP, datetype TEXT, line TEXT, type TEXT, is_rush INT, is_weekend INT)''')

        return True

    def _setup_current(self):
        """ Populate the current table.
            >>> s = Storage('test')
            >>> s.setup()
            True
            """
        lines = dicts.lines['subway']
        items = []
        for item in lines:
            items.append((None, self.q.convert_datetime(datetime.now()), item, 'subway', 0, 0, ''))
        sql = 'INSERT INTO current VALUES (?, ?, ?, ?, ?, ?, ?)'
        self.c.executemany(sql, items)
        self.conn.commit()

    def insert(self, table, **kwargs):
        """
            """
        pass


class Query:
    """ Manage database queries."""

    def __init__(self, c):
        """ This class is dependent on a database connection, which is handed
            to it when the Query object is created.
            >>> s = Storage('test')
            >>> print s.dbname
            test
            """
        self.c = c

    def convert_datetime(self, value):
        """ Turn a datetime object into a string sqlite can handle.
            >>> s = Storage('test')
            >>> print s.q.convert_datetime(datetime(2017, 1, 1, 0, 0, 0))
            2017-01-01 00:00:00
            """
        return datetime.strftime(value, '%Y-%m-%d %H:%M:00')

    @staticmethod
    def convert_to_datetime(value):
        """ Turn a string into a datetime object.
            >>> s = Storage('test')
            >>> print s.q.convert_to_datetime('2017-01-01 00:00:00')
            datetime(2017, 1, 1, 0, 0, 0)
            """
        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')

    def update_current(self, **kwargs):
        """ Update the "current" table with the latest alert datetime.
            >>> s = Storage('test')
            >>> s.setup()
            >>> d = { 'start': datetime(2017, 1, 1, 0, 0, 0), 'line': 'A', 'transit_type': 'subway' }
            >>> print s.q.update_current(**d)
            True
            """
        if 'start' in kwargs:
            sql = 'UPDATE current SET start = "%s", stop = "-1", cause = "%s" WHERE line = "%s" and type = "%s"' \
                  % (self.convert_datetime(kwargs['start']), kwargs['cause'], kwargs['line'], kwargs['transit_type'])
        if 'stop' in kwargs:
            sql = 'UPDATE current SET start = "0", stop = "%s" WHERE line = "%s" and type = "%s"' \
                  % (self.convert_datetime(kwargs['stop']), kwargs['line'], kwargs['transit_type'])
        self.c.execute(sql)
        return True

    def update_minute(self, **kwargs):
        """ Update the "minute" table with the current number of minutes since midnight and the number of alerts
            >>> s = Storage('test')
            >>> s.setup()
            >>> d = { 'minute': datetime(2017, 1, 1, 0, 0, 0), 'count': 3, 'transit_type': 'subway' }
            >>> print s.q.update_minute(**d)
            True
            """
        #(id INTEGER PRIMARY KEY AUTOINCREMENT, datestamp DATESTAMP DEFAULT CURRENT_TIMESTAMP, date TEXT, minute INT, count INT, type TEXT)
        sql = 'INSERT INTO minute VALUES (?, ?, ?, ?, ?)'
        values = (None, self.convert_datetime(datetime.now()), kwargs['minute'], kwargs['count'], kwargs['transit_type'])
        self.c.execute(sql, values)
        return True

    def update_archive(self, **kwargs):
        """ Update the "archive" table with the records of the starts and stops for each line's alerts.
            >>> s = Storage('test')
            >>> s.setup()
            >>> d = { 'start': datetime(2017, 1, 1, 0, 0, 0), 'line': 'A', 'transit_type': 'subway' }
            >>> print s.q.update_current(**d)
            True
            """
        return True

    def make_dict(self, fields, rows):
        """ Return a list of dicts of query results.
            >>> s = Storage('test')
            >>> s.setup()
            >>> fields = s.q.get_table_fields('current')
            >>> rows = s.q.select_current()
            >>> d = s.q.make_dict(fields, rows[:1])
            >>> # d will look something like
            >>> # [{u'datestamp': u'2017-07-09 21:46:00', u'line': u'ALL', u'type': u'subway', u'id': 1, u'alert': '2017-07-09 20:04:00'}]
            >>> print d[0]['type'], d[0]['id']
            MTA 1
            """
        items = []
        try:
            for row in rows:
                items.append(dict(zip(fields, row)))
        except:
            # This fires when there's only one row
            items.append(dict(zip(fields, rows)))
        return items

    def get_table_fields(self, table):
        """ Get the fields in a table for more useful query results.
            >>> s = Storage('test')
            >>> s.setup()
            >>> print s.q.get_table_fields('current')
            [u'id', u'datestamp', u'line', u'type', u'alert']
            """
        sql = 'PRAGMA TABLE_INFO(%s)' % table
        self.c.execute(sql)
        fields = [tup[1] for tup in self.c.fetchall()]
        return fields

    def select_current(self):
        """ Select the contents of the current table, return a list.
            >>> s = Storage('test')
            >>> s.setup()
            >>> rows = s.q.select_current()
            >>> print rows[0][2:]
            (u'ALL', u'subway', 0)
            """
        sql = 'SELECT * FROM current'
        self.c.execute(sql)
        rows = self.c.fetchall()
        return rows


def build_parser(args):
    """ This method allows us to test the args.
        >>> args = build_parser(['--verbose'])
        >>> print args.verbose
        True
        """
    parser = argparse.ArgumentParser(usage='$ python sqliter.py',
                                     description='Test the db classes.',
                                     epilog='Example use: python sqliter.py')
    parser.add_argument("-v", "--verbose", dest="verbose", default=False, action="store_true")
    parser.add_argument("--test", dest="test", default=True, action="store_true")
    args = parser.parse_args(args)
    return args


if __name__ == '__main__':
    args = build_parser(sys.argv[1:])

    if args.test:
        doctest.testmod(verbose=args.verbose)
