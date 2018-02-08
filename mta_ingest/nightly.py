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
    fields = ['start', 'stop', 'line', 'length', 'is_weekend']
    fields_str = ','.join(fields)
    days = [10, 30, 60, 90]
    for limit in days:
        i = 0
        hours = 0
        archives, archives_full = {}, {}
        while i < limit:
            i += 1
            d_ = datetime.now() - timedelta(i)
            d = d_.date().__str__()
            params = { 'date': d,
                    'select': fields_str
                    }
            rows = log.db.q.select_archive(**params)
            archives_full[d] = log.db.q.make_dict(fields, rows)

            results = archives_full[d]
            length = 0
            delays = 0
            for r in results:
                delays += 1
                length += r['length']
            archives[d] = {'delays': delays, 'seconds': length}
            hours += float(float(length / 60) / 60)
        fh = open('_output/archives-average-%d.json' % limit, 'wb')
        json.dump({'days': limit, 'average': hours / limit}, fh)
        fh.close()
        fh = open('_output/archives-full-%d.json' % limit, 'wb')
        json.dump(archives_full, fh)
        fh.close()
        fh = open('_output/archives-%d.json' % limit, 'wb')
        json.dump(archives, fh)
        fh.close()
