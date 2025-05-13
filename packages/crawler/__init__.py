from .facebook_crawler import fetch_facebook_comments
from .instagram_crawler import fetch_instagram_comments
from .reddit_crawler import fetch_reddit_comments
from .tiktok_crawler import fetch_tiktok_comments
from .twitter_crawler import fetch_twitter_comments
from .youtube_crawler import fetch_youtube_comments

# Mapping of supported platform hostnames to their corresponding fetch functions
HANDLER = {
    'Facebook': fetch_facebook_comments,
    'Instagram': fetch_instagram_comments,
    'Reddit': fetch_reddit_comments,
    'Tiktok': fetch_tiktok_comments,
    'Twitter': fetch_twitter_comments,
    'Youtube': fetch_youtube_comments,
}

def fetch_comments(platform: str, url: str, limit: int):
    fetch_func = HANDLER.get(platform)

    if not fetch_func:
        raise ValueError(f"Unsupported or unrecognized platform: {platform}")

    return fetch_func(url, limit)
