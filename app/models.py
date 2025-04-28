# app/models.py

from bert_model import predict_sentiment
from preprocessing import clean_text

def predict_single_text(text):
    """清理并预测单条文本"""
    cleaned = clean_text(text)
    prediction = predict_sentiment(cleaned)
    return prediction

def predict_batch_text(text_list):
    """批量清理并预测多条文本"""
    results = []
    for text in text_list:
        cleaned = clean_text(text)
        pred = predict_sentiment(cleaned)
        results.append((text, pred))
    return results
