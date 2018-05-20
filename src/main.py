#!/usr/bin/python3
import datetime
import re
import time
import data
import json
import reddit

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
def apply_filters(posts_by_subreddit, subs, username, db):
    new_posts_by_subreddit = {}
    for sub, posts in posts_by_subreddit.items():
        if sub not in subs:
            continue
        new_posts = []
        filter = data.get_filter(db, username, sub)[0]
        for post in posts:
            if re.match(filter, post[0]):
                new_posts.append(post)
        new_posts_by_subreddit[sub] = new_posts
    return new_posts_by_subreddit

# uses system notify-send command to post notification on linux
def send_updates(posts, username, account):
    current_time = time.mktime(datetime.datetime.utcnow().timetuple())
    subject = 'New Posts from '
    total_content = ''
    for subreddit, posts in posts_by_subreddit.items():
        if posts:
            subject += '/r/{} '.format(subreddit)
            total_content += '#r/' + subreddit
            total_content += '\n---\n\n'
            for post in posts:
                seconds = int(current_time - (post[2] + 25200))
                total_content += "**[{}]({})** ^([{} seconds ago])\n\n".format(post[0], post[1], seconds)
    if total_content != '':
        reddit.send_pm(subject, total_content, username, account)

if __name__ == '__main__':
    account = reddit.connect()
    db = data.connect()
    most_recent_time = 0
    interval = 30
    while True:
        reddit.update_users(db, account)
        global_sub_list = data.subreddits(db)
        subs = data.subreddits(db)
        user_list = data.users(db)
        if global_sub_list:
            posts_by_subreddit = reddit.fetch_posts(subs, account)

            posts_by_subreddit_by_users = {}
            for user in user_list:
                most_recent_time, posts_by_subreddit = get_new_posts(posts_by_subreddit, most_recent_time)
                posts_by_subreddit = apply_filters(posts_by_subreddit, user[1], user[0], db)
                try:
                    posts_by_subreddit_by_users[user[0]] += posts_by_subreddit
                except:
                    posts_by_subreddit_by_users[user[0]] = posts_by_subreddit

            for username, posts in posts_by_subreddit_by_users.items():
                send_updates(posts, username, account)