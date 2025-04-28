# bert_model.py

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# 加载DistilBERT（预训练好的情感分析模型）
MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# 确认是否使用GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
model.eval()

# 标签映射（你可以后面根据自己的7分类进一步调整）
id2label = {
    0: "Negative",
    1: "Positive"
}

# 预测单条文本情感
def predict_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.softmax(logits, dim=1)
        pred_label = torch.argmax(probs, dim=1).item()
    
    return id2label.get(pred_label, "Unknown")
