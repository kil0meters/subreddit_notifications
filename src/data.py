import sqlite3 as lite
import json
import sys

WHITELISTED_USERS = ['kil0meters', 'genericasianperson']

def connect():
    db = lite.connect('users.db')
    cur = db.cursor()
    cur.execute("create table if not exists users (name text, filters text, subreddits text)")
    db.commit()
    return db

def users(con):
    cur = con.cursor()
    cur.execute("select * from users")
    rows = cur.fetchall()
    return rows

def update_user(data, con):
    cur = con.cursor()
    username = data['username']
    if username not in WHITELISTED_USERS:
        return
    filters = '(?i)(' + '|'.join(data['filters']) + ')'
    subreddits = ','.join(data['subreddits'])

    data = cur.execute("select name from users where name= ?", (username,))
    print(data)
    if data:
        cur.execute('update users set filters="{}", subreddits="{}" where name="{}"'.format(filters,subreddits,username))
        con.commit()
    else:
        cur.execute('insert into users values ("{}", "{}", "{}")'.format(username, filters, subreddits))
        con.commit()

def remove_user(user, con):
    cur = con.cursor()
    cur.execute("drop {} from users".format(user))
    con.commit()
