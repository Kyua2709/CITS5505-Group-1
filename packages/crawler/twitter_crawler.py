import snscrape.modules.twitter as sntwitter
import re
import time

def fetch_twitter_comments(tweet_url, limit=100):
    """
    爬取Twitter帖子下的评论
    :param tweet_url: Twitter帖子链接
    :param limit: 评论数量上限
    :return: 评论内容列表
    """
    # 从URL中提取tweet ID
    tweet_id = None
    if 'twitter.com' in tweet_url or 'x.com' in tweet_url:
        match = re.search(r'/status/(\d+)', tweet_url)
        if match:
            tweet_id = match.group(1)
    
    if not tweet_id:
        print("Invalid Twitter URL")
        return []
    
    try:
        print(f"Fetching comments for tweet ID: {tweet_id}")
        comments = []
        
        # 使用snscrape获取评论
        query = f"conversation_id:{tweet_id}"
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
            if i >= limit:
                break
            if tweet.id != int(tweet_id):  # 跳过原始推文
                comments.append(tweet.rawContent)
                print(f"Found comment {i+1}: {tweet.rawContent[:50]}...")
        
        print(f"Found {len(comments)} Twitter comments")
        return comments
        
    except Exception as e:
        print(f"Error fetching comments: {e}")
        return []

if __name__ == "__main__":
    url = input("请输入Twitter帖子URL: ").strip()
    limit = int(input("请输入评论数量上限（如50/100/200/500/1000）: ").strip())
    comments = fetch_twitter_comments(url, limit)
    print(f"共抓取到{len(comments)}条评论：")
    for i, c in enumerate(comments, 1):
        print(f"{i}: {c}\n") 