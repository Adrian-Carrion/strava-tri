# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 23:24:08 2023

@author: a.a.carrion.almagro
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Jun 30 00:36:58 2023

@author: a.a.carrion.almagro
"""

import requests
from datetime import datetime
import re
import collections.abc
import pandas as pd
from datetime import date
from datetime import timedelta
import urllib3
from sql import createDB, initConn, getAll, emptyDB, insertJson, getActivity
import logging
import os
urllib3.disable_warnings()

current_file_dir = os.path.dirname(__file__)
log_filename = os.path.join(current_file_dir,'TriDB.log')
logging.basicConfig(level=logging.INFO,filename=log_filename, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# =============================================================================
# Aux method: flatten json and remove unnecesary fields
# =============================================================================
def cleanActivity(a, fields2keep):
    result = {}
    a = flatten(a)
    for k in a:
        if k in fields2keep.keys(): result[fields2keep[k]] = a[k]
    result = extractStats(result)
    return result

# =============================================================================
# Aux method: flatten json
# =============================================================================
def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.abc.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key.lower(), v))
    return dict(items)

# =============================================================================
# Aux method: extract stats from activity
# =============================================================================
def extractStats(activity):
    stats = activity.pop('stats')

    for i in range(0,len(stats),2):
        stat_value = re.sub('(<.*?>)','',stats[i]['value'])
        stat_value = stat_value.replace(',','')
        activity['stat_'+stats[i+1]['value'].lower().replace(' ','_')] = stat_value # stat subtitle
    return activity


def isFormat(date_text, date_format):
        try:
            datetime.strptime(date_text, date_format)
            return True
        except ValueError:
            return False

#%%


FIELDS2KEEP = {
    'id': 'id',
    'type': 'type',
    'isVirtual': 'is_virtual',
    'athlete_athletename': 'athlete_name',
    'athlete_athleteid': 'athlete_id',
    'athlete_sex': 'athlete_sex',
    'timeandlocation_displaydateattime' : 'activity_date',
    'timeandlocation_displaydateattime_epoc': 'activity_date_epoc',
    'cursor_updated_at': 'cursor_updated_at',
    'entity': 'entity',
    'name': 'name',
    'stats': 'stats'
    }

logger = logging.getLogger('StravaSyncActivities')

logger.info('--- Init program ---')
#init dates and things for the requests
now = datetime.now()
cursor = before = now.timestamp()# 1688068009 #1687986440

url = f"https://www.strava.com/clubs/331843/feed?feed_type=club&athlete_id=20997100&club_id=331843&before={before}&cursor={cursor}"
payload={}
headers = {
  'authority': 'www.strava.com',
  'accept': 'application/json, text/plain, */*',
  'accept-language': 'en-US',
  'cookie': 'sp=d408220f-4fb8-4bb5-b417-f8b1c7c500c5; xp_session_identifier=c28d3d6cf5a37569d6b4f6bd2d31bdbe; _gcl_au=1.1.2069285407.1684914883; CloudFront-Policy=eyJTdGF0ZW1lbnQiOiBbeyJSZXNvdXJjZSI6Imh0dHBzOi8vaGVhdG1hcC1leHRlcm5hbC0qLnN0cmF2YS5jb20vKiIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTY4ODM2NDAzN30sIkRhdGVHcmVhdGVyVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNjg3MTQwMDM3fX19XX0_; CloudFront-Key-Pair-Id=APKAIDPUN4QMG7VUQPSA; CloudFront-Signature=Vm3ew6OIsAFCUXKKmjJsUxZYJFQzY1D8sIFLlOIKLYJnkMgrTFaNSf9LDvslsLc0DnNNnNVLiWGFOND6z0R~mgAaASckb5Y54zcL~EHdNBLMBhSSoyHGuXjuMmD9oIn2PQDRu2iOtgEoMCNKW65wSxkRzc1WtDLfrvG0pirq9VcUI9mIonZZBQIa3BeUwS-x8gYTob1V1t0FPPjTL6hKg7GkVyXulKy42d7RT3CClhkXyShuSyuZSgQJE9feq9J1ziT-DPKyqmM3j-qfIo8c6KbJBqqyzYDHUF2XlxhRhF8i1NfE7-qziEm9OnLRFRbxnFK4QCCwCURTGNmV2-2ZIA__; _strava4_session=71dk87ukk7al634k1ohl230k2do4bq1h; _gid=GA1.2.1416851961.1688026963; _sp_ses.047d=*; _dc_gtm_UA-6309847-24=1; _ga=GA1.1.1773445609.1643874570; _sp_id.047d=256080e2-d3c8-4d80-8dd1-17a629047333.1643874507.665.1688072428.1688033670.6ac11496-5e59-4980-8f13-31f0aea1987f; _ga_ESZ0QKJW56=GS1.1.1688069858.38.1.1688072428.13.0.0',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'x-requested-with': 'XMLHttpRequest'
}



activities = []
df_activities = pd.DataFrame()
response = requests.request("GET", url, headers=headers, data=payload, verify=False)
# print(response.text)
r = response.json()
while r['pagination']['hasMore']:
    logger.debug('--- Getting Club activities. Cursor [%s]' % datetime.strftime(now, '%Y-%m-%d %H:%M:%S'))
    url = f"https://www.strava.com/clubs/331843/feed?feed_type=club&athlete_id=20997100&club_id=331843&before={before}&cursor={cursor}"
    response = requests.request("GET", url, headers=headers, data=payload, verify=False)
    r = response.json()
    for e in r['entries']:
        tmp_activity = {}
        tmp_activity['cursor_updated_at'] = e['cursorData']['updated_at']
        if e['entity'] == 'Activity':
            tmp_activity['entity'] = e['entity']
            tmp_activity['name'] = e['activity']['activityName']
            tmp_activity.update(e['activity'])
            tmp_activity['id'] = e['activity']['athlete']['athleteId'] + e['activity']['id']
            if isFormat(e['activity']['timeAndLocation']['displayDateAtTime'], "%B %d, %Y at %I:%M %p"):
                tmp_activity['timeandlocation_displaydateattime_epoc'] = datetime.strptime(e['activity']['timeAndLocation']['displayDateAtTime'],"%B %d, %Y at %I:%M %p").timestamp()
            if isFormat(e['activity']['timeAndLocation']['displayDateAtTime'], "%B %d, %Y"):
                tmp_activity['timeandlocation_displaydateattime_epoc'] = datetime.strptime(e['activity']['timeAndLocation']['displayDateAtTime'],"%B %d, %Y").timestamp()
            if ('Today' in e['activity']['timeAndLocation']['displayDateAtTime']):
                        tmp_activity['timeandlocation_displaydateattime'] = date.strftime(datetime.today(),"%B %d, %Y")
                        tmp_activity['timeandlocation_displaydateattime_epoc'] = datetime.today().timestamp()
            if ('Yesterday' in e['activity']['timeAndLocation']['displayDateAtTime']):
                        yesterday = datetime.today() - timedelta(days = 1)
                        tmp_activity['timeandlocation_displaydateattime'] = date.strftime(yesterday,"%B %d, %Y")
                        tmp_activity['timeandlocation_displaydateattime_epoc'] = yesterday.timestamp()
            activities.append(cleanActivity(tmp_activity,FIELDS2KEEP))
            tmp_activity['id']
        if e['entity'] == 'GroupActivity':
            ga = e['rowData']
            for inner_activity in ga['activities']:
                tmp_activity['entity'] = ga['entity']
                tmp_activity['id'] = str(inner_activity['athlete_id']) + str(inner_activity['activity_id'])
                tmp_activity['stats'] = inner_activity['stats']
                tmp_activity['type'] = inner_activity['type']
                tmp_activity['name'] = inner_activity['name']
                tmp_activity['athlete_athletename'] = inner_activity['athlete_name']
                tmp_activity['athlete_sex'] = inner_activity['athlete_sex']
                dt = datetime.strptime(inner_activity['start_date_local'], '%Y-%m-%dT%H:%M:%SZ')
                long_date = dt.strftime("%B %d, %Y at %I:%M %p")
                tmp_activity['timeandlocation_displaydateattime'] = long_date
                tmp_activity['timeandlocation_displaydateattime_epoc'] = dt = datetime.strptime(inner_activity['start_date_local'], '%Y-%m-%dT%H:%M:%SZ').timestamp()
                tmp_activity['athlete_athleteid'] = inner_activity['athlete_id']

                activities.append(cleanActivity(tmp_activity,FIELDS2KEEP))
    logger.debug('Extracted [%s] activities' % len(activities))
    df = pd.DataFrame(activities)

    df = df.sort_values(by='cursor_updated_at')
    #df_activities.append(df, ignore_index=False, verify_integrity=False)
    pd.concat([df_activities, df], ignore_index=True, verify_integrity=False)

    before = df.iloc[0]['cursor_updated_at']
    cursor = before
    logger.debug('New cursor [%s]' % cursor)
#%%
df = getAll('strava')
logger.debug("DB Size [%s]" % len(df))
logger.debug("Inserting %s activities" % len(activities))
nbInserted = 0
conn=initConn('strava')
for a in activities:
    logger.debug('Inserting activity [%s] activities' % a['id'])
    activity_exist = getActivity(conn, a['id'])
    if activity_exist:
        logger.debug('Activity [%s] already exists. Skipping...' % a['id'])
    else:
        insertJson(conn, a)
        logger.info('Inserted activity [%s]' % a['id'])
        nbInserted += 1
conn.close()
logger.info('Inserted [%s] activities' % nbInserted)
df = getAll('strava')
logger.debug("DB Size [%s]" % len(df))
