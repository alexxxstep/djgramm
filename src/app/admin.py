"""Admin configuration for DJGramm."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Like, Post, PostImage, Profile, Tag, User


class ProfileInline(admin.StackedInline):
    """Inline for Profile in User admin."""

    model = Profile
    can_delete = False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin for custom User model."""

    list_display = ["email", "username", "is_active", "is_staff"]
    list_filter = ["is_active", "is_staff", "is_email_verified"]
    search_fields = ["email", "username"]
    ordering = ["email"]
    inlines = [ProfileInline]


class PostImageInline(admin.TabularInline):
    """Inline for PostImage in Post admin."""

    model = PostImage
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin for Post model."""

    list_display = ["id", "author", "created_at"]
    list_filter = ["created_at", "tags"]
    search_fields = ["caption", "author__email", "author__username"]
    inlines = [PostImageInline]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin for Tag model."""

    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """Admin for Like model."""

    list_display = ["user", "post", "created_at"]
    list_filter = ["created_at"]
