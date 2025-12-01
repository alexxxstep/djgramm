#!/usr/bin/env python
"""
Seed data script for DJGramm.

Usage:
    cd src && python manage.py shell < ../scripts/seed_data.py

Or run as management command:
    cd src && python manage.py runscript seed_data
"""

import os
import random
import sys
from io import BytesIO
from pathlib import Path

import django

# Setup Django
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.core.files.base import ContentFile
from PIL import Image

from app.models import Like, Post, PostImage, Tag, User


def create_placeholder_image(width=800, height=800, color=None):
    """Create a placeholder image."""
    if color is None:
        color = (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255),
        )
    img = Image.new("RGB", (width, height), color=color)
    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    buffer.seek(0)
    return ContentFile(buffer.getvalue())


def seed_tags(count=10):
    """Create tags."""
    print(f"Creating {count} tags...")
    tag_names = [
        "photography",
        "travel",
        "food",
        "nature",
        "art",
        "music",
        "fashion",
        "fitness",
        "tech",
        "pets",
        "sunset",
        "coffee",
        "books",
        "design",
        "lifestyle",
    ]
    tags = []
    for name in tag_names[:count]:
        tag, created = Tag.objects.get_or_create(
            name=name,
            defaults={"slug": name.lower().replace(" ", "-")},
        )
        tags.append(tag)
        if created:
            print(f"  Created tag: #{name}")
    return tags


def seed_users(count=20):
    """Create users with profiles."""
    print(f"Creating {count} users...")
    users = []

    # Create admin if not exists
    admin, created = User.objects.get_or_create(
        username="admin",
        defaults={
            "email": "admin@djgramm.net",
            "is_staff": True,
            "is_superuser": True,
        },
    )
    if created:
        admin.set_password("admin")
        admin.save()
        print("  Created admin user (admin/admin)")
    users.append(admin)

    # Create regular users
    for i in range(1, count):
        username = f"user{i}"
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": f"{username}@example.com",
            },
        )
        if created:
            user.set_password("testpass123")
            user.save()
            # Update profile
            user.profile.full_name = f"User {i} Name"
            user.profile.bio = f"Hello! I'm user {i}. I love sharing photos on DJGramm!"
            user.profile.save()
            print(f"  Created user: {username}")
        users.append(user)

    return users


def seed_posts(users, tags, count=100):
    """Create posts with images."""
    print(f"Creating {count} posts...")
    posts = []
    captions = [
        "Beautiful day!",
        "Living my best life",
        "Can't stop, won't stop",
        "Adventure awaits",
        "Coffee first",
        "Weekend vibes",
        "Grateful for this moment",
        "New beginnings",
        "Dream big, work hard",
        "Making memories",
        "Love this view!",
        "Good food, good mood",
        "Exploring new places",
        "Perfect sunset",
        "Simple pleasures",
    ]

    for i in range(count):
        author = random.choice(users)
        post = Post.objects.create(
            author=author,
            caption=random.choice(captions) + f" #{i+1}",
        )

        # Add 1-3 random tags
        post_tags = random.sample(tags, min(random.randint(1, 3), len(tags)))
        post.tags.set(post_tags)

        # Add 1-2 images
        num_images = random.randint(1, 2)
        for j in range(num_images):
            img_content = create_placeholder_image()
            post_image = PostImage(post=post, order=j)
            post_image.image.save(f"post_{post.pk}_{j}.jpg", img_content)
            post_image.save()

        posts.append(post)
        if (i + 1) % 20 == 0:
            print(f"  Created {i + 1} posts...")

    return posts


def seed_likes(users, posts, count=500):
    """Create random likes."""
    print(f"Creating ~{count} likes...")
    likes_created = 0

    for _ in range(count):
        user = random.choice(users)
        post = random.choice(posts)

        like, created = Like.objects.get_or_create(user=user, post=post)
        if created:
            likes_created += 1

    print(f"  Created {likes_created} likes")
    return likes_created


def main():
    """Run all seed functions."""
    print("\n" + "=" * 50)
    print("Seeding DJGramm database...")
    print("=" * 50 + "\n")

    # Clear existing data (optional, comment out if you want to keep data)
    # print("Clearing existing data...")
    # Like.objects.all().delete()
    # PostImage.objects.all().delete()
    # Post.objects.all().delete()
    # Tag.objects.all().delete()
    # User.objects.filter(is_superuser=False).delete()

    tags = seed_tags(10)
    users = seed_users(20)
    posts = seed_posts(users, tags, 100)
    seed_likes(users, posts, 500)

    print("\n" + "=" * 50)
    print("Seeding complete!")
    print("=" * 50)
    print("\nSummary:")
    print(f"  - Users: {User.objects.count()}")
    print(f"  - Tags: {Tag.objects.count()}")
    print(f"  - Posts: {Post.objects.count()}")
    print(f"  - Images: {PostImage.objects.count()}")
    print(f"  - Likes: {Like.objects.count()}")
    print("\nAdmin login: admin@djgramm.net / admin")
    print("Test users: user1@example.com ... user19@example.com / testpass123")


if __name__ == "__main__":
    main()
