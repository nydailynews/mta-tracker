#!/usr/bin/env python
#from __future__ import print_function
import sys
import argparse
import doctest
import sqlite3
from datetime import datetime, time
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
        self.tables = ['active', 'current', 'raw', 'archive', 'averages']

    def setup(self, table=None):
        """ Create the tables.
            >>> s = Storage('test')
            >>> s.setup()
            True
            """
        # INDEXNAME, TABLENAME, COLUMNNAME
        # self.c.execute('CREATE INDEX ? ON ?(?)', value)
        if not table or table == 'active':
            self.c.execute('DROP TABLE IF EXISTS active')
            self.c.execute('''CREATE TABLE active 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, datestamp DATESTAMP DEFAULT CURRENT_TIMESTAMP, line TEXT, type TEXT, start DATETIME, cause TEXT)''')
            #self._setup_active()

        if not table or table == 'current':
            self.c.execute('DROP TABLE IF EXISTS current')
            self.c.execute('''CREATE TABLE current 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, datestamp DATESTAMP DEFAULT CURRENT_TIMESTAMP, line TEXT, type TEXT, start DATETIME, stop DATETIME, cause TEXT)''')
            self._setup_current()

        if not table or table == 'raw':
            self.c.execute('DROP TABLE IF EXISTS raw')
            self.c.execute('''CREATE TABLE raw
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, datestamp DATESTAMP DEFAULT CURRENT_TIMESTAMP, start DATETIME, stop DATETIME, line TEXT, type TEXT, is_rush INT, is_weekend INT, cause TEXT)''')
        #self.c.execute('''CREATE TABLE IF NOT EXISTS minute
        #     (id INTEGER PRIMARY KEY AUTOINCREMENT, datestamp DATESTAMP DEFAULT CURRENT_TIMESTAMP, datetime DATE, line TEXT, type TEXT, cause TEXT)''')

        if not table or table == 'archive':
            self.c.execute('DROP TABLE IF EXISTS archive')
            self.c.execute('''CREATE TABLE archive
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, datestamp DATESTAMP DEFAULT CURRENT_TIMESTAMP, start DATETIME, stop DATETIME, line TEXT, type TEXT, is_rush INT, is_weekend INT, sincelast INT, length INT, active INT, direction TEXT, cause TEXT)''')

        if not table or table == 'averages':
            self.c.execute('DROP TABLE IF EXISTS averages')
            self.c.execute('''CREATE TABLE averages 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, datestamp DATESTAMP DEFAULT CURRENT_TIMESTAMP, datetype TEXT, line TEXT, type TEXT, is_rush INT, is_weekend INT, direction TEXT)''')

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

    @staticmethod
    def is_rush(value):
        """ Takes a datetime object and returns whether it happened in rush hour.
            Returns True or False.
            >>> s = Storage('test')
            >>> print s.q.is_rush(s.q.convert_to_datetime('2017-01-01 00:00:00'))
            0
            """
        if 6 <= value.hour < 9 or 16 <= value.hour < 7:
            return 1
        return 0

    @staticmethod
    def is_weekend(value):
        """ Takes a datetime object and returns whether it happened on a weekend.
            Returns True or False.
            >>> s = Storage('test')
            >>> print s.q.is_weekend(s.q.convert_to_datetime('2017-01-01 00:00:00'))
            1
            >>> print s.q.is_weekend(s.q.convert_to_datetime('2017-01-03 00:00:00'))
            0
            """
        if value.weekday() >= 5:
            return 1
        return 0

    def update_active(self, **kwargs):
        """ Update the "current" table with the latest alert datetime.
            >>> s = Storage('test')
            >>> s.setup()
            True
            >>> d = { 'start': datetime(2017, 1, 1, 0, 0, 0), 'line': 'A', 'transit_type': 'subway', 'cause': 'Test' }
            >>> print s.q.update_active(**d)
            True
            """
        sql = 'UPDATE current SET start = "%s", cause = "%s" WHERE line = "%s" and type = "%s"' \
              % (self.convert_datetime(kwargs['start']), kwargs['cause'], kwargs['line'], kwargs['transit_type'])
        self.c.execute(sql)
        return True

    def update_current(self, **kwargs):
        """ Update the "current" table with the latest alert datetime.
            >>> s = Storage('test')
            >>> s.setup()
            True
            >>> d = { 'start': datetime(2017, 1, 1, 0, 0, 0), 'line': 'A', 'transit_type': 'subway', 'cause': 'Test' }
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

    '''
    def update_minute(self, **kwargs):
        """ Update the "minute" table with the current number of minutes since midnight and the number of alerts
            >>> s = Storage('test')
            >>> s.setup()
            True
            >>> d = { 'minute': datetime(2017, 1, 1, 0, 0, 0), 'count': 3, 'transit_type': 'subway' }
            >>> print s.q.update_minute(**d)
            True
            """
        #(id INTEGER PRIMARY KEY AUTOINCREMENT, datestamp DATESTAMP DEFAULT CURRENT_TIMESTAMP, date TEXT, minute INT, count INT, type TEXT)
        sql = 'INSERT INTO minute VALUES (?, ?, ?, ?, ?)'
        values = (None, self.convert_datetime(datetime.now()), kwargs['minute'], kwargs['count'], kwargs['transit_type'])
        self.c.execute(sql, values)
        return True
    '''

    def update_archive(self, **kwargs):
        """ Update the "archive" table with the records of the starts and stops for each line's alerts.
            Note that the calling command when we have a stop will include the start time (to make lookups easier).
            db fields: id, datestamp, start, stop, line, type, is_rush, is_weekend, sincelast, length, active, cause
            >>> s = Storage('test')
            >>> s.setup()
            True
            >>> d = { 'start': datetime(2017, 1, 1, 0, 0, 0), 'line': 'A', 'transit_type': 'subway', 'cause': 'Test' }
            >>> print s.q.update_archive(**d)
            True
            >>> d = { 'stop': datetime(2017, 1, 1, 3, 0, 0), 'length': 10800, 'line': 'A', 'transit_type': 'subway', 'cause': 'Test' }
            >>> print s.q.update_archive(**d)
            True
            """
        if 'stop' in kwargs:
            stop = kwargs['stop']
            is_rush = self.is_rush(stop)
            is_weekend = self.is_weekend(stop)
            sql = 'UPDATE archive SET stop = "%s", length = %d, active = 0 WHERE line = "%s" and type = "%s" AND cause = "%s" AND active = 1' \
                  % (self.convert_datetime(stop), kwargs['length'], kwargs['line'], kwargs['transit_type'], kwargs['cause'])
            self.c.execute(sql)
        elif 'start' in kwargs:
            start = kwargs['start']
            is_rush = self.is_rush(start)
            is_weekend = self.is_weekend(start)
            sql = '''INSERT INTO archive
                (start, line, type, is_rush, is_weekend, active, cause)
                VALUES
                (?, ?, ?, ?, ?, ?, ?)'''
            values = (self.convert_datetime(start), kwargs['line'], 'subway', is_rush, is_weekend, 1, kwargs['cause'])
            self.c.execute(sql, values)
        return True

    def make_dict(self, fields, rows):
        """ Return a list of dicts of query results.
            >>> s = Storage('test')
            >>> s.setup()
            True
            >>> fields = s.q.get_table_fields('current')
            >>> rows = s.q.select_current()
            >>> d = s.q.make_dict(fields, rows[:1])
            >>> # d will look something like
            >>> # [{u'datestamp': u'2017-07-09 21:46:00', u'line': u'ALL', u'type': u'subway', u'id': 1, u'alert': '2017-07-09 20:04:00'}]
            >>> print d[0]['type'], d[0]['id']
            subway 1
            """
        items = []
        try:
            for row in rows:
                items.append(dict(zip(fields, row)))
        except:
            # This fires when there's only one row
            items.append(dict(zip(fields, rows)))
        return items

    def get_table_records(self, table):
        """ Get all the records in a particular table.
            >>> s = Storage('test')
            >>> s.setup()
            True
            >>> print s.q.get_table_records('archive')
            []
            """
        sql = 'SELECT * FROM %s' % table
        self.c.execute(sql)
        records = [tup[0] for tup in self.c.fetchall()]
        return records

    def get_tables(self):
        """ Get the names of the tables in the database.
            >>> s = Storage('test')
            >>> s.setup()
            True
            >>> print s.q.get_tables()
            [u'sqlite_sequence', u'current', u'raw', u'archive', u'averages']
            """
        sql = 'SELECT name FROM sqlite_master WHERE type = "table"'
        self.c.execute(sql)
        tables = [tup[0] for tup in self.c.fetchall()]
        return tables

    def get_table_fields(self, table):
        """ Get the fields in a table for more useful query results.
            >>> s = Storage('test')
            >>> s.setup()
            True
            >>> print s.q.get_table_fields('current')
            [u'id', u'datestamp', u'line', u'type', u'start', u'stop', u'cause']
            >>> print s.q.get_table_fields('archive')
            [u'id', u'datestamp', u'start', u'stop', u'line', u'type', u'is_rush', u'is_weekend', u'sincelast', u'length', u'active', u'cause']
            """
        sql = 'PRAGMA TABLE_INFO(%s)' % table
        self.c.execute(sql)
        fields = [tup[1] for tup in self.c.fetchall()]
        return fields

    def query_all(self, table, **params):
        """ Basic query, returns all rows.
            """
        clause = '*'
        if 'clause' in params:
            clause = params['clause']
        sql = 'SELECT %s FROM %s' % (clause, table)
        self.c.execute(sql)
        rows = self.c.fetchall()
        return rows

    def select_current(self):
        """ Select the contents of the current table, return a list.
            >>> s = Storage('test')
            >>> s.setup()
            True
            >>> rows = s.q.select_current()
            >>> print rows[0][2:]
            (u'ALL', u'subway', 0, 0, u'')
            """
        return self.query_all('current')

    def select_archive(self, **params):
        """ Select from the archive table.
            >>> s = Storage('test')
            >>> s.setup()
            True
            >>> rows = s.q.select_archive()
            >>> print rows[0][2:]
            """
        clause, values = '', ()
        if 'date' in params:
            clause = ' WHERE start LIKE ? OR stop LIKE ?'
            date_str = '%s%%' % params['date']
            values = (date_str, date_str)
        sql = 'SELECT * FROM archive%s' % clause
        self.c.execute(sql, values)
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
    #parser.add_argument("--setup", dest="setup", default=None, help="Run the setup method on a particular table")
    args = parser.parse_args(args)
    return args


if __name__ == '__main__':
    args = build_parser(sys.argv[1:])

    if args.test:
        doctest.testmod(verbose=args.verbose)
