"""Admin configuration for DJGramm."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Comment, Follow, Like, Post, PostImage, Profile, Tag, User


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

    def delete_model(self, request, obj):
        """Handle user deletion with proper cleanup."""
        try:
            # Clean up OAuth associations before deletion
            if hasattr(obj, "social_auth"):
                obj.social_auth.all().delete()
        except Exception:
            # Ignore errors - CASCADE will handle it
            pass

        # Call parent delete
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """Handle bulk user deletion with proper cleanup."""
        for obj in queryset:
            try:
                # Clean up OAuth associations before deletion
                if hasattr(obj, "social_auth"):
                    obj.social_auth.all().delete()
            except Exception:
                # Ignore errors - CASCADE will handle it
                pass

        # Call parent delete
        super().delete_queryset(request, queryset)


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


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin for Comment model."""

    list_display = ["author", "post", "created_at", "text"]
    list_filter = ["created_at"]
    search_fields = ["text", "author__email", "author__username"]
    ordering = ["created_at"]


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Admin for Follow model."""

    list_display = ["follower", "following", "created_at"]
    list_filter = ["created_at"]
    search_fields = [
        "follower__email",
        "follower__username",
        "following__email",
        "following__username",
    ]
    ordering = ["created_at"]
