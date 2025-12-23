"""Tests for OAuth functionality."""

from unittest.mock import MagicMock

from django.contrib.auth import get_user_model
from django.urls import reverse
from social_django.models import UserSocialAuth

from app.models import Profile
from app.pipeline import (
    associate_by_email,
    create_profile,
    get_username,
    save_avatar,
)

User = get_user_model()


class TestGetUsername:
    """Tests for get_username pipeline function."""

    def test_get_username_from_details(self, db):
        """Test username generation from details."""
        strategy = MagicMock()
        details = {"username": "testuser", "email": "test@example.com"}
        backend = MagicMock(name="github")

        result = get_username(strategy, details, backend)

        assert "username" in result
        assert result["username"] == "testuser"

    def test_get_username_from_email(self, db):
        """Test username generation from email if username not provided."""
        strategy = MagicMock()
        details = {"email": "testuser@example.com"}
        backend = MagicMock(name="github")

        result = get_username(strategy, details, backend)

        assert "username" in result
        assert result["username"] == "testuser"

    def test_get_username_handles_conflict(self, db, user):
        """Test username conflict resolution."""
        strategy = MagicMock()
        # user fixture creates "testuser"
        details = {"username": "testuser", "email": "new@example.com"}
        backend = MagicMock(name="github")

        result = get_username(strategy, details, backend)

        assert "username" in result
        assert result["username"] == "testuser_1"

    def test_get_username_fallback(self, db):
        """Test username fallback when email and username missing."""
        strategy = MagicMock()
        details = {}
        backend = MagicMock()
        backend.name = "github"  # Set name attribute directly

        result = get_username(strategy, details, backend)

        assert "username" in result
        assert result["username"].startswith("user_github")


class TestAssociateByEmail:
    """Tests for associate_by_email pipeline function."""

    def test_associate_existing_user(self, db, user):
        """Test associating OAuth with existing user by email."""
        backend = MagicMock()
        details = {"email": "test@example.com"}
        response = {}

        result = associate_by_email(backend, details, response)

        assert result is not None
        assert result["user"] == user
        assert result["is_new"] is False

    def test_associate_new_user(self, db):
        """Test no association for new user."""
        backend = MagicMock()
        details = {"email": "newuser@example.com"}
        response = {}

        result = associate_by_email(backend, details, response)

        assert result is None

    def test_associate_no_email(self, db):
        """Test no association when email is missing."""
        backend = MagicMock()
        details = {}
        response = {}

        result = associate_by_email(backend, details, response)

        assert result is None


class TestCreateProfile:
    """Tests for create_profile pipeline function."""

    def test_create_profile_new_user(self, db, user):
        """Test profile creation for new OAuth user."""
        backend = MagicMock()
        response = {}

        # Delete existing profile
        Profile.objects.filter(user=user).delete()

        result = create_profile(backend, user, response, is_new=True)

        assert result is None
        assert Profile.objects.filter(user=user).exists()

    def test_create_profile_existing_user(self, db, user):
        """Test profile creation doesn't duplicate for existing user."""
        backend = MagicMock()
        response = {}
        profile_count_before = Profile.objects.filter(user=user).count()

        result = create_profile(backend, user, response, is_new=False)

        assert result is None
        assert (
            Profile.objects.filter(user=user).count() == profile_count_before
        )


class TestSaveAvatar:
    """Tests for save_avatar pipeline function."""

    def test_save_avatar_github(self, db, user):
        """Test avatar URL extraction from GitHub response."""
        backend = MagicMock(name="github")
        response = {
            "avatar_url": "https://avatars.githubusercontent.com/u/123"
        }
        profile, _ = Profile.objects.get_or_create(user=user)

        result = save_avatar(backend, user, response)

        assert result is None
        # Avatar URL is stored but not downloaded yet (pass in function)

    def test_save_avatar_google(self, db, user):
        """Test avatar URL extraction from Google response."""
        backend = MagicMock(name="google-oauth2")
        response = {"picture": "https://lh3.googleusercontent.com/a/photo.jpg"}
        profile, _ = Profile.objects.get_or_create(user=user)

        result = save_avatar(backend, user, response)

        assert result is None

    def test_save_avatar_other_provider(self, db, user):
        """Test save_avatar skips non-GitHub/Google providers."""
        backend = MagicMock(name="facebook")
        response = {}

        result = save_avatar(backend, user, response)

        assert result is None


class TestDisconnectOAuth:
    """Tests for disconnect_oauth view."""

    def test_disconnect_oauth_success(self, authenticated_client, user, db):
        """Test successful OAuth disconnection."""
        # Create social auth connection
        UserSocialAuth.objects.create(
            user=user, provider="github", uid="12345"
        )

        response = authenticated_client.post(
            reverse("disconnect_oauth", kwargs={"provider": "github"})
        )

        assert response.status_code == 302
        assert not UserSocialAuth.objects.filter(
            user=user, provider="github"
        ).exists()

    def test_disconnect_oauth_not_connected(self, authenticated_client, user):
        """Test disconnecting non-connected provider."""
        response = authenticated_client.post(
            reverse("disconnect_oauth", kwargs={"provider": "github"})
        )

        assert response.status_code == 302

    def test_disconnect_oauth_requires_login(self, client, db):
        """Test disconnect requires authentication."""
        response = client.post(
            reverse("disconnect_oauth", kwargs={"provider": "github"})
        )

        assert response.status_code == 302  # Redirect to login

    def test_disconnect_oauth_last_method(
        self, authenticated_client, user, db
    ):
        """Test cannot disconnect last authentication method."""
        # Create social auth connection (only method)
        UserSocialAuth.objects.create(
            user=user, provider="github", uid="12345"
        )
        # Ensure user has no password
        user.set_unusable_password()
        user.save()

        response = authenticated_client.post(
            reverse("disconnect_oauth", kwargs={"provider": "github"})
        )

        assert response.status_code == 302
        # Should still be connected (disconnect prevented)
        assert UserSocialAuth.objects.filter(
            user=user, provider="github"
        ).exists()

    def test_disconnect_oauth_with_password(
        self, authenticated_client, user, db
    ):
        """Test can disconnect when password is set."""
        # Create social auth connection
        UserSocialAuth.objects.create(
            user=user, provider="github", uid="12345"
        )

        # User already has password from fixture, but let's ensure it's usable
        # The user fixture creates user with password, so it should be usable
        # But let's verify and potentially reset it
        if not user.has_usable_password():
            user.set_password("testpass123")
            user.save()

        # Verify password is usable
        assert user.has_usable_password(), "Password should be usable"
        # Also verify password field directly
        assert user.password and not user.password.startswith("!"), (
            "Password field should be set and usable"
        )

        response = authenticated_client.post(
            reverse("disconnect_oauth", kwargs={"provider": "github"})
        )

        assert response.status_code == 302
        assert not UserSocialAuth.objects.filter(
            user=user, provider="github"
        ).exists()


class TestOAuthURLs:
    """Tests for OAuth URL patterns."""

    def test_oauth_login_github(self, client, db):
        """Test GitHub OAuth login URL is accessible."""
        response = client.get(
            reverse("social:begin", kwargs={"backend": "github"})
        )
        # Should redirect to GitHub
        assert response.status_code in [302, 200]

    def test_oauth_login_google(self, client, db):
        """Test Google OAuth login URL is accessible."""
        response = client.get(
            reverse("social:begin", kwargs={"backend": "google-oauth2"})
        )
        # Should redirect to Google
        assert response.status_code in [302, 200]


class TestProfileEditOAuth:
    """Tests for OAuth section in profile edit."""

    def test_profile_edit_shows_oauth_section(
        self, authenticated_client, user
    ):
        """Test profile edit page shows Connected Accounts section."""
        response = authenticated_client.get(reverse("profile_edit"))
        assert response.status_code == 200
        assert "Connected Accounts" in response.content.decode()

    def test_profile_edit_shows_connected_providers(
        self, authenticated_client, user, db
    ):
        """Test profile edit shows connected providers."""
        UserSocialAuth.objects.create(
            user=user, provider="github", uid="12345"
        )

        response = authenticated_client.get(reverse("profile_edit"))
        content = response.content.decode()

        assert response.status_code == 200
        assert "GitHub" in content
        assert "Disconnect" in content

    def test_profile_edit_shows_connect_buttons(
        self, authenticated_client, user
    ):
        """Test profile edit shows Connect buttons."""
        response = authenticated_client.get(reverse("profile_edit"))
        content = response.content.decode()

        assert response.status_code == 200
        assert "GitHub" in content
        assert "Google" in content
        assert "Connect" in content
