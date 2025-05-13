from TikTokApi import TikTokApi
import re

def fetch_tiktok_comments(url, limit=100):
    # 需要 pip install TikTokApi
    m = re.search(r'/video/(\d+)', url)
    if not m:
        return []
    video_id = m.group(1)
    comments = []
    try:
        with TikTokApi() as api:
            for comment in api.video(id=video_id).comments(count=limit):
                comments.append(comment.text)
                if len(comments) >= limit:
                    break
    except Exception as e:
        print('Error:', e)
    return comments 