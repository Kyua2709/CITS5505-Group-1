import requests


def fetch_reddit_comments(post_url, limit):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; SentiSocialBot/1.0)"}

    if not post_url.endswith(".json"):
        if post_url.endswith("/"):
            post_url = post_url[:-1]
        post_url += ".json"

    resp = requests.get(post_url, headers=headers)
    data = resp.json()
    comments = []

    for c in data[1]["data"]["children"]:
        if c["kind"] == "t1":
            body = c["data"].get("body")
            if body:
                comments.append(body)
            if len(comments) >= limit:
                break

    return comments
