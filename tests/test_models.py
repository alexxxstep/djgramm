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

    def test_profile_avatar_field_type(self, profile):
        """Test that Profile.avatar is CloudinaryField."""
        from cloudinary.models import CloudinaryField

        field = Profile._meta.get_field("avatar")
        assert isinstance(field, CloudinaryField)
        # Note: folder parameter is passed but not stored as attribute
        assert field.blank is True


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

    def test_post_image_field_type(self, db):
        """Test that PostImage.image is CloudinaryField."""
        from cloudinary.models import CloudinaryField

        field = PostImage._meta.get_field("image")
        assert isinstance(field, CloudinaryField)
        # Note: folder parameter is passed but not stored as attribute
        assert field.blank is False

    def test_post_image_ordering(self, post, db, mock_cloudinary_upload):
        """Test that images are ordered by order field."""
        from io import BytesIO

        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image

        # Create test images
        img1_data = BytesIO()
        img1_pil = Image.new("RGB", (100, 100), color="red")
        img1_pil.save(img1_data, format="JPEG")
        img1_data.seek(0)

        img0_data = BytesIO()
        img0_pil = Image.new("RGB", (100, 100), color="blue")
        img0_pil.save(img0_data, format="JPEG")
        img0_data.seek(0)

        img1 = PostImage.objects.create(
            post=post,
            image=SimpleUploadedFile(
                "1.jpg", img1_data.getvalue(), content_type="image/jpeg"
            ),
            order=1,
        )
        img0 = PostImage.objects.create(
            post=post,
            image=SimpleUploadedFile(
                "0.jpg", img0_data.getvalue(), content_type="image/jpeg"
            ),
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
        # user.following = User objects (ManyToManyField)
        assert user.following.contains(user2)
        # user.following_set = Follow objects where user is follower
        assert user.following_set.filter(following=user2).exists()
        # user2.followers = User objects (ManyToManyField reverse)
        assert user2.followers.contains(user)
        # user2.followers_set = Follow objects where user2 is being followed
        assert user2.followers_set.filter(follower=user).exists()

    def test_follow_method(self, user, user2, db):
        """Test follow method creates Follow relationship."""
        follow, created = user.follow(user2)
        assert created is True
        assert isinstance(follow, Follow)
        assert follow.follower == user
        assert follow.following == user2
        assert user.is_following(user2) is True

    def test_follow_method_idempotent(self, user, user2, db):
        """Test that follow method is idempotent (no duplicates)."""
        follow1, created1 = user.follow(user2)
        assert created1 is True
        follow2, created2 = user.follow(user2)
        assert created2 is False
        assert follow1 == follow2
        assert user.following.count() == 1

    def test_follow_method_prevents_self_follow(self, user, db):
        """Test that user cannot follow themselves."""
        follow, created = user.follow(user)
        assert created is False
        assert follow is None
        assert user.following.count() == 0

    def test_follow_method_with_invalid_user(self, user, db):
        """Test follow method handles invalid user gracefully."""
        follow, created = user.follow(None)
        assert created is False
        assert follow is None

    def test_unfollow_method(self, user, user2, db):
        """Test unfollow method removes Follow relationship."""
        Follow.objects.create(follower=user, following=user2)
        assert user.is_following(user2) is True

        result = user.unfollow(user2)
        assert result is True
        assert user.is_following(user2) is False
        assert user.following.count() == 0

    def test_unfollow_method_when_not_following(self, user, user2, db):
        """Test unfollow method when not following returns False."""
        assert user.is_following(user2) is False
        result = user.unfollow(user2)
        assert result is False

    def test_unfollow_method_with_invalid_user(self, user, db):
        """Test unfollow method handles invalid user gracefully."""
        result = user.unfollow(None)
        assert result is False


class TestUserUnreadNewsCount:
    """Tests for get_unread_news_count method."""

    def test_unread_count_when_never_visited(self, user, user2, db):
        """Test unread count when never visited news feed."""
        # user follows user2
        user.following.add(user2)
        # user2 creates a post
        Post.objects.create(author=user2, caption="New post")
        # Should count all posts from followed users
        assert user.get_unread_news_count() == 1

    def test_unread_count_excludes_own_posts(self, user, user2, db):
        """Test that own posts are not counted."""
        user.following.add(user2)
        # user creates own post
        Post.objects.create(author=user, caption="My post")
        # user2 creates a post
        Post.objects.create(author=user2, caption="Followed post")
        # Should only count user2's post (not own)
        assert user.get_unread_news_count() == 1

    def test_unread_count_after_visit(self, user, user2, db):
        """Test unread count after visiting news feed."""
        from datetime import timedelta

        user.following.add(user2)
        # Use fixed time points to avoid timing issues
        now = timezone.now()
        visit_time = now - timedelta(days=1)
        old_post_time = now - timedelta(days=2)

        # Create post before visit
        # Note: auto_now_add=True ignores created_at in create(),
        # so we use update() after creation
        old_post = Post.objects.create(author=user2, caption="Old post")
        Post.objects.filter(pk=old_post.pk).update(created_at=old_post_time)

        # Set last visit
        user.profile.last_news_feed_visit = visit_time
        user.profile.save()

        # Create post after visit
        new_post = Post.objects.create(author=user2, caption="New post")
        Post.objects.filter(pk=new_post.pk).update(created_at=now)

        # Refresh from DB to get updated created_at
        old_post.refresh_from_db()
        new_post.refresh_from_db()

        # Refresh user profile to ensure last_news_feed_visit is loaded
        user.profile.refresh_from_db()

        # Verify timestamps are correct
        assert old_post.created_at < user.profile.last_news_feed_visit
        assert new_post.created_at > user.profile.last_news_feed_visit

        # Should only count new post
        count = user.get_unread_news_count()
        error_msg = (
            f"Expected 1, got {count}. "
            f"Old post: {old_post.created_at}, "
            f"New post: {new_post.created_at}, "
            f"Visit: {user.profile.last_news_feed_visit}"
        )
        assert count == 1, error_msg

    def test_unread_count_zero_when_no_following(self, user, db):
        """Test unread count is 0 when not following anyone."""
        assert user.get_unread_news_count() == 0

    def test_unread_count_multiple_followed_users(self, user, user2, db):
        """Test unread count with multiple followed users."""
        user3 = User.objects.create_user(
            username="user3",
            email="user3@example.com",
            password="testpass123",
        )
        user.following.add(user2, user3)
        # Create posts from both followed users
        Post.objects.create(author=user2, caption="Post from user2")
        Post.objects.create(author=user3, caption="Post from user3")
        # Should count both
        assert user.get_unread_news_count() == 2


class TestUserDeletion:
    """Tests for User deletion with proper cleanup."""

    def test_delete_user_with_follow_relationships(self, user, user2, db):
        """Test deleting user with Follow relationships."""
        # Create Follow relationships
        user.following.add(user2)  # user follows user2

        user3 = User.objects.create_user(
            username="user3",
            email="user3@example.com",
            password="testpass123",
        )
        user3.following.add(user)  # user3 follows user

        # Verify relationships exist
        assert user.following.count() == 1
        assert user.followers.count() == 1
        assert Follow.objects.filter(follower=user).count() == 1
        assert Follow.objects.filter(following=user).count() == 1

        user_id = user.pk

        # Delete user
        user.delete()

        # Verify user is deleted
        assert not User.objects.filter(pk=user_id).exists()

        # Verify Follow relationships are cleaned up
        assert Follow.objects.filter(follower_id=user_id).count() == 0
        assert Follow.objects.filter(following_id=user_id).count() == 0

        # Verify other users still exist
        assert User.objects.filter(pk=user2.pk).exists()
        assert User.objects.filter(pk=user3.pk).exists()

    def test_delete_user_with_posts_and_likes(self, user, user2, post, db):
        """Test deleting user cascades to posts and likes."""
        # user2 likes user's post
        Like.objects.create(user=user2, post=post)

        # Create post by user2 that user likes
        post2 = Post.objects.create(author=user2, caption="User2 post")
        Like.objects.create(user=user, post=post2)

        user_id = user.pk
        post_id = post.pk

        # Delete user
        user.delete()

        # Verify user and their posts are deleted (CASCADE)
        assert not User.objects.filter(pk=user_id).exists()
        assert not Post.objects.filter(pk=post_id).exists()

        # Verify likes by deleted user are removed
        assert not Like.objects.filter(user_id=user_id).exists()

        # Verify user2's post still exists (only likes removed)
        assert Post.objects.filter(pk=post2.pk).exists()
        assert post2.likes.count() == 0  # user's like removed

    def test_delete_user_with_comments(self, user, user2, post, db):
        """Test deleting user cascades to their comments."""
        from app.models import Comment

        # user comments on user2's post
        post2 = Post.objects.create(author=user2, caption="User2 post")
        comment = Comment.objects.create(
            author=user,
            post=post2,
            text="Nice post!",
        )

        comment_id = comment.pk

        # Delete user
        user.delete()

        # Verify comment is deleted (CASCADE)
        assert not Comment.objects.filter(pk=comment_id).exists()

        # Verify user2 and their post still exist
        assert User.objects.filter(pk=user2.pk).exists()
        assert Post.objects.filter(pk=post2.pk).exists()

    def test_bulk_delete_users_with_relationships(self, db):
        """Test bulk deletion of users with Follow relationships."""
        # Create 3 users
        user1 = User.objects.create_user(
            username="bulk1",
            email="bulk1@example.com",
            password="testpass123",
        )
        user2 = User.objects.create_user(
            username="bulk2",
            email="bulk2@example.com",
            password="testpass123",
        )
        user3 = User.objects.create_user(
            username="bulk3",
            email="bulk3@example.com",
            password="testpass123",
        )

        # Create relationships
        user1.following.add(user2, user3)
        user2.following.add(user1)
        user3.following.add(user1, user2)

        # Verify relationships
        initial_follow_count = Follow.objects.count()
        assert initial_follow_count == 5  # 1+1+2 = 5 relationships

        user1_id = user1.pk
        user2_id = user2.pk

        # Bulk delete user1 and user2
        User.objects.filter(pk__in=[user1_id, user2_id]).delete()

        # Verify users deleted
        assert not User.objects.filter(pk=user1_id).exists()
        assert not User.objects.filter(pk=user2_id).exists()
        assert User.objects.filter(pk=user3.pk).exists()

        # Verify Follow relationships cleaned up
        assert Follow.objects.filter(follower_id=user1_id).count() == 0
        assert Follow.objects.filter(following_id=user1_id).count() == 0
        assert Follow.objects.filter(follower_id=user2_id).count() == 0
        assert Follow.objects.filter(following_id=user2_id).count() == 0

        # user3 should have no relationships left
        assert Follow.objects.filter(follower=user3).count() == 0
        assert Follow.objects.filter(following=user3).count() == 0
