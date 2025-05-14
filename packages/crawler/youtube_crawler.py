from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import re
import time

def fetch_youtube_comments(url, limit):
    video_id = None
    if 'youtube.com' in url:
        match = re.search(r'v=([A-Za-z0-9_-]+)', url)
        if match:
            video_id = match.group(1)
    elif 'youtu.be' in url:
        match = re.search(r'youtu\.be/([A-Za-z0-9_-]+)', url)
        if match:
            video_id = match.group(1)

    if not video_id:
        return ValueError("URL does not contain video ID")

    try:
        print(f"Fetching comments for video ID: {video_id}")
        comments = []

        # 设置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 无头模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

        # 初始化浏览器
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)

        try:
            # 访问视频页面
            video_url = f'https://www.youtube.com/watch?v={video_id}'
            driver.get(video_url)
            time.sleep(3)  # 等待页面加载

            # 等待评论区域加载
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ytd-comments')))

            # 滚动到评论区域
            comments_section = driver.find_element(By.CSS_SELECTOR, 'ytd-comments')
            driver.execute_script("arguments[0].scrollIntoView();", comments_section)
            time.sleep(2)  # 等待评论加载

            last_height = driver.execute_script("return document.documentElement.scrollHeight")

            while len(comments) < limit:
                # 查找所有评论
                comment_elements = driver.find_elements(By.CSS_SELECTOR, 'ytd-comment-thread-renderer')

                # 提取评论内容
                for element in comment_elements:
                    try:
                        # 获取评论文本
                        text_element = element.find_element(By.CSS_SELECTOR, '#content-text')
                        if text_element:
                            comment_text = text_element.text
                            if comment_text and comment_text not in comments:
                                comments.append(comment_text)
                                print(f"Found comment {len(comments)}: {comment_text[:50]}...")
                                if len(comments) >= limit:
                                    break
                    except Exception as e:
                        print(f"Error extracting comment: {e}")
                        continue

                # 滚动到页面底部
                driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                time.sleep(2)  # 等待新内容加载

                # 检查是否到达页面底部
                new_height = driver.execute_script("return document.documentElement.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            print(f"Found {len(comments)} YouTube comments")
            return comments

        finally:
            driver.quit()

    except Exception as e:
        raise
