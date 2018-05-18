#!/usr/bin/python3
import datetime
import os
import re
import subprocess
import time
import xml.etree.ElementTree as ET
import requests
import toml

# loads and parses config_file
def load_config_file(config_file):
    file = open(config_file, "r")
    toml_string = file.read()
    return toml.loads(toml_string)

# fetches content on https://reddit.com/r/SUBREDDIT/new
def fetch_posts(subreddits):
    posts = []
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

                subreddit_posts.append([title, link, post_time])
        posts.append(subreddit_posts)
        time.sleep(2)
    return posts

# only shows posts that are new
def get_new_posts(posts, most_recent_time):
    new_posts = []
    times = []
    for subreddit in posts:
        for post in subreddit:
            if post[2] < most_recent_time:
                break
            times.append(post[2])
            new_posts.append([post[0], post[1], post[2]])
    if new_posts:
        most_recent_time = max(times) + 1
    return most_recent_time, new_posts

# only shows posts that match certain filters
def filter_tags(posts, tags):
    # # '\\x1B[0;31;1m\1\\x1B[0m'
    new_posts = []
    for post in posts:
        text = re.sub(tags, r'\x1b[0;31;1;3m\1\x1b[0m', post[0])
        post.append(text)
        if text != post[0]:
            new_posts.append(post)
    return new_posts

# uses system notify-send command to post notification on linux
def post_notification(post, current_time):
    how_long_ago = int(current_time - post[2])
    hours = how_long_ago // 3600
    how_long_ago = how_long_ago - (hours * 3600)
    minutes = how_long_ago // 60
    seconds = how_long_ago - (minutes * 60)
    title = "{} [{} hours {} minutes {} seconds ago]\n".format(post[0], hours, minutes, seconds)
    if os.name == 'posix':
        # FIXME: For some reason ANSI escape codes don't work with built in python functions
        subprocess.Popen(['echo', '-e', "{} [{} hours {} minutes {} seconds ago]\n{}\n"\
            .format(post[3], hours, minutes, seconds, post[1])])
        subprocess.Popen(['notify-send', title, post[1]])
    else:
        print("{}\n{}\n\n", title, post[1])


def print_posts(posts):
    current_time = time.mktime(datetime.datetime.utcnow().timetuple())
    for post in posts:
        post_notification(post, current_time)
        time.sleep(1)

def main():
    config = load_config_file("config.toml")
    interval = config['config']['interval']
    subreddits = config['config']['subreddits']
    tag_array = config['config']['tags']
    tags = '|'.join(tag_array)
    tags = '(' + tags + ')'
    most_recent_time = 0
    while True:
        posts = fetch_posts(subreddits)
        most_recent_time, posts = get_new_posts(posts, most_recent_time)
        if tags:
            posts = filter_tags(posts, tags)
        if posts:
            print_posts(posts)
        time.sleep(interval)

main()
