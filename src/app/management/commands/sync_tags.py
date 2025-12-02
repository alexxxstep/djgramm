"""Management command to sync tags from captions for all existing posts."""

from django.core.management.base import BaseCommand

from app.models import Post
from app.services import sync_post_tags


class Command(BaseCommand):
    help = "Sync tags from captions for all existing posts"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be synced without actually syncing",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        posts = Post.objects.filter(caption__icontains="#")
        total = posts.count()

        if total == 0:
            self.stdout.write(
                self.style.WARNING("No posts with hashtags found.")
            )
            return

        self.stdout.write(f"Found {total} posts with hashtags")

        if dry_run:
            self.stdout.write(
                self.style.WARNING("\nDRY RUN - No changes will be made\n")
            )

        synced = 0
        for post in posts:
            if not dry_run:
                sync_post_tags(post, post.caption)
            synced += 1

            if synced % 10 == 0:
                self.stdout.write(f"Processed {synced}/{total} posts...")

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nWould sync tags for {synced} posts"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nSuccessfully synced tags for {synced} posts"
                )
            )

