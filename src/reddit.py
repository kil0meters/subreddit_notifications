import praw
import json
import data
from secrets import *

def connect():
    account = praw.Reddit(user_agent="Subreddit Notification Bot (0.1)",
                         client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                         username=USERNAME, password=PASSWORD)
    return account

def update_users(db, account):
    for message in account.inbox.unread():
        if message.subject == 'update settings':
            try:
                config = json.loads(message.body)
                config['username'] = message.author.name
                print(config)
                data.update_user(config, db)
                print(config)
                message.mark_read()
            except:
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