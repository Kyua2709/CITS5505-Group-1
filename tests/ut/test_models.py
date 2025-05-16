import pytest
from datetime import datetime, timezone
from app.models import User, Upload, Comment
from app import create_app, db


@pytest.fixture(scope="module")
def app():
    test_config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    }
    app = create_app(test_config)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_user_password(app):
    """
    Test User Password Functionality:
    - Verifies password setting and hashing
    - Tests password verification with correct password
    - Tests password verification with incorrect password
    """
    with app.app_context():
        user = User(first_name="Test", last_name="User", email="test@example.com")
        user.set_password("password123")

        # Test correct password
        assert user.check_password("password123") == True

        # Test incorrect password
        assert user.check_password("wrongpassword") == False

        # Test if password hash is correctly generated
        assert user.password_hash is not None
        assert user.password_hash != "password123"


def test_comment_rating(app):
    """
    Test Comment Rating System:
    - Verifies initial rating assignment
    - Tests rating modification
    - Ensures rating values are correctly stored and retrieved
    """
    with app.app_context():
        # Test negative rating
        comment_negative = Comment(score=30)
        assert comment_negative.rating == -1

        # Test neutral rating
        comment_neutral = Comment(score=45)
        assert comment_neutral.rating == 0

        # Test positive rating
        comment_positive = Comment(score=60)
        assert comment_positive.rating == 1


def test_upload_to_dict(app):
    """
    Test Upload Data Serialization:
    - Verifies conversion of Upload model to dictionary
    - Tests all fields are correctly serialized
    - Ensures data integrity during serialization
    """
    with app.app_context():
        upload = Upload(
            id="test-id",
            title="Test Title",
            description="Test Description",
            platform="Test Platform",
            size=1000,
            status="Processing",
        )

        data = upload.to_dict()

        # Validate all fields
        assert data["id"] == "test-id"
        assert data["title"] == "Test Title"
        assert data["description"] == "Test Description"
        assert data["platform"] == "Test Platform"
        assert data["size"] == 1000
        assert data["status"] == "Processing"
        assert "timestamp" in data


def test_comment_to_dict(app):
    """
    Test Comment Data Serialization:
    - Verifies conversion of Comment model to dictionary
    - Tests content and rating serialization
    - Ensures timestamp is included in serialized data
    """
    with app.app_context():
        comment = Comment(content="Test Comment", score=50, created_at=datetime.now(timezone.utc))

        data = comment.to_dict()

        # Validate all fields
        assert data["content"] == "Test Comment"
        assert data["score"] == 50
        assert "rating" in data
        assert "created_at" in data
        assert data["rating"] == 0  # Score of 50 should return neutral rating


def test_user_uploads_relationship(app):
    """
    Test User-Upload Relationship:
    - Verifies one-to-many relationship between User and Upload
    - Tests adding uploads to user's collection
    - Ensures relationship integrity and data accessibility
    """
    with app.app_context():
        # Create test user
        user = User(first_name="Test", last_name="User", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        # Create test uploads
        upload1 = Upload(
            id="test-upload-1",
            title="Test Upload 1",
            description="Description 1",
            platform="Test Platform",
            user_id=user.id,
        )

        upload2 = Upload(
            id="test-upload-2",
            title="Test Upload 2",
            description="Description 2",
            platform="Test Platform",
            user_id=user.id,
        )

        db.session.add_all([upload1, upload2])
        db.session.commit()

        # Verify relationship
        assert len(user.uploads) == 2
        assert user.uploads[0].title == "Test Upload 1"
        assert user.uploads[1].title == "Test Upload 2"
        assert user.uploads[0].user_id == user.id
        assert user.uploads[1].user_id == user.id
