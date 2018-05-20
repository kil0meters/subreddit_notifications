import praw
import json
import data
import time
from secrets import *

def connect():
    account = praw.Reddit(user_agent="Subreddit Notification Bot (0.1)",
                         client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                         username=USERNAME, password=PASSWORD)
    return account

# fetches content on https://reddit.com/r/SUBREDDIT/new
def fetch_posts(subreddits, account):
    posts_by_subreddit = {}
    for subreddit_name in subreddits:
        subreddit_posts = []
        subreddit = account.subreddit(subreddit_name)
        new = subreddit.new(limit=(5))
        for submission in new:
            title = submission.title
            link = 'https://reddit.com' + submission.permalink
            post_time = submission.created_utc

            subreddit_posts.append([title, link, post_time, subreddit_name])
        posts_by_subreddit[subreddit] = subreddit_posts
        time.sleep(2)
    return posts_by_subreddit

def update_users(db, account):
    for message in account.inbox.unread():
        if message.subject == 'update settings':
            try:
                config = json.loads(message.body)
                config['username'] = message.author.name
                print("Updating user..")
                data.update_user(config, db)
                print(config)
                message.mark_read()
            except:
                print("An error occured: Invalid Configuration")
                message.reply("An error occured: Invalid Configuration")
                message.mark_read()
        else:
            message.mark_read()


def send_pm(subject, body, user, account):
    redditor = account.redditor(user)
    redditor.message(subject, body)
    print(subject)
    print("to: " + user)
    print('---')
    print(body)