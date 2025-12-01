"""Business logic services for DJGramm."""

from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image

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
