"""Tests for DJGramm views."""

from django.urls import reverse

from app.models import Like, Post, User


class TestFeedView:
    """Tests for FeedView."""

    def test_feed_anonymous(self, client, db):
        """Test feed is accessible to anonymous users."""
        response = client.get(reverse("feed"))
        assert response.status_code == 200

    def test_feed_authenticated(self, authenticated_client):
        """Test feed is accessible to authenticated users."""
        response = authenticated_client.get(reverse("feed"))
        assert response.status_code == 200

    def test_feed_shows_posts(self, client, post):
        """Test feed displays posts."""
        response = client.get(reverse("feed"))
        assert response.status_code == 200
        assert post.caption in response.content.decode()

    def test_feed_pagination(self, client, user, db):
        """Test feed pagination."""
        # Create 15 posts (more than paginate_by=12)
        for i in range(15):
            Post.objects.create(author=user, caption=f"Post {i}")

        response = client.get(reverse("feed"))
        assert response.status_code == 200
        assert "page_obj" in response.context
        assert response.context["page_obj"].paginator.num_pages == 2


class TestRegisterView:
    """Tests for RegisterView."""

    def test_register_page_loads(self, client, db):
        """Test register page loads."""
        response = client.get(reverse("register"))
        assert response.status_code == 200

    def test_register_success(self, client, db):
        """Test successful registration."""
        response = client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!",
            },
        )
        assert response.status_code == 302  # Redirect after success
        assert User.objects.filter(email="newuser@example.com").exists()

    def test_register_password_mismatch(self, client, db):
        """Test registration with mismatched passwords."""
        response = client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "ComplexPass123!",
                "password2": "DifferentPass123!",
            },
        )
        assert response.status_code == 200  # Stays on page
        assert not User.objects.filter(email="newuser@example.com").exists()

    def test_register_duplicate_email(self, client, user):
        """Test registration with existing email."""
        response = client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": user.email,  # Existing email
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!",
            },
        )
        assert response.status_code == 200  # Stays on page with error


class TestLoginView:
    """Tests for LoginView."""

    def test_login_page_loads(self, client, db):
        """Test login page loads."""
        response = client.get(reverse("login"))
        assert response.status_code == 200

    def test_login_success(self, client, user):
        """Test successful login."""
        response = client.post(
            reverse("login"),
            {
                "username": user.email,
                "password": "testpass123",
            },
        )
        assert response.status_code == 302  # Redirect after success

    def test_login_invalid_credentials(self, client, user):
        """Test login with invalid credentials."""
        response = client.post(
            reverse("login"),
            {
                "username": user.email,
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 200  # Stays on page


class TestProfileView:
    """Tests for ProfileView."""

    def test_profile_view(self, client, user):
        """Test viewing a user profile."""
        response = client.get(
            reverse("profile", kwargs={"username": user.username})
        )
        assert response.status_code == 200
        assert user.username in response.content.decode()

    def test_profile_shows_posts(self, client, post):
        """Test profile shows user's posts."""
        response = client.get(
            reverse("profile", kwargs={"username": post.author.username})
        )
        assert response.status_code == 200
        assert "posts" in response.context

    def test_profile_not_found(self, client, db):
        """Test 404 for non-existent user."""
        response = client.get(
            reverse("profile", kwargs={"username": "nonexistent"})
        )
        assert response.status_code == 404


class TestProfileEditView:
    """Tests for ProfileEditView."""

    def test_edit_requires_login(self, client, db):
        """Test that profile edit requires login."""
        response = client.get(reverse("profile_edit"))
        assert response.status_code == 302  # Redirect to login

    def test_edit_page_loads(self, authenticated_client):
        """Test profile edit page loads for authenticated user."""
        response = authenticated_client.get(reverse("profile_edit"))
        assert response.status_code == 200

    def test_edit_profile(self, authenticated_client, user):
        """Test editing profile."""
        response = authenticated_client.post(
            reverse("profile_edit"),
            {
                "full_name": "Updated Name",
                "bio": "Updated bio",
            },
        )
        assert response.status_code == 302  # Redirect after success
        user.profile.refresh_from_db()
        assert user.profile.full_name == "Updated Name"


class TestPostDetailView:
    """Tests for PostDetailView."""

    def test_post_detail(self, client, post):
        """Test viewing post detail."""
        response = client.get(reverse("post_detail", kwargs={"pk": post.pk}))
        assert response.status_code == 200
        assert post.caption in response.content.decode()

    def test_post_not_found(self, client, db):
        """Test 404 for non-existent post."""
        response = client.get(reverse("post_detail", kwargs={"pk": 99999}))
        assert response.status_code == 404


class TestPostCreateView:
    """Tests for PostCreateView."""

    def test_create_requires_login(self, client, db):
        """Test that post creation requires login."""
        response = client.get(reverse("post_create"))
        assert response.status_code == 302  # Redirect to login

    def test_create_page_loads(self, authenticated_client):
        """Test post creation page loads."""
        response = authenticated_client.get(reverse("post_create"))
        assert response.status_code == 200

    def test_create_post(self, authenticated_client, user):
        """Test creating a post."""
        response = authenticated_client.post(
            reverse("post_create"),
            {
                "caption": "New post caption",
                "postimage_set-TOTAL_FORMS": "3",
                "postimage_set-INITIAL_FORMS": "0",
                "postimage_set-MIN_NUM_FORMS": "0",
                "postimage_set-MAX_NUM_FORMS": "10",
            },
        )
        assert response.status_code == 302  # Redirect after success
        assert Post.objects.filter(
            author=user, caption="New post caption"
        ).exists()


class TestPostUpdateView:
    """Tests for PostUpdateView."""

    def test_update_requires_login(self, client, post):
        """Test that post update requires login."""
        response = client.get(reverse("post_update", kwargs={"pk": post.pk}))
        assert response.status_code == 302

    def test_update_requires_author(self, authenticated_client, user2, db):
        """Test that only author can update post."""
        other_post = Post.objects.create(author=user2, caption="Other's post")
        response = authenticated_client.get(
            reverse("post_update", kwargs={"pk": other_post.pk})
        )
        assert response.status_code == 403  # Forbidden

    def test_update_post(self, authenticated_client, post):
        """Test updating a post."""
        response = authenticated_client.post(
            reverse("post_update", kwargs={"pk": post.pk}),
            {
                "caption": "Updated caption",
                "postimage_set-TOTAL_FORMS": "3",
                "postimage_set-INITIAL_FORMS": "0",
                "postimage_set-MIN_NUM_FORMS": "0",
                "postimage_set-MAX_NUM_FORMS": "10",
            },
        )
        assert response.status_code == 302
        post.refresh_from_db()
        assert post.caption == "Updated caption"


class TestPostDeleteView:
    """Tests for PostDeleteView."""

    def test_delete_requires_login(self, client, post):
        """Test that post deletion requires login."""
        response = client.post(reverse("post_delete", kwargs={"pk": post.pk}))
        assert response.status_code == 302

    def test_delete_requires_author(self, authenticated_client, user2, db):
        """Test that only author can delete post."""
        other_post = Post.objects.create(author=user2, caption="Other's post")
        response = authenticated_client.post(
            reverse("post_delete", kwargs={"pk": other_post.pk})
        )
        assert response.status_code == 403

    def test_delete_post(self, authenticated_client, post):
        """Test deleting a post."""
        post_pk = post.pk
        response = authenticated_client.post(
            reverse("post_delete", kwargs={"pk": post_pk})
        )
        assert response.status_code == 302
        assert not Post.objects.filter(pk=post_pk).exists()


class TestToggleLikeView:
    """Tests for toggle_like view."""

    def test_like_requires_login(self, client, post):
        """Test that liking requires login."""
        response = client.post(reverse("toggle_like", kwargs={"pk": post.pk}))
        assert response.status_code == 302  # Redirect to login

    def test_like_requires_post_method(self, authenticated_client, post):
        """Test that only POST method is allowed."""
        response = authenticated_client.get(
            reverse("toggle_like", kwargs={"pk": post.pk})
        )
        assert response.status_code == 405  # Method not allowed

    def test_like_post(self, authenticated_client, post, user):
        """Test liking a post."""
        response = authenticated_client.post(
            reverse("toggle_like", kwargs={"pk": post.pk})
        )
        assert response.status_code == 200
        data = response.json()
        assert data["liked"] is True
        assert data["likes_count"] == 1
        assert Like.objects.filter(user=user, post=post).exists()

    def test_unlike_post(self, authenticated_client, like):
        """Test unliking a post."""
        response = authenticated_client.post(
            reverse("toggle_like", kwargs={"pk": like.post.pk})
        )
        assert response.status_code == 200
        data = response.json()
        assert data["liked"] is False
        assert data["likes_count"] == 0


class TestTagPostsView:
    """Tests for TagPostsView."""

    def test_tag_posts(self, client, post, tag):
        """Test viewing posts by tag."""
        post.tags.add(tag)
        response = client.get(reverse("tag_posts", kwargs={"slug": tag.slug}))
        assert response.status_code == 200
        assert post in response.context["posts"]

    def test_tag_not_found(self, client, db):
        """Test 404 for non-existent tag."""
        response = client.get(
            reverse("tag_posts", kwargs={"slug": "nonexistent"})
        )
        assert response.status_code == 404
