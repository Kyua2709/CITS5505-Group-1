import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Import custom utility classes and functions
from .model_cache import cache_directory

# Define the name of the pre-trained sentiment analysis model and cache directory
MODEL_NAME = "tabularisai/robust-sentiment-analysis"
CACHE_DIR = cache_directory

# Load the tokenizer and model using the specified model name and cache directory
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)

# Define function to predict sentiment from a given text string
def predict_sentiment(text: str) -> int:
    # Tokenize the input text, prepare it for the model
    input = tokenizer(
        text.lower(),
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=512,
    )

    # Run the model in inference mode (no gradient computation)
    with torch.no_grad():
        output = model(**input)
        logits = output.logits

    # Normalize the output to a score between [0, 100]
    # TODO: This is a hacky workaround to allow us display sentiment scores.
    # We may need to find a better way to do this
    probs = torch.softmax(logits, dim=-1).flatten()
    weight = torch.tensor([0.0, 0.25, 0.5, 0.75, 1.0], dtype=torch.float32)
    score = torch.dot(probs, weight).item()
    return round(score * 100)
