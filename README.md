# subreddit_notifications
Notifies you of new posts on a particular set of subreddits.

## Installation

You need python3 installed to run this program.

```
pip3 install toml requests
git clone https://github.com/kil0meters/subreddit_notifications
python3 main.py
```

## Configuration 

The file `config.toml` by default contains
```toml
[config]
# Interval in seconds (don't set this to less than 2 seconds)
interval = 30
# List of subreddits to monitor
subreddits = [
    "buildapcsales"
]
# Show posts only containing one of these tags
tags = [
    "GPU"
]
```
You can add additional subreddits or tags by editing their respective entries.
like so:
```toml
subreddits = [
    "subreddit1",
    "subreddit2",
    "subreddit3"
]
tag = [
    "tag1",
    "tag2",
    "tag3"
]
```