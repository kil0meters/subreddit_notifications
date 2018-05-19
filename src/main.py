#!/usr/bin/python3
import datetime
import os
import re
import subprocess
import time
import xml.etree.ElementTree as ET
import requests
import json
import data
import reddit

# loads sqlite database, gets new posts on all of the new subreddits
# pms them the new posts that match their tags and subreddits

# fetches content on https://reddit.com/r/SUBREDDIT/new
def fetch_posts(subreddits):
    posts_by_subreddit = {}
    for subreddit in subreddits:
        subreddit_posts = []
        url = "http://reddit.com/r/{}/new/.rss".format(subreddit)
        headers = {
            'User-Agent': ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, " +
                           "like Gecko) Chrome/59.0.3071.109 Safari/537.36")
        }
        res = requests.get(url, headers=headers)
        #print(r.text)
        #print(subreddit)
        tree = ET.fromstring(res.text)
        for child in tree:
            if child.tag == "{http://www.w3.org/2005/Atom}entry":
                title = child[-1].text

                link = child[-3].attrib['href']

                post_time_string = child[-2].text
                if post_time_string.endswith("+00:00"):
                    post_time_string = post_time_string[:-6]
                post_time = time.mktime(time.strptime(post_time_string, '%Y-%m-%dT%H:%M:%S'))

                subreddit_posts.append([title, link, post_time, subreddit])
        posts_by_subreddit[subreddit] = subreddit_posts
        time.sleep(2)
    return posts_by_subreddit

# only shows posts that are new
def get_new_posts(posts_by_subreddit, most_recent_time):
    new_posts_by_subreddit = {}
    is_new_posts = False
    times = []
    for subreddit, posts in posts_by_subreddit.items():
        new_posts = []
        for post in posts:
            if post[2] > most_recent_time:
                times.append(post[2])
                is_new_posts = True
                new_posts.append([post[0], post[1], post[2]])
            else:
                break
        new_posts_by_subreddit[subreddit] = new_posts
    if is_new_posts:
        most_recent_time = max(times) + 1
    return most_recent_time, new_posts_by_subreddit

# only shows posts that match certain filters
def apply_filters(posts_by_subreddit, filters):
    new_posts_by_subreddit = {}
    for (subreddit, posts) in posts_by_subreddit.items():
        new_posts = []
        for post in posts:
            if re.match(filters, post[0]):
                new_posts.append(post)
        new_posts_by_subreddit[subreddit] = new_posts
    return new_posts_by_subreddit

# uses system notify-send command to post notification on linux
def send_updates(posts_by_subreddit, username, account):
    current_time = time.mktime(datetime.datetime.utcnow().timetuple())
    total_content = ''
    print("posts by subreddit:")
    print(posts_by_subreddit)
    for subreddit, posts in posts_by_subreddit.items():
        total_content += '#r/' + subreddit
        total_content += '\n---\n\n'
        if posts:
            for post in posts:
                how_long_ago = int(current_time - post[2])
                hours = how_long_ago // 3600
                how_long_ago = how_long_ago - (hours * 3600)
                minutes = how_long_ago // 60
                seconds = how_long_ago - (minutes * 60)
                total_content += "**[{}]({})** ^([{} hours {} minutes {} seconds ago])\n\n".format(post[0], post[1], hours, minutes, seconds)
                #if os.name == 'posix':
                    # FIXME: For some reason ANSI escape codes don't work with built in python functions
                    #subprocess.Popen(['echo', '-e', "{} [{} hours {} minutes {} seconds ago]\n{}\n"\
                    #    .format(post[3], hours, minutes, seconds, post[1])])
                #else:
                    #print("{}\n{}\n\n", title, post[1])
        else:
            total_content += "It looks like there's nothing here :(\n"
    reddit.send_pm("New Posts", total_content, username, account)

def main():
    account = reddit.connect()
    db = data.connect()
    users = data.users(db)
    most_recent_time = 0
    interval = 30
    while True:
        for user in users:
            username = user[0]
            filters = user[1]
            subreddits = user[2].split(',')
            posts_by_subreddit = fetch_posts(subreddits)
            most_recent_time, posts_by_subreddit = get_new_posts(posts_by_subreddit, most_recent_time)

            is_new_posts = False
            posts_by_subreddit = apply_filters(posts_by_subreddit, filters)
            for subreddit, posts in posts_by_subreddit.items():
                if posts:
                    is_new_posts = True
                    break
            if is_new_posts:
                send_updates(posts_by_subreddit, username, account)
            time.sleep(2)
        #time.sleep(interval)
        reddit.update_users(db, account)
        users = data.users(db)


main()
