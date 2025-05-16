from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import re
import time

def fetch_youtube_comments(url, limit):
    # Extract video ID from YouTube URL
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
        raise ValueError("URL does not contain video ID")
    
    try:
        print(f"Fetching comments for video ID: {video_id}")
        comments = set()
        
        # Set Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # Initialize browser
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 15)
        
        try:
            # Navigate to video page
            video_url = f'https://www.youtube.com/watch?v={video_id}'
            driver.get(video_url)
            time.sleep(5)  # Allow full page to load
            
            # Wait for comments section
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ytd-comments')))
            driver.execute_script("window.scrollTo(0, 500);")  # Initial scroll to activate comments
            time.sleep(3)

            last_count = 0
            attempts = 0

            while len(comments) < limit and attempts < 20:
                # Scroll to load more comments
                driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                time.sleep(3)

                # Extract all visible comments
                comment_elements = driver.find_elements(By.CSS_SELECTOR, 'ytd-comment-thread-renderer #content-text')

                for element in comment_elements:
                    comment_text = element.text.strip()
                    if comment_text:
                        comments.add(comment_text)
                    if len(comments) >= limit:
                        break

                # Check if we are stuck
                if len(comments) == last_count:
                    attempts += 1
                else:
                    attempts = 0  # Reset if new comments were found
                    last_count = len(comments)

            final_comments = list(comments)[:limit]
            print(f"✅ Fetched {len(final_comments)} comments.")
            return final_comments

        finally:
            driver.quit()

    except Exception as e:
        print(f"❌ Error fetching comments: {e}")
        raise
