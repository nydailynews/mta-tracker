#!/usr/bin/env python
# Download and log the MTA's status updates. We only log changes.
#from __future__ import print_function
import argparse
import doctest
import json
import os
import random
import string
import re
import sys
from datetime import datetime, timedelta

from logger import Logger, build_parser

if __name__ == '__main__':
    # Write the previous day's archives
    args = build_parser([])
    log = Logger(args)
    fields = ['start', 'stop', 'line', 'length']
    fields_str = ','.join(fields)
    for limit in [10, 30, 60, 90]:
        i = 0
        archives = {}
        while i < limit:
            i += 1
            d_ = datetime.now() - timedelta(i)
            d = d_.date().__str__()
            params = { 'date': d,
                    'select': fields_str
                    }
            rows = log.db.q.select_archive(**params)
            archives[d] = log.db.q.make_dict(fields, rows)
        fh = open('_output/archives-%d.json' % limit, 'wb')
        json.dump(archives, fh)
        fh.close()
