"""Tests for DJGramm services."""

from io import BytesIO
from unittest.mock import MagicMock

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from app.services import (
    ALLOWED_IMAGE_TYPES,
    MAX_IMAGE_SIZE,
    generate_thumbnail,
    process_uploaded_image,
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
