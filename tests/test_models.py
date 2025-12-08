"""Tests for DJGramm models."""

import pytest
from django.db import IntegrityError
from django.utils import timezone

from app.models import Follow, Like, Post, PostImage, Profile, Tag, User


class TestUserModel:
    """Tests for User model."""

    def test_create_user(self, db):
        """Test creating a user."""
        user = User.objects.create_user(
            username="newuser",
            email="new@example.com",
            password="testpass123",
        )
        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.check_password("testpass123")
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_superuser(self, db):
        """Test creating a superuser."""
        admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass",
        )
        assert admin.is_staff
        assert admin.is_superuser

    def test_user_str(self, user):
        """Test user string representation."""
        assert str(user) == user.email

    def test_email_unique(self, user, db):
        """Test that email must be unique."""
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                username="another",
                email=user.email,  # Same email
                password="testpass",
            )

    def test_username_field_is_email(self, db):
        """Test that USERNAME_FIELD is email."""
        assert User.USERNAME_FIELD == "email"


class TestProfileModel:
    """Tests for Profile model."""

    def test_profile_created_on_user_creation(self, user):
        """Test that profile is auto-created when user is created."""
        assert hasattr(user, "profile")
        assert isinstance(user.profile, Profile)

    def test_profile_str(self, profile):
        """Test profile string representation."""
        assert str(profile) == f"Profile of {profile.user.username}"

    def test_profile_fields(self, profile):
        """Test profile fields."""
        assert profile.full_name == "Test User"
        assert profile.bio == "Test bio"


class TestTagModel:
    """Tests for Tag model."""

    def test_create_tag(self, db):
        """Test creating a tag."""
        tag = Tag.objects.create(name="Python", slug="python")
        assert tag.name == "Python"
        assert tag.slug == "python"

    def test_tag_str(self, tag):
        """Test tag string representation."""
        assert str(tag) == tag.name

    def test_tag_get_absolute_url(self, tag):
        """Test tag get_absolute_url."""
        assert tag.get_absolute_url() == f"/tag/{tag.slug}/"

    def test_tag_name_unique(self, tag, db):
        """Test that tag name must be unique."""
        with pytest.raises(IntegrityError):
            Tag.objects.create(name=tag.name, slug="different")

    def test_tag_slug_unique(self, tag, db):
        """Test that tag slug must be unique."""
        with pytest.raises(IntegrityError):
            Tag.objects.create(name="Different", slug=tag.slug)


class TestPostModel:
    """Tests for Post model."""

    def test_create_post(self, user, db):
        """Test creating a post."""
        post = Post.objects.create(author=user, caption="Hello world!")
        assert post.author == user
        assert post.caption == "Hello world!"
        assert post.created_at is not None

    def test_post_str(self, post):
        """Test post string representation."""
        assert str(post) == f"Post #{post.pk} by {post.author.username}"

    def test_post_get_absolute_url(self, post):
        """Test post get_absolute_url."""
        assert post.get_absolute_url() == f"/post/{post.pk}/"

    def test_post_ordering(self, user, db):
        """Test that posts are ordered by -created_at."""

        now = timezone.now()
        post1 = Post.objects.create(
            author=user,
            caption="First",
            created_at=now,  # fmt: skip
        )
        post2 = Post.objects.create(
            author=user,
            caption="Second",
            created_at=now + timezone.timedelta(seconds=1),
        )

        posts = list(Post.objects.all())
        assert posts[0] == post2  # Newer first
        assert posts[1] == post1

    def test_post_with_tags(self, post, tags):
        """Test adding tags to post."""
        post.tags.set(tags)
        assert post.tags.count() == 3

    def test_post_likes_count(self, post, user, user2):
        """Test counting post likes."""
        Like.objects.create(user=user, post=post)
        Like.objects.create(user=user2, post=post)
        assert post.likes.count() == 2


class TestPostImageModel:
    """Tests for PostImage model."""

    def test_post_image_str(self, post_with_image):
        """Test post image string representation."""
        image = post_with_image.images.first()
        assert str(image) == f"Image 0 for Post #{post_with_image.pk}"

    def test_post_image_ordering(self, post, db):
        """Test that images are ordered by order field."""
        from django.core.files.uploadedfile import SimpleUploadedFile

        img1 = PostImage.objects.create(
            post=post,
            image=SimpleUploadedFile("1.jpg", b"content", "image/jpeg"),
            order=1,
        )
        img0 = PostImage.objects.create(
            post=post,
            image=SimpleUploadedFile("0.jpg", b"content", "image/jpeg"),
            order=0,
        )

        images = list(post.images.all())
        assert images[0] == img0
        assert images[1] == img1


class TestLikeModel:
    """Tests for Like model."""

    def test_create_like(self, user, post, db):
        """Test creating a like."""
        like = Like.objects.create(user=user, post=post)
        assert like.user == user
        assert like.post == post

    def test_like_str(self, like):
        """Test like string representation."""
        assert str(like) == f"{like.user.username} likes Post #{like.post.pk}"

    def test_like_unique_together(self, like, db):
        """Test that user can only like a post once."""
        with pytest.raises(IntegrityError):
            Like.objects.create(user=like.user, post=like.post)

    def test_user_can_like_multiple_posts(self, user, db):
        """Test that user can like multiple different posts."""
        post1 = Post.objects.create(author=user, caption="Post 1")
        post2 = Post.objects.create(author=user, caption="Post 2")

        Like.objects.create(user=user, post=post1)
        Like.objects.create(user=user, post=post2)

        assert user.likes.count() == 2


class TestFollowModel:
    """Tests for Follow model."""

    def test_create_follow(self, user, user2, db):
        """Test creating a follow relationship."""
        follow = Follow.objects.create(follower=user, following=user2)
        assert follow.follower == user
        assert follow.following == user2
        assert follow.created_at is not None

    def test_follow_str(self, user, user2, db):
        """Test follow string representation."""
        follow = Follow.objects.create(follower=user, following=user2)
        assert str(follow) == f"{user.username} follows {user2.username}"

    def test_follow_unique_together(self, user, user2, db):
        """Test that user can only follow another user once."""
        Follow.objects.create(follower=user, following=user2)
        with pytest.raises(IntegrityError):
            Follow.objects.create(follower=user, following=user2)

    def test_user_can_follow_multiple_users(self, user, user2, db):
        """Test that user can follow multiple different users."""
        user3 = User.objects.create_user(
            username="user3",
            email="user3@example.com",
            password="testpass123",
        )
        Follow.objects.create(follower=user, following=user2)
        Follow.objects.create(follower=user, following=user3)
        assert user.following.count() == 2

    def test_follow_ordering(self, user, user2, db):
        """Test that follows are ordered by -created_at."""
        follow1 = Follow.objects.create(follower=user, following=user2)
        follow2 = Follow.objects.create(
            follower=user2, following=user
        )  # Reverse follow
        follows = list(Follow.objects.all())
        assert follows[0] == follow2  # Newer first
        assert follows[1] == follow1


class TestUserFollowMethods:
    """Tests for User follow helper methods."""

    def test_get_followers_count(self, user, user2, db):
        """Test get_followers_count method."""
        assert user.get_followers_count() == 0
        Follow.objects.create(follower=user2, following=user)
        assert user.get_followers_count() == 1

    def test_get_following_count(self, user, user2, db):
        """Test get_following_count method."""
        assert user.get_following_count() == 0
        Follow.objects.create(follower=user, following=user2)
        assert user.get_following_count() == 1

    def test_is_following_true(self, user, user2, db):
        """Test is_following returns True when following."""
        Follow.objects.create(follower=user, following=user2)
        assert user.is_following(user2) is True

    def test_is_following_false(self, user, user2, db):
        """Test is_following returns False when not following."""
        assert user.is_following(user2) is False

    def test_is_following_with_none(self, user):
        """Test is_following handles None gracefully."""
        assert user.is_following(None) is False

    def test_related_names_work(self, user, user2, db):
        """Test that related_name attributes work correctly."""
        Follow.objects.create(follower=user, following=user2)
        # user.following = Follow objects where user is follower
        assert user.following.filter(following=user2).exists()
        # user2.followers = Follow objects where user2 is being followed
        assert user2.followers.filter(follower=user).exists()
