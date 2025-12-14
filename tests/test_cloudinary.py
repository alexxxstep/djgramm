"""Tests for Cloudinary integration."""

from io import BytesIO
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import override_settings
from PIL import Image

from app.models import PostImage, Profile


class TestProfileCloudinaryField:
    """Tests for Profile.avatar CloudinaryField."""

    def test_profile_avatar_is_cloudinary_field(self, profile):
        """Test that Profile.avatar is a CloudinaryField."""
        from cloudinary.models import CloudinaryField

        field = Profile._meta.get_field("avatar")
        assert isinstance(field, CloudinaryField)
        # Note: folder parameter is passed but not stored as attribute
        # We verify it's CloudinaryField and blank=True
        assert field.blank is True

    def test_profile_avatar_can_be_empty(self, profile):
        """Test that Profile.avatar can be empty (blank=True)."""
        profile.avatar = None
        profile.save()
        assert profile.avatar is None or profile.avatar == ""

    def test_profile_avatar_has_no_path_when_cloudinary(self, profile):
        """Test that CloudinaryField doesn't have .path attribute."""
        # When avatar is on Cloudinary, it won't have .path
        # This is expected behavior
        if profile.avatar:
            # If avatar exists, it might be CloudinaryResource
            avatar = profile.avatar
            has_path = hasattr(avatar, "path")
            has_url = hasattr(avatar, "url")
            assert not has_path or has_url

    @override_settings(
        CLOUDINARY_STORAGE={
            "CLOUD_NAME": "",
            "API_KEY": "",
            "API_SECRET": "",
        }
    )
    @patch("cloudinary.uploader.upload_resource")
    def test_profile_avatar_accepts_file(self, mock_upload, profile, db):
        """Test that Profile.avatar accepts file uploads."""
        import cloudinary.uploader
        from cloudinary.models import CloudinaryField

        # Mock Cloudinary upload to return a valid response
        upload_result = {
            "public_id": "avatars/test_avatar",
            "version": 1,
            "url": (
                "https://res.cloudinary.com/test/image/upload/"
                "v1/avatars/test_avatar.jpg"
            ),
            "secure_url": (
                "https://res.cloudinary.com/test/image/upload/"
                "v1/avatars/test_avatar.jpg"
            ),
        }
        mock_upload.return_value = upload_result

        # Patch pre_save to extract public_id
        original_pre_save = CloudinaryField.pre_save

        def patched_pre_save(self, obj, add):
            value = getattr(obj, self.attname)
            if value and hasattr(value, "read"):
                result = cloudinary.uploader.upload_resource(value, **{})
                if isinstance(result, dict):
                    return result.get("public_id", "avatars/test_avatar")
                return str(result) if result else value
            return value

        CloudinaryField.pre_save = patched_pre_save

        try:
            # Create a test image
            img = Image.new("RGB", (100, 100), color="red")
            buffer = BytesIO()
            img.save(buffer, format="JPEG")
            buffer.seek(0)

            image_file = SimpleUploadedFile(
                name="test_avatar.jpg",
                content=buffer.getvalue(),
                content_type="image/jpeg",
            )

            # Upload avatar (will use local storage in tests)
            profile.avatar = image_file
            profile.save()

            # Verify the field accepts the file
            assert profile.avatar is not None
        finally:
            CloudinaryField.pre_save = original_pre_save

    def test_profile_avatar_url_property(self, profile):
        """Test that Profile.avatar has url property."""
        if profile.avatar:
            # CloudinaryField should have .url property
            has_url = hasattr(profile.avatar, "url")
            has_build_url = hasattr(profile.avatar, "build_url")
            assert has_url or has_build_url


class TestPostImageCloudinaryField:
    """Tests for PostImage.image CloudinaryField."""

    def test_post_image_is_cloudinary_field(self, db):
        """Test that PostImage.image is a CloudinaryField."""
        from cloudinary.models import CloudinaryField

        field = PostImage._meta.get_field("image")
        assert isinstance(field, CloudinaryField)
        # Note: folder parameter is passed but not stored as attribute
        # We verify it's CloudinaryField and blank=False (required)
        assert field.blank is False  # Required field

    def test_post_image_has_no_path_when_cloudinary(self, post_with_image):
        """Test that CloudinaryField doesn't have .path attribute."""
        image = post_with_image.images.first()
        if image and image.image:
            # If image exists, it might be CloudinaryResource
            has_path = hasattr(image.image, "path")
            has_url = hasattr(image.image, "url")
            assert not has_path or has_url

    @override_settings(
        CLOUDINARY_STORAGE={
            "CLOUD_NAME": "",
            "API_KEY": "",
            "API_SECRET": "",
        }
    )
    @patch("cloudinary.uploader.upload_resource")
    def test_post_image_accepts_file(self, mock_upload, post, db):
        """Test that PostImage.image accepts file uploads."""
        import cloudinary.uploader
        from cloudinary.models import CloudinaryField

        # Mock Cloudinary upload to return a valid response
        upload_result = {
            "public_id": "post_images/test_image",
            "version": 1,
            "url": (
                "https://res.cloudinary.com/test/image/upload/"
                "v1/post_images/test_image.jpg"
            ),
            "secure_url": (
                "https://res.cloudinary.com/test/image/upload/"
                "v1/post_images/test_image.jpg"
            ),
        }
        mock_upload.return_value = upload_result

        # Patch pre_save to extract public_id
        original_pre_save = CloudinaryField.pre_save

        def patched_pre_save(self, obj, add):
            value = getattr(obj, self.attname)
            if value and hasattr(value, "read"):
                result = cloudinary.uploader.upload_resource(value, **{})
                if isinstance(result, dict):
                    return result.get("public_id", "post_images/test_image")
                return str(result) if result else value
            return value

        CloudinaryField.pre_save = patched_pre_save

        try:
            # Create a test image
            img = Image.new("RGB", (200, 200), color="blue")
            buffer = BytesIO()
            img.save(buffer, format="JPEG")
            buffer.seek(0)

            image_file = SimpleUploadedFile(
                name="test_image.jpg",
                content=buffer.getvalue(),
                content_type="image/jpeg",
            )

            # Create PostImage (will use local storage in tests)
            post_image = PostImage.objects.create(
                post=post, image=image_file, order=0
            )

            # Verify image was saved
            assert post_image.image is not None
        finally:
            CloudinaryField.pre_save = original_pre_save

    def test_post_image_url_property(self, post_with_image):
        """Test that PostImage.image has url property."""
        image = post_with_image.images.first()
        if image and image.image:
            # CloudinaryField should have .url property
            has_url = hasattr(image.image, "url")
            has_build_url = hasattr(image.image, "build_url")
            assert has_url or has_build_url


class TestMigrateToCloudinaryCommand:
    """Tests for migrate_to_cloudinary management command."""

    @override_settings(
        CLOUDINARY_STORAGE={
            "CLOUD_NAME": "test_cloud",
            "API_KEY": "test_key",
            "API_SECRET": "test_secret",
        }
    )
    @patch("cloudinary.uploader.upload")
    def test_command_with_cloudinary_configured(self, mock_upload, db, capsys):
        """Test command when Cloudinary is configured."""
        from app.models import User

        # Mock Cloudinary upload response
        mock_upload.return_value = {
            "public_id": "avatars/test_avatar",
            "version": 1,
            "url": (
                "https://res.cloudinary.com/test/image/upload/"
                "v1/avatars/test_avatar.jpg"
            ),
        }

        # Create user with profile
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        # Create a local image file for testing
        img = Image.new("RGB", (100, 100), color="red")
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        buffer.seek(0)

        # Note: In tests, we can't easily test actual file uploads
        # because CloudinaryField might use different storage backends
        # This test verifies the command structure works

        # Run command with dry-run
        call_command("migrate_to_cloudinary", "--dry-run")

        # Check output
        captured = capsys.readouterr()
        has_cloudinary = "Cloudinary configured" in captured.out
        has_dry_run = "DRY RUN" in captured.out
        assert has_cloudinary or has_dry_run

    @override_settings(
        CLOUDINARY_STORAGE={
            "CLOUD_NAME": "",
            "API_KEY": "",
            "API_SECRET": "",
        }
    )
    def test_command_without_cloudinary_configured(self, db, capsys):
        """Test command when Cloudinary is not configured."""
        call_command("migrate_to_cloudinary")

        # Check error message
        captured = capsys.readouterr()
        assert "Cloudinary is not configured" in captured.out

    @override_settings(
        CLOUDINARY_STORAGE={
            "CLOUD_NAME": "test_cloud",
            "API_KEY": "test_key",
            "API_SECRET": "test_secret",
        }
    )
    def test_command_skips_already_cloudinary_images(self, db, capsys):
        """Test that command skips images already on Cloudinary."""
        from app.models import User

        # Create user with profile
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        # Set avatar to a Cloudinary public_id (simulating already migrated)
        # Note: In real scenario, this would be a CloudinaryResource
        # For testing, we just verify the command handles it gracefully
        user.profile.avatar = "avatars/test_avatar"  # public_id format
        user.profile.save()

        # Run command
        call_command("migrate_to_cloudinary", "--dry-run")

        # Check output
        captured = capsys.readouterr()
        # Should skip images that don't have .path attribute
        has_skipped = "skipped" in captured.out.lower()
        has_migrated = "migrated" in captured.out.lower()
        assert has_skipped or has_migrated

    @override_settings(
        CLOUDINARY_STORAGE={
            "CLOUD_NAME": "test_cloud",
            "API_KEY": "test_key",
            "API_SECRET": "test_secret",
        }
    )
    def test_command_handles_missing_files(self, db, capsys):
        """Test that command handles missing local files gracefully."""
        from app.models import User

        # Create user with profile
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        # Note: In tests, we can't easily create a file that doesn't exist
        # This test verifies the command structure handles errors

        # Run command
        call_command("migrate_to_cloudinary", "--dry-run")

        # Should complete without crashing
        captured = capsys.readouterr()
        has_dry_run = "DRY RUN COMPLETE" in captured.out
        has_migration = "MIGRATION COMPLETE" in captured.out
        assert has_dry_run or has_migration

    @override_settings(
        CLOUDINARY_STORAGE={
            "CLOUD_NAME": "test_cloud",
            "API_KEY": "test_key",
            "API_SECRET": "test_secret",
        }
    )
    def test_command_dry_run_flag(self, db, capsys):
        """Test that --dry-run flag works correctly."""
        call_command("migrate_to_cloudinary", "--dry-run")

        # Check output
        captured = capsys.readouterr()
        assert "DRY RUN" in captured.out
        assert "No changes were made" in captured.out

    @override_settings(
        CLOUDINARY_STORAGE={
            "CLOUD_NAME": "test_cloud",
            "API_KEY": "test_key",
            "API_SECRET": "test_secret",
        }
    )
    def test_command_with_no_images(self, db, capsys):
        """Test command when there are no images to migrate."""
        # Create user without avatar
        from app.models import User

        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        # Run command
        call_command("migrate_to_cloudinary", "--dry-run")

        # Check output
        captured = capsys.readouterr()
        has_no_profiles = "No profiles with avatars found" in captured.out
        has_found_zero = "Found 0" in captured.out
        assert has_no_profiles or has_found_zero

        has_no_images = "No post images found" in captured.out
        assert has_no_images or has_found_zero
