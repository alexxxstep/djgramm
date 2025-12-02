"""Business logic services for DJGramm."""

import re
from io import BytesIO

from django.core.files.base import ContentFile
from django.utils.text import slugify
from PIL import Image

from .models import Tag

# Allowed image types
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB


def validate_image(file) -> tuple[bool, str]:
    """
    Validate uploaded image file.

    Args:
        file: Uploaded file object

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file size
    if file.size > MAX_IMAGE_SIZE:
        return (
            False,
            f"Image too large. Maximum size is {MAX_IMAGE_SIZE // (1024 * 1024)}MB.",
        )

    # Check content type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        allowed = ", ".join(t.split("/")[1].upper() for t in ALLOWED_IMAGE_TYPES)
        return False, f"Invalid image type. Allowed types: {allowed}."

    # Try to open as image to verify it's valid
    try:
        with Image.open(file) as img:
            img.verify()
        file.seek(0)  # Reset file pointer after verify
    except Exception:
        return False, "Invalid or corrupted image file."

    return True, ""


def generate_thumbnail(
    image_field, max_size: tuple[int, int] = (300, 300)
) -> ContentFile:
    """
    Generate thumbnail from an image field.

    Args:
        image_field: Django ImageField or uploaded file
        max_size: Maximum dimensions (width, height)

    Returns:
        ContentFile with the thumbnail
    """
    with Image.open(image_field) as img:
        # Convert to RGB if necessary (for PNG with transparency)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Create thumbnail maintaining aspect ratio
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Save to buffer
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85, optimize=True)
        buffer.seek(0)

        return ContentFile(buffer.getvalue())


def process_uploaded_image(file, max_dimension: int = 1080) -> ContentFile:
    """
    Process uploaded image: resize if too large, optimize.

    Args:
        file: Uploaded file
        max_dimension: Maximum width or height

    Returns:
        ContentFile with processed image
    """
    with Image.open(file) as img:
        # Convert to RGB if necessary
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Resize if larger than max dimension
        if max(img.size) > max_dimension:
            ratio = max_dimension / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        # Save to buffer
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85, optimize=True)
        buffer.seek(0)

        return ContentFile(buffer.getvalue())


# =============================================================================
# Tag Extraction Services
# =============================================================================


def extract_hashtags(text: str) -> set[str]:
    """
    Extract hashtags from text.

    Examples:
        "#travel #nature" -> {"travel", "nature"}
        "Check out #sunset photos!" -> {"sunset"}
        "#tag1#tag2" -> {"tag1", "tag2"}

    Args:
        text: Text containing hashtags

    Returns:
        Set of tag names (lowercase, without #)
    """
    if not text:
        return set()

    # Pattern: # followed by word characters (letters, numbers, underscore)
    pattern = r"#(\w+)"
    matches = re.findall(pattern, text)

    # Normalize: lowercase, remove duplicates, filter empty
    tags = {tag.lower().strip() for tag in matches if tag.strip()}

    return tags


def create_or_get_tags(tag_names: set[str]) -> list[Tag]:
    """
    Create Tag objects if they don't exist, return all tags.

    Args:
        tag_names: Set of tag names (without #)

    Returns:
        List of Tag objects
    """
    tags = []

    for name in tag_names:
        # Skip empty or too long names
        if not name or len(name) > 50:
            continue

        # Generate slug
        slug = slugify(name)
        if not slug:
            continue

        # Get or create tag
        tag, created = Tag.objects.get_or_create(
            slug=slug, defaults={"name": name}
        )
        tags.append(tag)

    return tags


def sync_post_tags(post, caption: str) -> None:
    """
    Extract hashtags from caption and sync with post.tags.

    Args:
        post: Post instance
        caption: Post caption text
    """
    # Extract hashtags
    tag_names = extract_hashtags(caption)

    # Create/get tags
    tags = create_or_get_tags(tag_names)

    # Sync with post (replace all tags)
    post.tags.set(tags)
