"""Django signals for DJGramm."""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import Profile, User


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a Profile when a new User is created."""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the Profile when the User is saved."""
    # Skip if user is being deleted (profile will be deleted via CASCADE)
    if kwargs.get("raw") or not instance.pk:
        return

    # Only save if profile exists and user is not being deleted
    try:
        if hasattr(instance, "profile") and instance.profile:
            instance.profile.save()
    except Profile.DoesNotExist:
        # Profile doesn't exist yet, will be created by create_user_profile
        pass


@receiver(pre_delete, sender=User)
def cleanup_user_oauth(sender, instance, **kwargs):
    """Clean up OAuth associations before user deletion."""
    try:
        from social_django.models import UserSocialAuth

        # Delete all OAuth associations
        UserSocialAuth.objects.filter(user=instance).delete()
    except ImportError:
        # social_django not installed or not available
        pass
    except Exception:
        # Ignore errors during cleanup
        pass
