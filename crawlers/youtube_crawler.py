from googleapiclient.discovery import build
import re
import os

def fetch_youtube_comments(url, limit=100):
    # 需要先 pip install google-api-python-client
    API_KEY = os.getenv('YOUTUBE_API_KEY')
    if not API_KEY:
        raise ValueError('请在环境变量中设置YOUTUBE_API_KEY')
    video_id = None
    m = re.search(r'v=([A-Za-z0-9_-]+)', url)
    if m:
        video_id = m.group(1)
    else:
        m = re.search(r'youtu\.be/([A-Za-z0-9_-]+)', url)
        if m:
            video_id = m.group(1)
    if not video_id:
        return []
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    comments = []
    nextPageToken = None
    while len(comments) < limit:
        request = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=min(100, limit-len(comments)),
            pageToken=nextPageToken
        )
        response = request.execute()
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)
            if len(comments) >= limit:
                break
        nextPageToken = response.get('nextPageToken')
        if not nextPageToken:
            break
    return comments 