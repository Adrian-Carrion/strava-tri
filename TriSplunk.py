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

urllib3.disable_warnings()

utc_date_str = '2023-06-30 12:00:00'
dt = datetime.strptime(utc_date_str, '%Y-%m-%d %H:%M:%S')
epoch_date_time = datetime.now().timestamp()
# epoch_date_time = dt.timestamp()
before =epoch_date_time# 1688068009 #1687986440 
cursor = before

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


def cleanActivity(a, fields2keep):
    result = {}
    a = flatten(a)
    for k in a:
        if k in fields2keep.keys(): result[fields2keep[k]] = a[k]
    result = extractStats(result)
    return result
        

def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key.lower(), v))
    return dict(items)

def extractStats(activity):
    result_stat = {}
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
print(datetime.fromtimestamp(1688250407))
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

print("New cursor: %s" % datetime.fromtimestamp(cursor))
activities = []
df_activities = pd.DataFrame()
response = requests.request("GET", url, headers=headers, data=payload, verify=False)
# print(response.text)
r = response.json()
while r['pagination']['hasMore']:

    url = f"https://www.strava.com/clubs/331843/feed?feed_type=club&athlete_id=20997100&club_id=331843&before={before}&cursor={cursor}"
    response = requests.request("GET", url, headers=headers, data=payload, verify=False)
    r = response.json()
    print(len(r['entries']))
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
            activities.append(tmp_activity)
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
                
                activities.append(tmp_activity)
#%%
    clean_activities = []
    for a in activities:
        clean_activities.append(cleanActivity(a, FIELDS2KEEP))
        # print(a_clean)
        
    df = pd.DataFrame(clean_activities)
        
    df = df.sort_values(by='cursor_updated_at')
    df_activities.append(df, ignore_index=False, verify_integrity=False)
    before = df.iloc[0]['cursor_updated_at']
    cursor = before
    print("New cursor: %s" % datetime.fromtimestamp(cursor))
    
    import json
    with open('result.json', 'w',  encoding='utf-8') as fp:
        json.dump(activities, fp, ensure_ascii=False)

    df.to_csv('strava.csv')
