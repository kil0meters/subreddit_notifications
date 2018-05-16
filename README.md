# subreddit_notifications
Notifies you of new posts on a particular set of subreddits.

## Installation

You need python3 installed to run this program.

```
pip3 install toml requests notify2
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
```
You can add additional subreddits to the list by editing the `subreddits` entry
like so:
```toml
subreddits = [
    "subreddit1",
    "subreddit2",
    "subreddit3"
]
```