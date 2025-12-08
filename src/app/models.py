"""Models for DJGramm."""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    """Custom user model with email authentication."""

    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    def get_followers_count(self):
        "Return number of followers."
        return self.followers.count()

    def get_following_count(self):
        "Return number of users being followed."
        return self.following.count()

    def is_following(self, user):
        "Check if current user follows given user."
        if not user or not isinstance(user, User):
            return False
        return self.following.filter(following=user).exists()


class Profile(models.Model):
    """User profile with additional information."""

    user = models.OneToOneField(  # fmt: skip
        User, on_delete=models.CASCADE, related_name="profile"
    )
    full_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


class Tag(models.Model):
    """Tag for categorizing posts."""

    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("tag_posts", kwargs={"slug": self.slug})


class Post(models.Model):
    """User post with images."""

    author = models.ForeignKey(  # fmt: skip
        User, on_delete=models.CASCADE, related_name="posts"
    )
    caption = models.TextField(max_length=2200, blank=True)
    tags = models.ManyToManyField(Tag, related_name="posts", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Post #{self.pk} by {self.author.username}"

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"pk": self.pk})


class PostImage(models.Model):
    """Image attached to a post."""

    post = models.ForeignKey(  # fmt: skip
        Post, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="posts/")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Image {self.order} for Post #{self.post_id}"


class Like(models.Model):
    """Like on a post."""

    user = models.ForeignKey(  # fmt: skip
        User, on_delete=models.CASCADE, related_name="likes"
    )
    post = models.ForeignKey(  # fmt: skip
        Post, on_delete=models.CASCADE, related_name="likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "post"]

    def __str__(self):
        return f"{self.user.username} likes Post #{self.post_id}"


class Comment(models.Model):
    """Comment on a post."""

    author = models.ForeignKey(  # fmt: skip
        User, on_delete=models.CASCADE, related_name="comments"
    )
    post = models.ForeignKey(  # fmt: skip
        Post, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]  # Chronological order

    def __str__(self):
        return f"Comment by {self.author.username} on Post #{self.post_id}"


class Follow(models.Model):
    """Follow relationship between users."""

    follower = models.ForeignKey(  # fmt: skip
        User, on_delete=models.CASCADE, related_name="following"
    )
    following = models.ForeignKey(  # fmt: skip
        User, on_delete=models.CASCADE, related_name="followers"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["follower", "following"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
