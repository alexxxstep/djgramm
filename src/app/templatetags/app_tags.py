"""Custom template tags for DJGramm."""

import os
import re

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def linkify_hashtags(text):
    """
    Convert hashtags in text to links.

    Example:
        "Check #travel photos" -> "Check <a href='/tag/travel'>#travel</a> photos"

    Args:
        text: Text containing hashtags

    Returns:
        HTML string with clickable hashtag links
    """
    if not text:
        return text

    pattern = r"#(\w+)"

    def replace_hashtag(match):
        tag_name = match.group(1)
        slug = tag_name.lower()
        return (
            f'<a href="/tag/{slug}/" '
            f'class="text-secondary hover:underline">#{tag_name}</a>'
        )

    return mark_safe(re.sub(pattern, replace_hashtag, text))


@register.filter
def get_image_url(image_field):
    """
    Get image URL, handling Cloudinary or local storage.

    If Cloudinary is configured and DEFAULT_FILE_STORAGE is set to Cloudinary,
    returns Cloudinary URL. Otherwise tries to use local storage.

    Args:
        image_field: CloudinaryField or ImageField instance

    Returns:
        URL string
    """
    if not image_field:
        return ""

    # Check if Cloudinary storage is active
    has_cloudinary_storage = (
        hasattr(settings, "DEFAULT_FILE_STORAGE")
        and "cloudinary" in settings.DEFAULT_FILE_STORAGE.lower()
    )

    # If Cloudinary storage is active, use Cloudinary URL
    if has_cloudinary_storage:
        try:
            return image_field.url
        except Exception:
            # If Cloudinary URL generation fails, return empty
            return ""

    # If Cloudinary is not active, try local storage
    # Check if it's a CloudinaryField with public_id
    if hasattr(image_field, "public_id"):
        public_id = image_field.public_id
        if public_id:
            # Try to find local file based on public_id
            # public_id format: "posts/tiger_OccEUCo" -> "posts/tiger_OccEUCo.jpg"
            media_root = settings.MEDIA_ROOT
            # Try common extensions
            for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
                # Extract filename from public_id (last part after /)
                filename = public_id.split("/")[-1] + ext
                folder = public_id.split("/")[0] if "/" in public_id else ""
                if folder:
                    local_path = os.path.join(media_root, folder, filename)
                else:
                    local_path = os.path.join(media_root, filename)

                if os.path.exists(local_path):
                    # Return local media URL
                    if folder:
                        return f"{settings.MEDIA_URL}{folder}/{filename}"
                    else:
                        return f"{settings.MEDIA_URL}{filename}"

    # Default: try to use field's url property (works for both CloudinaryField and ImageField)
    try:
        return image_field.url
    except Exception:
        # Fallback to empty string if URL generation fails
        return ""
