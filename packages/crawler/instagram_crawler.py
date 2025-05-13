import instaloader
import re

def fetch_instagram_comments(url, limit=100):
    # 需要 pip install instaloader
    L = instaloader.Instaloader()
    # L.login('your_username', 'your_password')  # 可选，部分内容需登录
    m = re.search(r'/p/([A-Za-z0-9_-]+)/', url)
    if not m:
        return []
    shortcode = m.group(1)
    comments = []
    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        for comment in post.get_comments():
            comments.append(comment.text)
            if len(comments) >= limit:
                break
    except Exception as e:
        print('Error:', e)
    return comments 