#!/usr/bin/env python
import sys
import argparse
import doctest
import sqlite3
from datetime import datetime

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
            """
        self.c.execute('''CREATE TABLE IF NOT EXISTS current 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, datestamp DATESTAMP DEFAULT CURRENT_TIMESTAMP, line TEXT, type TEXT, alert DATETIME)''')
        # INDEXNAME, TABLENAME, COLUMNNAME
        #self.c.execute('CREATE INDEX ? ON ?(?)', value)
        self._setup_current()

        self.c.execute('''CREATE TABLE IF NOT EXISTS raw
             (id INTEGER PRIMARY KEY AUTOINCREMENT, datetime DATETIME, line TEXT, type TEXT, is_rush INT, is_weekend INT)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS archive
             (id INTEGER PRIMARY KEY AUTOINCREMENT, datetime DATETIME, line TEXT, type TEXT, is_rush INT, is_weekend INT, sincelast INT)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS averages 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, datetype TEXT, line TEXT, type TEXT, is_rush INT, is_weekend INT)''')

    def _setup_current(self):
        """ Populate the current table.
            """
        lines = ['ALL','1','2','3','4','5','6','7','A','C','E','B','D','F','M','N','Q','R','J','Z','G','L','W']
        items = []
        for item in lines:
            items.append((None, self.q.convert_datetime(datetime.now()), item, 'MTA', 0))
        sql = 'INSERT INTO current VALUES (?, ?, ?, ?, ?)'
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

    def update_current(self, **kwargs):
        """ Update the "current" table with the latest alert datetime.
            >>> s = Storage('test')
            >>> s.setup()
            >>> d = { 'alert': datetime(2017, 1, 1, 0, 0, 0), 'line': 'A' }
            >>> print s.q.update_current(**d)
            True
            """
        sql = 'UPDATE current SET alert = "%s" WHERE line = "%s" and type = "MTA"'\
             % (self.convert_datetime(kwargs['alert']), kwargs['line'])
        #print sql
        self.c.execute(sql)
        return True

    def select_current(self):
        """ Select the contents of the current table.
            >>> s = Storage('test')
            >>> s.setup()
            >>> rows = s.q.select_current()
            >>> print rows[0]
            (1, u'2017-07-09 21:46:00', u'ALL', u'MTA', 0)
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

    if args.test== True:
        doctest.testmod(verbose=args.verbose)
