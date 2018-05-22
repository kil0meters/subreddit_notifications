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
            if re.search(filter, post[0]):
                new_posts.append(post)
        new_posts_by_subreddit[sub] = new_posts
    return new_posts_by_subreddit

# uses system notify-send command to post notification on linux
def send_updates(posts_by_subreddit, username, account):
    current_time = time.mktime(datetime.datetime.utcnow().timetuple())
    subject_subreddits = ''
    total_content = ''
    debug_content = ''
    post_count = 0
    for subreddit, posts in posts_by_subreddit.items():
        if posts:
            subject_subreddits += '/r/{} '.format(subreddit)
            total_content += '#r/' + subreddit
            total_content += '\n---\n\n'
            for post in posts:
                post_count += 1
                seconds = int(current_time - (post[2] + 25200))
                total_content += "**[{}]({})** ^([{} seconds ago])\n\n".format(post[0], post[1], seconds)
                debug_content += "{} [{} seconds ago]\n{}\n\n".format(post[0], seconds, post[1])
    if total_content != '':
        if post_count > 1:
            subject = "{} New Posts from {}".format(post_count, subject_subreddits)
        else:
            subject = "New Post from " + subject_subreddits
        print("subject: " + subject)
        print("to: " + username)
        print("---")
        print(debug_content)
        reddit.send_pm(subject, total_content, username, account)

if __name__ == '__main__':
    account = reddit.connect()
    db = data.connect()
    most_recent_time = data.get_most_recent_time()
    interval = 30
    while True:
        reddit.update_users(db, account)
        global_sub_list = data.subreddits(db)
        subs = data.subreddits(db)
        user_list = data.users(db)
        if global_sub_list:
            try:
                posts_by_subreddit = reddit.fetch_posts(subs, account)
            except:
                print("Error fetching posts.")
            posts_by_subreddit_by_users = {}
            most_recent_time, posts_by_subreddit = get_new_posts(posts_by_subreddit, most_recent_time)
            for user in user_list:
                new_posts_by_subreddit = apply_filters(posts_by_subreddit, user[1], user[0], db)
                try:
                    posts_by_subreddit_by_users[user[0]] += new_posts_by_subreddit
                except:
                    posts_by_subreddit_by_users[user[0]] = new_posts_by_subreddit

            for username, posts in posts_by_subreddit_by_users.items():
                send_updates(posts, username, account)
        data.set_most_recent_time(most_recent_time)