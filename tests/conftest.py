import os
import sys
import pytest
import warnings
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Mock the crawler module to avoid loading snscrape
sys.modules['packages.crawler'] = type('MockCrawler', (), {
    'fetch_twitter_comments': lambda *args, **kwargs: [],
    'fetch_facebook_comments': lambda *args, **kwargs: [],
    'fetch_tiktok_comments': lambda *args, **kwargs: []
})

from app import create_app, db

# 忽略Werkzeug的废弃警告
warnings.filterwarnings("ignore", category=DeprecationWarning, module="werkzeug")

@pytest.fixture
def app():
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-key'
    }
    app = create_app(test_config)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client() 