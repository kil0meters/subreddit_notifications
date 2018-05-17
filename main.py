import toml, time, requests, notify2, os
import xml.etree.ElementTree as ET

# loads and parses config_file
def loadConfigFile(config_file):
    f = open(config_file, "r")
    toml_string = f.read()
    return toml.loads(toml_string)

# fetches content on https://reddit.com/r/SUBREDDIT/new
def fetchPosts(subreddits):
    posts = []
    for subreddit in subreddits:
        subredditPosts = []
        url = "http://reddit.com/r/{}/new/.rss".format(subreddit)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.109 Safari/537.36'
        }
        r = requests.get(url, headers=headers)
        #print(r.text)
        #print(subreddit)
        tree = ET.fromstring(r.text)
        for child in tree:
            if child.tag == "{http://www.w3.org/2005/Atom}entry":
                title = child[-1].text

                link = child[-3].attrib['href']

                postTimeString = child[-2].text
                if postTimeString.endswith("+00:00"):
                    postTimeString = postTimeString[:-6]
                postTime = time.mktime(time.strptime(postTimeString, '%Y-%m-%dT%H:%M:%S'))

                subredditPosts.append([title, link, postTime])
        posts.append(subredditPosts)
        time.sleep(2)
    return posts

def getNewPosts(posts, mostRecentTime):
    newPosts = []
    times = []
    for subreddit in posts:
        for post in subreddit:
            if post[2] < mostRecentTime:
                break
            times.append(post[2])
            newPosts.append([post[0], post[1]])
    mostRecentTime = max(times)
    return mostRecentTime, newPosts

def filterTags(posts, tags):
    newPosts = []
    for post in posts:
        for tag in tags:
            if tag in post[0]:
                newPosts.append(post)
                break
    return newPosts

def printPosts(posts):
    string = ''
    for post in posts:
        string += "TITLE: {}\n".format(post[0])
        string += "LINK: {}\n\n".format(post[1])
    print(string)
    if os.name == 'posix':
        n = notify2.Notification("NEW POSTS", string, "notification-message-im")
        n.show()

def main():
    if os.name == 'posix':
        notify2.init("Reddit Notifier")

    config = loadConfigFile("config.toml")
    interval = config['config']['interval']
    subreddits = config['config']['subreddits']
    tags = config['config']['tags']
    mostRecentTime = 0
    while True:
        posts = fetchPosts(subreddits)
        mostRecentTime, posts = getNewPosts(posts, mostRecentTime)
        if len(tags) > 0:
            posts = filterTags(posts, tags)
        if len(posts) > 0:
            printPosts(posts)
        time.sleep(interval)

main()