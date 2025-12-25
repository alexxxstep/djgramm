"""Django signals for DJGramm."""

import logging

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import Profile, User

logger = logging.getLogger(__name__)


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
def cleanup_user_data(sender, instance, **kwargs):
    """Clean up user-related data before deletion."""
    logger.info(
        f"Starting cleanup for user: {instance.email} (ID: {instance.pk})"
    )

    try:
        # 1. Clean up Follow relationships explicitly
        # This prevents potential CASCADE conflicts
        from .models import Follow

        followers_count = Follow.objects.filter(following=instance).count()
        following_count = Follow.objects.filter(follower=instance).count()

        logger.info(
            f"User {instance.email} has {followers_count} followers "
            f"and follows {following_count} users"
        )

        # Delete Follow relationships where user is follower
        Follow.objects.filter(follower=instance).delete()
        logger.info(f"Deleted {following_count} following relationships")

        # Delete Follow relationships where user is being followed
        Follow.objects.filter(following=instance).delete()
        logger.info(f"Deleted {followers_count} follower relationships")

    except Exception as e:
        logger.error(
            f"Error cleaning up Follow relationships for {instance.email}: {e}",
            exc_info=True,
        )

    try:
        # 2. Clean up OAuth associations
        from social_django.models import UserSocialAuth

        oauth_count = UserSocialAuth.objects.filter(user=instance).count()
        if oauth_count > 0:
            UserSocialAuth.objects.filter(user=instance).delete()
            logger.info(f"Deleted {oauth_count} OAuth associations")

    except ImportError:
        logger.debug("social_django not installed")
    except Exception as e:
        logger.error(
            f"Error cleaning up OAuth for {instance.email}: {e}",
            exc_info=True,
        )

    logger.info(f"Cleanup completed for user: {instance.email}")
