"""Pytest fixtures for DJGramm tests."""

from unittest.mock import patch

import pytest
from django.test import Client

from app.models import Like, Post, PostImage, Tag, User


@pytest.fixture
def user(db):
    """Create a regular user."""
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )
    return user


@pytest.fixture
def user2(db):
    """Create a second user for testing interactions."""
    user = User.objects.create_user(
        username="testuser2",
        email="test2@example.com",
        password="testpass123",
    )
    return user


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    user = User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123",
    )
    return user


@pytest.fixture
def client():
    """Return Django test client."""
    return Client()


@pytest.fixture
def authenticated_client(client, user):
    """Return authenticated Django test client."""
    client.login(email="test@example.com", password="testpass123")
    return client


@pytest.fixture
def tag(db):
    """Create a tag."""
    return Tag.objects.create(name="testtag", slug="testtag")


@pytest.fixture
def tags(db):
    """Create multiple tags."""
    return [
        Tag.objects.create(name=f"tag{i}", slug=f"tag{i}") for i in range(3)
    ]


@pytest.fixture
def post(db, user):
    """Create a post."""
    return Post.objects.create(
        author=user,
        caption="Test post caption",
    )


@pytest.fixture
def mock_cloudinary_upload():
    """Mock Cloudinary upload to prevent actual API calls in tests."""
    with patch("cloudinary.uploader.upload_resource") as mock_upload:
        # Return a mock response that CloudinaryField expects
        mock_upload.return_value = {
            "public_id": "test/test_image",
            "version": 1,
            "url": "https://res.cloudinary.com/test/image/upload/v1/test/test_image.jpg",
            "secure_url": "https://res.cloudinary.com/test/image/upload/v1/test/test_image.jpg",
        }
        yield mock_upload


@pytest.fixture
def post_with_image(db, user, tmp_path, mock_cloudinary_upload):
    """Create a post with an image."""
    from io import BytesIO

    from django.core.files.uploadedfile import SimpleUploadedFile
    from PIL import Image

    # Create post
    post = Post.objects.create(
        author=user,
        caption="Post with image",
    )

    # Create image
    img = Image.new("RGB", (100, 100), color="red")
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)

    image_file = SimpleUploadedFile(
        name="test.jpg",
        content=buffer.getvalue(),
        content_type="image/jpeg",
    )

    PostImage.objects.create(post=post, image=image_file, order=0)

    return post


@pytest.fixture
def like(db, user, post):
    """Create a like."""
    return Like.objects.create(user=user, post=post)


@pytest.fixture
def profile(db, user):
    """Return user's profile (auto-created by signal)."""
    user.profile.full_name = "Test User"
    user.profile.bio = "Test bio"
    user.profile.save()
    return user.profile
