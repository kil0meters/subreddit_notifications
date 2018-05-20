import sqlite3 as lite
import json
import sys
from secrets import WHITELISTED_USERS

def connect():
    db = lite.connect('users.db')
    cur = db.cursor()
    cur.execute("create table if not exists users (username text, filters text, subreddits text)")
    db.commit()
    return db

def users(con):
    cur = con.cursor()
    cur.execute("select * from users")
    rows = cur.fetchall()
    return rows

def update_user(data, db):
    cur = db.cursor()
    username = data['username']
    if username not in WHITELISTED_USERS:
        print("The user is not whitelisted")
        return
    filters = '(?i)(' + '|'.join(data['filters']) + ')'
    subreddits = ','.join(data['subreddits'])

    data = cur.execute("select username from users where username=?", (username,))
    if data.fetchall():
        cur.execute('update users set filters="{}", subreddits="{}" where username="{}"'.format(filters,subreddits,username))
        db.commit()
        return
    else:
        print("Creating new user: " + username)
        cur.execute('insert into users values ("{}", "{}", "{}")'.format(username, filters, subreddits))
        db.commit()
        return

def remove_user(user, con):
    cur = con.cursor()
    cur.execute("drop {} from users".format(user))
    con.commit()
