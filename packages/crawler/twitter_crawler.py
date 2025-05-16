import snscrape.modules.twitter as sntwitter
import re
import time

def fetch_twitter_comments(tweet_url, limit):
    tweet_id = None
    if 'twitter.com' in tweet_url or 'x.com' in tweet_url:
        match = re.search(r'/status/(\d+)', tweet_url)
        if match:
            tweet_id = match.group(1)

    if not tweet_id:
        raise ValueError("URL does not contain post ID")

    print(f"Fetching comments for tweet ID: {tweet_id}")
    comments = []

    query = f"conversation_id:{tweet_id}"
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
        if i >= limit:
            break
        if tweet.id != int(tweet_id):
            comments.append(tweet.rawContent)
            print(f"Found comment {i+1}: {tweet.rawContent[:50]}...")

    print(f"Found {len(comments)} Twitter comments")
    return comments
