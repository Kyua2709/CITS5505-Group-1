"""
Mock packages for testing

This module provides mock implementations of the packages used in the application
to avoid dependencies on external services during testing.
"""

class MockTwitterCrawler:
    @staticmethod
    def fetch_twitter_comments(query, limit=100):
        """Mock implementation of fetch_twitter_comments"""
        return [
            {"date": "2023-01-01", "content": "This is a great product!", "username": "user1", "sentiment": "positive"},
            {"date": "2023-01-02", "content": "I love this service.", "username": "user2", "sentiment": "positive"},
            {"date": "2023-01-03", "content": "Not very satisfied with the quality.", "username": "user3", "sentiment": "negative"},
        ]

# Create a mock crawler module
class MockCrawler:
    twitter_crawler = MockTwitterCrawler()
    
    @staticmethod
    def fetch_twitter_comments(*args, **kwargs):
        return MockTwitterCrawler.fetch_twitter_comments(*args, **kwargs)

# Create a mock bert_model module
class MockBertModel:
    @staticmethod
    def predict(texts):
        """Mock implementation of predict"""
        results = []
        for text in texts:
            if "great" in text.lower() or "love" in text.lower():
                results.append("positive")
            elif "not" in text.lower() or "bad" in text.lower():
                results.append("negative")
            else:
                results.append("neutral")
        return results
