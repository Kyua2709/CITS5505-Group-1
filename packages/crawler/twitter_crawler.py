import snscrape.modules.twitter as sntwitter
import re

def fetch_twitter_comments(url, limit=100):
    # 需要 pip install snscrape
    m = re.search(r'status/(\d+)', url)
    if not m:
        return []
    tweet_id = m.group(1)
    comments = []
    for i, reply in enumerate(sntwitter.TwitterTweetScraper(tweet_id).get_items()):
        if hasattr(reply, 'content'):
            comments.append(reply.content)
        if len(comments) >= limit:
            break
    return comments 