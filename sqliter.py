#!/usr/bin/env python
import doctest
import sqlite3
from datetime import datetime

class Storage:
    """ Manage object storage and retrieval."""

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
    """ Manage queries."""

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
            """
        sql = 'UPDATE current SET alert = "%s" WHERE line = "%s" and type = "MTA"'\
             % (self.convert_datetime(kwargs['alert']), kwargs['line'])
        #print sql
        self.c.execute(sql)
        return True
