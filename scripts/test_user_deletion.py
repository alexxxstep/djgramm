#!/usr/bin/env python
"""Script to test user deletion with Follow relationships."""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django  # noqa: E402

django.setup()

from app.models import Follow, User  # noqa: E402


def main():
    """Create test users with relationships and test deletion."""
    print("\n" + "=" * 60)
    print("Testing User Deletion with Follow Relationships")
    print("=" * 60 + "\n")

    # Clean up existing test users first
    print("0. Cleaning up existing test users...")
    User.objects.filter(
        email__in=[
            "test_delete_1@example.com",
            "test_delete_2@example.com",
            "test_delete_3@example.com",
        ]
    ).delete()
    print("   [+] Cleanup complete\n")

    # Create test users
    print("1. Creating test users...")
    test_user1 = User.objects.create_user(
        username="test_delete_1",
        email="test_delete_1@example.com",
        password="testpass123",
    )
    test_user2 = User.objects.create_user(
        username="test_delete_2",
        email="test_delete_2@example.com",
        password="testpass123",
    )
    test_user3 = User.objects.create_user(
        username="test_delete_3",
        email="test_delete_3@example.com",
        password="testpass123",
    )
    print(f"   [+] Created {test_user1.email}")
    print(f"   [+] Created {test_user2.email}")
    print(f"   [+] Created {test_user3.email}")

    # Create Follow relationships
    print("\n2. Creating Follow relationships...")
    test_user1.following.add(test_user2, test_user3)
    test_user2.following.add(test_user1)
    test_user3.following.add(test_user1, test_user2)
    print(
        f"   [+] {test_user1.username} follows: {test_user1.following.count()}"
    )
    print(
        f"   [+] {test_user2.username} follows: {test_user2.following.count()}"
    )
    print(
        f"   [+] {test_user3.username} follows: {test_user3.following.count()}"
    )
    print(f"   [+] Total Follow objects: {Follow.objects.count()}")

    # Display relationships
    print("\n3. Current relationships:")
    for follow in Follow.objects.all():
        print(
            f"   - {follow.follower.username} -> {follow.following.username}"
        )

    # Test deletion
    print(f"\n4. Deleting user: {test_user1.email}...")
    user1_id = test_user1.pk
    test_user1.delete()
    print("   [+] User deleted successfully!")

    # Verify cleanup
    print("\n5. Verifying cleanup:")
    remaining_users = User.objects.filter(
        email__in=[
            "test_delete_1@example.com",
            "test_delete_2@example.com",
            "test_delete_3@example.com",
        ]
    )
    print(f"   [+] Remaining test users: {remaining_users.count()}")

    follow_count = (
        Follow.objects.filter(follower_id=user1_id).count()
        + Follow.objects.filter(following_id=user1_id).count()
    )
    print(f"   [+] Follow objects with deleted user: {follow_count}")

    if follow_count == 0:
        print("\n   [SUCCESS] All Follow relationships cleaned up!")
    else:
        print("\n   [ERROR] Some Follow relationships still exist!")

    # Cleanup remaining test users
    print("\n6. Cleaning up remaining test users...")
    for user in remaining_users:
        print(f"   - Deleting {user.email}...")
        user.delete()
    print("   [+] Cleanup complete!")

    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
