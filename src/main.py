#!/usr/bin/python3
import datetime
import re
import time
import data
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
    for subreddit, posts in posts_by_subreddit.items():
        if posts:
            total_content += '#r/' + subreddit.display_name
            total_content += '\n---\n\n'
            for post in posts:
                how_long_ago = int(current_time - (post[2] + 25200))
                hours = how_long_ago // 3600
                how_long_ago = how_long_ago - (hours * 3600)
                minutes = how_long_ago // 60
                seconds = how_long_ago - (minutes * 60)
                total_content += "**[{}]({})** ^([{} hours {} minutes {} seconds ago])\n\n".format(post[0], post[1], hours, minutes, seconds)
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
            posts_by_subreddit = reddit.fetch_posts(subreddits, account)
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
