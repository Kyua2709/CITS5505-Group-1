from facebook_scraper import get_posts
import re


def fetch_facebook_comments(url, limit):
    m = re.search(r"/posts/(pfbid\w+|\d+)", url)
    if not m:
        raise ValueError("URL does not contain post ID")

    post_id = m.group(1)
    comments = []

    for post in get_posts(post_urls=[url], options={"comments": True}):
        for comment in post.get("comments_full", []):
            comments.append(comment["comment_text"])
            if len(comments) >= limit:
                break
        if len(comments) >= limit:
            break

    return comments
