# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 22:38:45 2023

@author: a.a.carrion.almagro
"""

import sqlite3
import pandas as pd

def createDB(name):
    try:        
        conn = sqlite3.connect(name+".db")
        
        conn.execute("""create table activities (
                            id text primary key,
                            type text,
                            is_virtual text,
                            athlete_name text,
                            athlete_id text,
                            athlete_sex text,
                            activity_date text,
                            activity_date_epoc text,
                            cursor_updated_at text,
                            entity text,
                            name text,
                            stat_distance,
                            stat_pace,
                            stat_time,
                            stat_avg,
                            stat_speed,
                            stat_avg_temp,
                            stat_avg_power,
                            stat_cal,
                            stat_avg_hr,
                            stat_elev_gain
                            )""")
    finally:
        conn.close()
        
def initConn(db_name):
    return sqlite3.connect(db_name+".db")

# return DF
def getAll(db_name):
    try:
        conn = sqlite3.connect(db_name+".db")
        cur = conn.cursor()
        res = cur.execute("SELECT * FROM activities")
        columns = list(map(lambda x: x[0], cur.description))
        rows = res.fetchall()
        df = pd.DataFrame(rows, columns=columns)
        return df
    finally:
        conn.close()

def getActivity(conn, activity_id):
    try:
        cur = conn.cursor()
        sql_sentence = f"SELECT * FROM activities WHERE id={activity_id}"
        res = cur.execute(sql_sentence)
        result = res.fetchall()
        return result
    except Exception as e:
        print(e)
        pass

    
def insertJson(conn, record):
    try:
        cur = conn.cursor()
        keys = ', '.join(record.keys())
        values = tuple(record.values())
        param = ', '.join(['?'] * len(values))
        table = 'activities'
        
        sql_sentence = f"INSERT INTO {table} ({keys}) VALUES ({param})"
        cur.execute(sql_sentence, values)
        conn.commit()
    except Exception as e:
        # print(e)
        pass
    
def emptyDB(db_name):  
    try:
        conn=sqlite3.connect(db_name+".db")
        cur = conn.cursor()
        cur.execute("DELETE FROM activities")
        conn.commit()
    finally:
        conn.close()