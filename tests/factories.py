"""Factory Boy factories for DJGramm tests."""

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory, ImageField

from app.models import Follow, Like, Post, PostImage, Profile, Tag

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Factory for User model."""

    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    is_active = True
    is_email_verified = False

    @factory.post_generation
    def profile(self, create, extracted, **kwargs):
        """Profile is auto-created by signal, just update if needed."""
        if not create:
            return
        if extracted:
            # Update profile with provided data
            for key, value in extracted.items():
                setattr(self.profile, key, value)
            self.profile.save()


class ProfileFactory(DjangoModelFactory):
    """Factory for Profile model."""

    class Meta:
        model = Profile

    user = factory.SubFactory(UserFactory)
    full_name = factory.Faker("name")
    bio = factory.Faker("text", max_nb_chars=200)
    # avatar = ImageField(filename="avatar.jpg")  # Uncomment if needed


class TagFactory(DjangoModelFactory):
    """Factory for Tag model."""

    class Meta:
        model = Tag

    name = factory.Sequence(lambda n: f"tag{n}")
    slug = factory.LazyAttribute(lambda obj: obj.name.lower())


class PostFactory(DjangoModelFactory):
    """Factory for Post model."""

    class Meta:
        model = Post

    author = factory.SubFactory(UserFactory)
    caption = factory.Faker("text", max_nb_chars=500)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        """Add tags to post."""
        if not create:
            return
        if extracted:
            for tag in extracted:
                self.tags.add(tag)


class PostImageFactory(DjangoModelFactory):
    """Factory for PostImage model."""

    class Meta:
        model = PostImage

    post = factory.SubFactory(PostFactory)
    image = ImageField(filename="post_image.jpg", color="blue")
    order = factory.Sequence(lambda n: n)


class LikeFactory(DjangoModelFactory):
    """Factory for Like model."""

    class Meta:
        model = Like

    user = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)


class FollowFactory(DjangoModelFactory):
    """Factory for Follow model (intermediate model for ManyToManyField)."""

    class Meta:
        model = Follow

    follower = factory.SubFactory(UserFactory)
    following = factory.SubFactory(UserFactory)
