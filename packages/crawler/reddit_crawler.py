import requests
from bs4 import BeautifulSoup
import re

def fetch_reddit_comments(post_url, limit=100):
    """
    爬取Reddit帖子下最新的评论
    :param post_url: Reddit帖子链接
    :param limit: 评论数量上限
    :return: 评论内容列表
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; SentiSocialBot/1.0)"
    }
    # Reddit新页面结构，.json结尾可直接拿到结构化数据
    if not post_url.endswith('.json'):
        if post_url.endswith('/'):
            post_url = post_url[:-1]
        post_url += '.json'
    resp = requests.get(post_url, headers=headers)
    if resp.status_code != 200:
        print(f"Failed to fetch: {resp.status_code}")
        return []
    data = resp.json()
    comments = []
    # 评论在第二个元素的data->children
    try:
        for c in data[1]['data']['children']:
            if c['kind'] == 't1':  # t1是评论
                body = c['data'].get('body')
                if body:
                    comments.append(body)
                if len(comments) >= limit:
                    break
    except Exception as e:
        print("Parse error:", e)
    return comments

if __name__ == "__main__":
    url = input("请输入Reddit帖子URL: ").strip()
    limit = int(input("请输入评论数量上限（如50/100/200/500/1000）: ").strip())
    comments = fetch_reddit_comments(url, limit)
    print(f"共抓取到{len(comments)}条评论：")
    for i, c in enumerate(comments, 1):
        print(f"{i}: {c}\n") 