"""Custom OAuth pipeline functions for social-auth-app-django."""


def get_username(strategy, details, backend, user=None, *args, **kwargs):
    """Generate unique username, handling conflicts."""
    # If user already exists (from associate_by_email), skip generation
    if user and user.pk:
        return {"username": user.username}

    from django.contrib.auth import get_user_model

    User = get_user_model()
    username = (
        details.get("username") or details.get("email", "").split("@")[0]
    )

    if not username:
        # Fallback: use email prefix or generate random
        email = details.get("email", "")
        if email:
            username = email.split("@")[0]
        else:
            username = f"user_{backend.name}"

    # Make username unique if it exists
    original_username = username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{original_username}_{counter}"
        counter += 1

    return {"username": username}


def associate_by_email(backend, details, response, *args, **kwargs):
    """Associate OAuth account with existing user by email."""
    email = details.get("email")
    if email:
        from django.contrib.auth import get_user_model

        User = get_user_model()
        # Try exact match first (case-sensitive)
        try:
            user = User.objects.get(email=email)
            return {"user": user, "is_new": False}
        except User.DoesNotExist:
            # Try case-insensitive match as fallback
            try:
                user = User.objects.get(email__iexact=email)
                return {"user": user, "is_new": False}
            except User.DoesNotExist:
                pass
    return None


def create_profile(backend, user, response, *args, **kwargs):
    """Ensure Profile is created for OAuth users."""
    if user:
        from app.models import Profile

        # get_or_create is safe - won't create duplicate if exists
        Profile.objects.get_or_create(user=user)
    return None


def save_avatar(backend, user, response, *args, **kwargs):
    """Save avatar from OAuth provider to Profile."""
    if user and backend.name in ("github", "google-oauth2"):
        from app.models import Profile

        profile, created = Profile.objects.get_or_create(user=user)

        # Get avatar URL from response
        avatar_url = None
        if backend.name == "github":
            avatar_url = response.get("avatar_url")
        elif backend.name == "google-oauth2":
            avatar_url = response.get("picture")

        # Save avatar URL (will be downloaded later if needed)
        if avatar_url and not profile.avatar:
            # For now, just store URL - actual download can be done later
            # or use Cloudinary to fetch from URL
            pass

    return None
