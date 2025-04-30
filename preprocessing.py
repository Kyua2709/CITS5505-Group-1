# preprocessing.py

import re

def clean_text(text):
    # 小写化
    text = text.lower()
    # 移除URL
    text = re.sub(r"http\S+|www.\S+", "", text)
    # 移除提及@用户
    text = re.sub(r"@\w+", "", text)
    # 移除话题#
    text = re.sub(r"#\w+", "", text)
    # 移除非字母字符
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    # 移除多余空格
    text = re.sub(r"\s+", " ", text).strip()
    return text
