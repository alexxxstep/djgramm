"""Management command to migrate existing images to Cloudinary."""

import os

import cloudinary.uploader
from django.conf import settings
from django.core.management.base import BaseCommand

from app.models import PostImage, Profile


class Command(BaseCommand):
    help = "Migrate existing images to Cloudinary"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be migrated without actually migrating",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        # Check if Cloudinary is configured
        cloud_name = settings.CLOUDINARY_STORAGE.get("CLOUD_NAME", "")
        if not cloud_name:
            self.stdout.write(
                self.style.ERROR(
                    "Cloudinary is not configured. "
                    "Please set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, "
                    "and CLOUDINARY_API_SECRET in your .env file."
                )
            )
            return

        msg = f"Cloudinary configured: {cloud_name}"
        self.stdout.write(self.style.SUCCESS(msg))

        if dry_run:
            self.stdout.write(
                self.style.WARNING("\nDRY RUN - No changes will be made\n")
            )

        # Migrate Profile avatars
        self.stdout.write("\n=== Migrating Profile Avatars ===")
        profiles = Profile.objects.exclude(avatar="").exclude(
            avatar__isnull=True
        )
        total_profiles = profiles.count()

        if total_profiles == 0:
            self.stdout.write(
                self.style.WARNING("No profiles with avatars found.")
            )
        else:
            self.stdout.write(f"Found {total_profiles} profiles with avatars")
            migrated_profiles = 0
            skipped_profiles = 0
            error_profiles = 0

            for profile in profiles:
                if not profile.avatar:
                    skipped_profiles += 1
                    continue

                # Get raw value from database to check if it's a public_id
                # or a local file path
                avatar_value = None
                try:
                    # Get the raw value from the field
                    avatar_field = profile._meta.get_field("avatar")
                    raw_value = avatar_field.value_from_object(profile)
                    # Convert to string if it's a CloudinaryResource
                    # or other object
                    if raw_value is not None:
                        if isinstance(raw_value, str):
                            avatar_value = raw_value
                        else:
                            # Try to get public_id if it's CloudinaryResource
                            if hasattr(raw_value, "public_id"):
                                avatar_value = raw_value.public_id
                            else:
                                avatar_value = str(raw_value)
                except Exception:
                    avatar_value = (
                        str(profile.avatar) if profile.avatar else None
                    )

                # Try to find local file
                file_path = None
                try:
                    # First, try to get path directly
                    if hasattr(profile.avatar, "path"):
                        file_path = profile.avatar.path
                    else:
                        # Try to find file by value in media directory
                        if avatar_value:
                            media_root = settings.MEDIA_ROOT
                            # Check if it's a public_id format
                            # (folder/filename)
                            if "/" in avatar_value:
                                folder, filename = avatar_value.split("/", 1)
                                # Try common extensions
                                for ext in [
                                    ".jpg",
                                    ".jpeg",
                                    ".png",
                                    ".gif",
                                    ".webp",
                                ]:
                                    potential_path = os.path.join(
                                        media_root, folder, filename + ext
                                    )
                                    if os.path.exists(potential_path):
                                        file_path = potential_path
                                        break
                            else:
                                # Try in avatars folder
                                for ext in [
                                    ".jpg",
                                    ".jpeg",
                                    ".png",
                                    ".gif",
                                    ".webp",
                                ]:
                                    potential_path = os.path.join(
                                        media_root,
                                        "avatars",
                                        avatar_value + ext,
                                    )
                                    if os.path.exists(potential_path):
                                        file_path = potential_path
                                        break
                                # Also try without extension
                                # (in case it's already in filename)
                                potential_path = os.path.join(
                                    media_root, "avatars", avatar_value
                                )
                                if os.path.exists(potential_path):
                                    file_path = potential_path
                                    if dry_run:
                                        self.stdout.write(
                                            f"    Found file: {potential_path}"
                                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  Profile {profile.user.username}: "
                            f"Error finding file: {e}"
                        )
                    )  # noqa: E501

                if not file_path or not os.path.exists(file_path):
                    self.stdout.write(
                        self.style.WARNING(
                            f"  Profile {profile.user.username}: "
                            f"Local file not found, skipping"
                        )
                    )  # noqa: E501
                    skipped_profiles += 1
                    continue

                try:
                    if dry_run:
                        self.stdout.write(
                            f"  Would migrate: {profile.user.username} "
                            f"({file_path})"
                        )
                    else:
                        # Upload to Cloudinary
                        result = cloudinary.uploader.upload(
                            file_path,
                            folder="avatars",
                            resource_type="image",
                        )
                        profile.avatar = result["public_id"]
                        profile.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"  ✓ Migrated: {profile.user.username}"
                            )
                        )
                    migrated_profiles += 1

                except Exception as e:
                    error_profiles += 1
                    username = profile.user.username
                    self.stdout.write(
                        self.style.ERROR(
                            f"  ✗ Error migrating {username}: {e}"
                        )
                    )

                total_processed = (
                    migrated_profiles + skipped_profiles + error_profiles
                )
                if total_processed % 10 == 0:
                    msg = f"  Progress: {total_processed}/{total_profiles}..."
                    self.stdout.write(msg)

            self.stdout.write(
                f"\nProfiles: {migrated_profiles} migrated, "
                f"{skipped_profiles} skipped, {error_profiles} errors"
            )

        # Migrate PostImage
        self.stdout.write("\n=== Migrating Post Images ===")
        post_images = PostImage.objects.exclude(image="").exclude(
            image__isnull=True
        )
        total_images = post_images.count()

        if total_images == 0:
            self.stdout.write(self.style.WARNING("No post images found."))
        else:
            self.stdout.write(f"Found {total_images} post images")
            migrated_images = 0
            skipped_images = 0
            error_images = 0

            for post_image in post_images:
                if not post_image.image:
                    skipped_images += 1
                    continue

                # Get raw value from database to check if it's
                # a public_id or a local file path
                image_value = None
                try:
                    # Get the raw value from the field
                    image_field = post_image._meta.get_field("image")
                    raw_value = image_field.value_from_object(post_image)
                    # Convert to string if it's a CloudinaryResource
                    # or other object
                    if raw_value is not None:
                        if isinstance(raw_value, str):
                            image_value = raw_value
                        else:
                            # Try to get public_id if it's CloudinaryResource
                            if hasattr(raw_value, "public_id"):
                                image_value = raw_value.public_id
                            else:
                                image_value = str(raw_value)
                except Exception:
                    image_value = (
                        str(post_image.image) if post_image.image else None
                    )

                # Try to find local file
                file_path = None
                try:
                    # First, try to get path directly
                    if hasattr(post_image.image, "path"):
                        file_path = post_image.image.path
                    else:
                        # Try to find file by value in media directory
                        if image_value:
                            media_root = settings.MEDIA_ROOT
                            # Check if it's a public_id format
                            # (folder/filename)
                            if "/" in image_value:
                                folder, filename = image_value.split("/", 1)
                                # Try common extensions
                                for ext in [
                                    ".jpg",
                                    ".jpeg",
                                    ".png",
                                    ".gif",
                                    ".webp",
                                ]:
                                    potential_path = os.path.join(
                                        media_root, folder, filename + ext
                                    )
                                    if os.path.exists(potential_path):
                                        file_path = potential_path
                                        break
                            else:
                                # Try in posts folder
                                for ext in [
                                    ".jpg",
                                    ".jpeg",
                                    ".png",
                                    ".gif",
                                    ".webp",
                                ]:
                                    potential_path = os.path.join(
                                        media_root, "posts", image_value + ext
                                    )
                                    if os.path.exists(potential_path):
                                        file_path = potential_path
                                        break
                                # Also try without extension
                                # (in case it's already in filename)
                                potential_path = os.path.join(
                                    media_root, "posts", image_value
                                )
                                if os.path.exists(potential_path):
                                    file_path = potential_path
                                    if dry_run:
                                        self.stdout.write(
                                            f"    Found file: {potential_path}"
                                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  PostImage #{post_image.id}: "
                            f"Error finding file: {e}"
                        )
                    )

                if not file_path or not os.path.exists(file_path):
                    self.stdout.write(
                        self.style.WARNING(
                            f"  PostImage #{post_image.id}: "
                            f"Local file not found, skipping"
                        )
                    )
                    skipped_images += 1
                    continue

                try:
                    if dry_run:
                        self.stdout.write(
                            f"  Would migrate: PostImage #{post_image.id} "
                            f"({file_path})"
                        )
                    else:
                        # Upload to Cloudinary
                        result = cloudinary.uploader.upload(
                            file_path,
                            folder="posts",
                            resource_type="image",
                        )
                        post_image.image = result["public_id"]
                        post_image.save()
                        msg = f"  ✓ Migrated: PostImage #{post_image.id}"
                        self.stdout.write(self.style.SUCCESS(msg))
                    migrated_images += 1

                except Exception as e:
                    error_images += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f"  ✗ Error migrating "
                            f"PostImage #{post_image.id}: {e}"
                        )
                    )

                total_processed = (
                    migrated_images + skipped_images + error_images
                )
                if total_processed % 10 == 0:
                    msg = f"  Progress: {total_processed}/{total_images}..."
                    self.stdout.write(msg)

            self.stdout.write(
                f"\nPost Images: {migrated_images} migrated, "
                f"{skipped_images} skipped, {error_images} errors"
            )

        # Summary
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\n=== DRY RUN COMPLETE ==="
                    "\nNo changes were made. Run without --dry-run to migrate."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "\n=== MIGRATION COMPLETE ==="
                    "\nAll images have been migrated to Cloudinary."
                )
            )
