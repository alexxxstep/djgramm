"""Django signals for DJGramm."""

import json
import logging
import time

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
    # #region agent log
    try:
        with open(".cursor/debug.log", "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "sessionId": "debug-session",
                        "runId": "run1",
                        "hypothesisId": "D",
                        "location": "signals.py:36",
                        "message": "cleanup_user_data signal entry",
                        "data": {
                            "user_id": instance.pk,
                            "user_email": instance.email,
                        },
                        "timestamp": int(time.time() * 1000),
                    }
                )
                + "\n"
            )
    except Exception:
        pass
    # #endregion

    logger.info(
        f"Starting cleanup for user: {instance.email} (ID: {instance.pk})"
    )

    try:
        # 1. Clean up Follow relationships explicitly
        # This prevents potential CASCADE conflicts
        from .models import Follow

        followers_count = Follow.objects.filter(following=instance).count()
        following_count = Follow.objects.filter(follower=instance).count()

        # #region agent log
        try:
            with open(".cursor/debug.log", "a", encoding="utf-8") as f:
                f.write(
                    json.dumps(
                        {
                            "sessionId": "debug-session",
                            "runId": "run1",
                            "hypothesisId": "D",
                            "location": "signals.py:48",
                            "message": "Follow relationships count",
                            "data": {
                                "followers_count": followers_count,
                                "following_count": following_count,
                            },
                            "timestamp": int(time.time() * 1000),
                        }
                    )
                    + "\n"
                )
        except Exception:
            pass
        # #endregion

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
        # #region agent log
        try:
            with open(".cursor/debug.log", "a", encoding="utf-8") as f:
                f.write(
                    json.dumps(
                        {
                            "sessionId": "debug-session",
                            "runId": "run1",
                            "hypothesisId": "D",
                            "location": "signals.py:64",
                            "message": "Follow cleanup error",
                            "data": {
                                "error_type": type(e).__name__,
                                "error_message": str(e),
                            },
                            "timestamp": int(time.time() * 1000),
                        }
                    )
                    + "\n"
                )
        except Exception:
            pass
        # #endregion

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

    try:
        # 3. Clean up Cloudinary images (avatar and post images)
        import cloudinary.uploader

        # #region agent log
        try:
            with open(".cursor/debug.log", "a", encoding="utf-8") as f:
                f.write(
                    json.dumps(
                        {
                            "sessionId": "debug-session",
                            "runId": "run1",
                            "hypothesisId": "E",
                            "location": "signals.py:87",
                            "message": "Cloudinary cleanup start",
                            "data": {
                                "has_profile": hasattr(instance, "profile"),
                                "has_avatar": hasattr(instance, "profile")
                                and instance.profile.avatar,
                            },
                            "timestamp": int(time.time() * 1000),
                        }
                    )
                    + "\n"
                )
        except Exception:
            pass
        # #endregion

        deleted_images = 0

        # Delete user avatar
        if hasattr(instance, "profile") and instance.profile.avatar:
            avatar_public_id = getattr(
                instance.profile.avatar, "public_id", None
            )
            if avatar_public_id:
                cloudinary.uploader.destroy(avatar_public_id)
                deleted_images += 1
                logger.info(
                    f"Deleted avatar from Cloudinary: {avatar_public_id}"
                )

        # Delete all post images
        posts_count = instance.posts.count()
        if posts_count > 0:
            for post in instance.posts.all():
                for image in post.images.all():
                    if image.image:
                        image_public_id = getattr(
                            image.image, "public_id", None
                        )
                        if image_public_id:
                            cloudinary.uploader.destroy(image_public_id)
                            deleted_images += 1

            if deleted_images > 1:  # More than just avatar
                logger.info(
                    f"Deleted {deleted_images} images from Cloudinary "
                    f"({posts_count} posts)"
                )

        # #region agent log
        try:
            with open(".cursor/debug.log", "a", encoding="utf-8") as f:
                f.write(
                    json.dumps(
                        {
                            "sessionId": "debug-session",
                            "runId": "run1",
                            "hypothesisId": "E",
                            "location": "signals.py:118",
                            "message": "Cloudinary cleanup complete",
                            "data": {
                                "deleted_images": deleted_images,
                                "posts_count": posts_count,
                            },
                            "timestamp": int(time.time() * 1000),
                        }
                    )
                    + "\n"
                )
        except Exception:
            pass
        # #endregion

    except ImportError:
        logger.debug("Cloudinary not installed, skipping image cleanup")
    except Exception as e:
        # #region agent log
        try:
            with open(".cursor/debug.log", "a", encoding="utf-8") as f:
                f.write(
                    json.dumps(
                        {
                            "sessionId": "debug-session",
                            "runId": "run1",
                            "hypothesisId": "E",
                            "location": "signals.py:126",
                            "message": "Cloudinary cleanup error",
                            "data": {
                                "error_type": type(e).__name__,
                                "error_message": str(e),
                            },
                            "timestamp": int(time.time() * 1000),
                        }
                    )
                    + "\n"
                )
        except Exception:
            pass
        # #endregion

        logger.error(
            f"Error deleting Cloudinary images for {instance.email}: {e}",
            exc_info=True,
        )
        # Don't raise - allow user deletion even if Cloudinary cleanup fails

    # #region agent log
    try:
        with open(".cursor/debug.log", "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "sessionId": "debug-session",
                        "runId": "run1",
                        "hypothesisId": "D",
                        "location": "signals.py:133",
                        "message": "cleanup_user_data signal complete",
                        "data": {
                            "user_id": instance.pk,
                            "user_email": instance.email,
                        },
                        "timestamp": int(time.time() * 1000),
                    }
                )
                + "\n"
            )
    except Exception:
        pass
    # #endregion

    logger.info(f"Cleanup completed for user: {instance.email}")
