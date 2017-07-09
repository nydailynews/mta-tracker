# MTA Tracker
How long has it been since a service interruption [checks watch]

## Data structure

These are the database tables, that track:

1. A "current" table, with the latest on each of the lines.
1. An "archive" table, with records of each of the time spans from one line's alert to another. The word we use to describe that time span is a "sincelast."
1. A "raw" table, with alerts and timestamps.
1. An "averages" table, which stores aggregate information about the delays.

## TODO's
[] Workflow for scraping the current status
[] Workflow for ingesting historic data
[] Workflow for calculating timesince's
[] Workflow for updating historic averages
[] Workflow for publishing to prod

## Usage

## Resources

### Look into
https://github.com/jimjshields/mta_service_alerts
https://github.com/craigcurtin/mta/blob/f580068bc5679a9d27d53cbfbd0998a1395f5118/mta.py
https://github.com/nficano/nickficano.com/blob/d2189e092acd9357a23f1c13f3630199ffaa67f1/nickficano/api/mta.py
https://github.com/softdev-projects/mta-smart-alerts/blob/936feb0aec1cc3b4af50b78ee05ea081d9fdd13c/mta.py
https://github.com/craigcurtin/mta/blob/f580068bc5679a9d27d53cbfbd0998a1395f5118/mta.py
https://github.com/jvaleo/mta_status/blob/f874aa0102f81c3f23da344f216c2eb1bee124e4/subway_status.py
https://github.com/DanielSoltis/subwaytracker/blob/ce69fbb2358761e51a358e7a680c0bc8d7b269b6/capture_transit_status.py
https://github.com/zmln/subway-tracker
https://github.com/dr-rodriguez/MTA-Notifier/blob/f0732a90a9fb71a5e560855b96b83f56ef21d7be/notifier.py #uses mailgun api to send email
https://github.com/mikeprevette/mprevdailyshow/blob/8588f9e838713db030cee47541acb86626454c63/app.py


