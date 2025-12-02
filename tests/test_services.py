"""Tests for DJGramm services."""

from io import BytesIO
from unittest.mock import MagicMock

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from app.models import Tag
from app.services import (
    ALLOWED_IMAGE_TYPES,
    MAX_IMAGE_SIZE,
    create_or_get_tags,
    extract_hashtags,
    generate_thumbnail,
    process_uploaded_image,
    sync_post_tags,
    validate_image,
)


class TestValidateImage:
    """Tests for validate_image function."""

    def create_image_file(
        self, size=(100, 100), format="JPEG", content_type="image/jpeg"
    ):
        """Helper to create an image file."""
        img = Image.new("RGB", size, color="red")
        buffer = BytesIO()
        img.save(buffer, format=format)
        buffer.seek(0)

        file = SimpleUploadedFile(
            name=f"test.{format.lower()}",
            content=buffer.getvalue(),
            content_type=content_type,
        )
        return file

    def test_valid_jpeg_image(self):
        """Test valid JPEG image passes validation."""
        file = self.create_image_file(format="JPEG", content_type="image/jpeg")
        is_valid, error = validate_image(file)
        assert is_valid is True
        assert error == ""

    def test_valid_png_image(self):
        """Test valid PNG image passes validation."""
        file = self.create_image_file(format="PNG", content_type="image/png")
        is_valid, error = validate_image(file)
        assert is_valid is True
        assert error == ""

    def test_valid_webp_image(self):
        """Test valid WebP image passes validation."""
        file = self.create_image_file(format="WEBP", content_type="image/webp")
        is_valid, error = validate_image(file)
        assert is_valid is True
        assert error == ""

    def test_invalid_content_type(self):
        """Test invalid content type fails validation."""
        file = MagicMock()
        file.size = 1000
        file.content_type = "image/gif"  # Not allowed

        is_valid, error = validate_image(file)
        assert is_valid is False
        assert "Invalid image type" in error

    def test_file_too_large(self):
        """Test file exceeding max size fails validation."""
        file = MagicMock()
        file.size = MAX_IMAGE_SIZE + 1  # Exceeds limit
        file.content_type = "image/jpeg"

        is_valid, error = validate_image(file)
        assert is_valid is False
        assert "too large" in error

    def test_corrupted_image(self):
        """Test corrupted image fails validation."""
        file = SimpleUploadedFile(
            name="test.jpg",
            content=b"not a valid image",
            content_type="image/jpeg",
        )

        is_valid, error = validate_image(file)
        assert is_valid is False
        assert "Invalid or corrupted" in error


class TestGenerateThumbnail:
    """Tests for generate_thumbnail function."""

    def create_image_file(self, size=(800, 800)):
        """Helper to create an image file."""
        img = Image.new("RGB", size, color="blue")
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        buffer.seek(0)
        return buffer

    def test_generate_thumbnail_default_size(self):
        """Test generating thumbnail with default size."""
        image_file = self.create_image_file(size=(800, 800))
        result = generate_thumbnail(image_file)

        # Open result and check size
        result_img = Image.open(BytesIO(result.read()))
        assert result_img.size[0] <= 300
        assert result_img.size[1] <= 300

    def test_generate_thumbnail_custom_size(self):
        """Test generating thumbnail with custom size."""
        image_file = self.create_image_file(size=(800, 800))
        result = generate_thumbnail(image_file, max_size=(100, 100))

        result_img = Image.open(BytesIO(result.read()))
        assert result_img.size[0] <= 100
        assert result_img.size[1] <= 100

    def test_generate_thumbnail_preserves_aspect_ratio(self):
        """Test that thumbnail preserves aspect ratio."""
        # Create 800x400 image (2:1 ratio)
        image_file = self.create_image_file(size=(800, 400))
        result = generate_thumbnail(image_file, max_size=(200, 200))

        result_img = Image.open(BytesIO(result.read()))
        # Should be 200x100 (maintaining 2:1 ratio)
        assert result_img.size[0] == 200
        assert result_img.size[1] == 100

    def test_generate_thumbnail_rgba_conversion(self):
        """Test that RGBA images are converted to RGB."""
        img = Image.new("RGBA", (400, 400), color=(255, 0, 0, 128))
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        result = generate_thumbnail(buffer)
        result_img = Image.open(BytesIO(result.read()))
        assert result_img.mode == "RGB"


class TestProcessUploadedImage:
    """Tests for process_uploaded_image function."""

    def create_image_file(self, size=(2000, 2000)):
        """Helper to create a large image file."""
        img = Image.new("RGB", size, color="green")
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        buffer.seek(0)
        return buffer

    def test_process_large_image(self):
        """Test processing large image resizes it."""
        image_file = self.create_image_file(size=(2000, 2000))
        result = process_uploaded_image(image_file, max_dimension=1080)

        result_img = Image.open(BytesIO(result.read()))
        assert max(result_img.size) <= 1080

    def test_process_small_image_unchanged(self):
        """Test that small images are not resized."""
        image_file = self.create_image_file(size=(500, 500))
        result = process_uploaded_image(image_file, max_dimension=1080)

        result_img = Image.open(BytesIO(result.read()))
        assert result_img.size == (500, 500)

    def test_process_preserves_aspect_ratio(self):
        """Test that processing preserves aspect ratio."""
        # Create 2000x1000 image (2:1 ratio)
        img = Image.new("RGB", (2000, 1000), color="red")
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        buffer.seek(0)

        result = process_uploaded_image(buffer, max_dimension=1000)
        result_img = Image.open(BytesIO(result.read()))

        # Should be 1000x500 (maintaining 2:1 ratio)
        assert result_img.size[0] == 1000
        assert result_img.size[1] == 500


class TestConstants:
    """Tests for service constants."""

    def test_allowed_image_types(self):
        """Test allowed image types are correct."""
        assert "image/jpeg" in ALLOWED_IMAGE_TYPES
        assert "image/png" in ALLOWED_IMAGE_TYPES
        assert "image/webp" in ALLOWED_IMAGE_TYPES
        assert len(ALLOWED_IMAGE_TYPES) == 3

    def test_max_image_size(self):
        """Test max image size is 10MB."""
        assert MAX_IMAGE_SIZE == 10 * 1024 * 1024


class TestExtractHashtags:
    """Tests for extract_hashtags function."""

    def test_extract_simple_hashtags(self):
        """Test extracting simple hashtags."""
        assert extract_hashtags("#travel #nature") == {"travel", "nature"}

    def test_extract_hashtags_in_text(self):
        """Test extracting hashtags from text."""
        assert extract_hashtags("Check out #sunset photos!") == {"sunset"}

    def test_extract_multiple_hashtags(self):
        """Test extracting multiple hashtags."""
        assert extract_hashtags("#tag1#tag2") == {"tag1", "tag2"}

    def test_extract_no_hashtags(self):
        """Test text without hashtags."""
        assert extract_hashtags("No tags here") == set()

    def test_extract_empty_string(self):
        """Test empty string."""
        assert extract_hashtags("") == set()

    def test_extract_case_insensitive(self):
        """Test that hashtags are case-insensitive."""
        assert extract_hashtags("#Travel #TRAVEL #travel") == {"travel"}

    def test_extract_with_numbers(self):
        """Test hashtags with numbers."""
        assert extract_hashtags("#tag123 #test1") == {"tag123", "test1"}


class TestCreateOrGetTags:
    """Tests for create_or_get_tags function."""

    def test_create_tags(self, db):
        """Test creating new tags."""
        tags = create_or_get_tags({"travel", "nature"})
        assert len(tags) == 2
        assert all(isinstance(tag, type(tags[0])) for tag in tags)

    def test_get_existing_tags(self, db, tag):
        """Test getting existing tags."""
        tags = create_or_get_tags({tag.name})
        assert len(tags) == 1
        assert tags[0] == tag

    def test_skip_too_long_names(self, db):
        """Test skipping tags with names longer than 50 chars."""
        long_name = "a" * 51
        tags = create_or_get_tags({long_name})
        assert len(tags) == 0

    def test_empty_set(self, db):
        """Test with empty set."""
        tags = create_or_get_tags(set())
        assert len(tags) == 0


class TestSyncPostTags:
    """Tests for sync_post_tags function."""

    def test_sync_tags_from_caption(self, db, post):
        """Test syncing tags from caption."""
        post.caption = "Check #travel #nature photos"
        sync_post_tags(post, post.caption)

        assert post.tags.count() == 2
        assert post.tags.filter(slug="travel").exists()
        assert post.tags.filter(slug="nature").exists()

    def test_sync_replaces_existing_tags(self, db, post, tag):
        """Test that sync replaces existing tags."""
        # Add existing tag
        post.tags.add(tag)

        # Sync with new caption
        post.caption = "New #sunset photo"
        sync_post_tags(post, post.caption)

        # Old tag should be removed
        assert not post.tags.filter(slug=tag.slug).exists()
        # New tag should be added
        assert post.tags.filter(slug="sunset").exists()

    def test_sync_empty_caption(self, db, post, tag):
        """Test syncing with empty caption removes all tags."""
        post.tags.add(tag)
        sync_post_tags(post, "")

        assert post.tags.count() == 0

    def test_sync_case_insensitive(self, db, post):
        """Test that sync handles case-insensitive hashtags."""
        post.caption = "#Travel #TRAVEL #travel"
        sync_post_tags(post, post.caption)

        # Should create only one tag
        assert post.tags.count() == 1
        assert post.tags.filter(slug="travel").exists()
