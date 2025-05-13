from facebook_scraper import get_posts
import re

def fetch_facebook_comments(url, limit=100):
    # 需要 pip install facebook-scraper
    m = re.search(r'posts/(\d+)', url)
    if not m:
        return []
    post_id = m.group(1)
    comments = []
    try:
        for post in get_posts(post_urls=[url], options={"comments": True}):
            for comment in post.get('comments_full', []):
                comments.append(comment['comment_text'])
                if len(comments) >= limit:
                    break
            if len(comments) >= limit:
                break
    except Exception as e:
        print('Error:', e)
    return comments 