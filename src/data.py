import sqlite3 as lite
import json
import sys
from secrets import WHITELISTED_USERS

def connect():
    db = lite.connect('test.db')
    cur = db.cursor()
    cur.execute("create table if not exists users (username text, subreddits text)")
    cur.execute("create table if not exists filters (username text, filter text, subreddit text)")
    db.commit()
    return db

def users(con):
    cur = con.cursor()
    cur.execute("select * from users")
    rows = cur.fetchall()
    return rows

def get_most_recent_time():
    try:
        file = open("most_recent_time.txt", 'r')
        text = file.read()
        file.close()
        return float(text)
    except:
        file = open("most_recent_time.txt", 'a')
        file.close()
        return 0


def set_most_recent_time(most_recent_time):
    file  = open("most_recent_time.txt", 'w')
    file.write(str(most_recent_time))
    file.close()

def get_filter(db, username, sub):
    cur = db.cursor()
    cur.execute('select filter from filters where username="{}" and subreddit="{}"'.format(username, sub))
    return cur.fetchone()

def subreddits(db):
    cur = db.cursor()
    cur.execute('select subreddits from users')
    subs = []
    for subreddit_group in cur.fetchall():
        subs = subs + subreddit_group[0].split(',')
    return subs

def update_user(user_data, db):
    cur = db.cursor()
    username = user_data['username']
    subreddit_filter_list = user_data['subreddits']
    if username not in WHITELISTED_USERS:
        print("The user {} is not whitelisted".format(username))
        return
    subreddit_list = []
    for subreddit in subreddit_filter_list:
        subreddit_list.append(subreddit[0])

    subreddit_list = ','.join(subreddit_list)
    cur.execute('select username from users where username="{}"'.format(username))
    if cur.fetchall():
        print("Updating user: " + username)
        cur.execute('update users set subreddits="{}" where username="{}"'.format(subreddit_list,username))
        cur.execute('delete from filters where username="{}"'.format(username))
    else:
        print("Creating new user: " + username)
        cur.execute('insert into users values ("{}", "{}")'.format(username, subreddit_list))
    for subreddit in subreddit_filter_list:
        cur.execute('insert into filters values ("{}", "(?i)({})", "{}")'.format(username, subreddit[1], subreddit[0]))
    db.commit()

def remove_user(user, con):
    cur = con.cursor()
    cur.execute("drop {} from users".format(user))
    con.commit()
