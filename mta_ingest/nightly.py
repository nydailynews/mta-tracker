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
        hours = {
                'all': 0,
                'weekend': 0,
                'weekday': 0
                }
        average = {
                'all': 0,
                'weekend': 0,
                'weekday': 0
                }
        archives, archives_full = {}, {}
        weekdays, weekends = 0, 0
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
                hours['all'] += float(float(r['length'] / 60) / 60)
                if r['is_weekend'] == 1:
                    hours['weekend'] += float(float(r['length'] / 60) / 60)
                    weekends += 1
                else:
                    hours['weekday'] += float(float(r['length'] / 60) / 60)
                    weekdays += 1
            archives[d] = {'delays': delays, 'seconds': length}
        average['all'] = hours['all'] / limit
        average['weekend'] = hours['weekend'] / weekends
        average['weekday'] = hours['weekday'] / weekdays
        fh = open('_output/archives-average-%d.json' % limit, 'wb')
        json.dump({'days': limit, 'hours': hours, 'average': average}, fh)
        fh.close()
        fh = open('_output/archives-full-%d.json' % limit, 'wb')
        json.dump(archives_full, fh)
        fh.close()
        fh = open('_output/archives-%d.json' % limit, 'wb')
        json.dump(archives, fh)
        fh.close()
