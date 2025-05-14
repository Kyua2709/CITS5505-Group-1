from TikTokApi import TikTokApi
import re

def fetch_tiktok_comments(url, limit):
    m = re.search(r'/video/(\d+)', url)
    if not m:
        raise ValueError("URL does not contain video ID")

    video_id = m.group(1)
    comments = []

    with TikTokApi() as api:
        for comment in api.video(id=video_id).comments(count=limit):
            comments.append(comment.text)
            if len(comments) >= limit:
                break

    return comments