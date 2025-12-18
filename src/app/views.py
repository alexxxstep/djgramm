"""Views for DJGramm."""

import json
import logging

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import (
    CommentForm,
    PostForm,
    PostImageFormSet,
    ProfileForm,
    RegistrationForm,
)
from .models import Comment, Follow, Like, Post, PostImage, Profile, Tag, User
from .services import sync_post_tags

# =============================================================================
# Feed
# =============================================================================


class FeedView(ListView):
    """Display feed of posts."""

    model = Post
    template_name = "app/feed.html"
    context_object_name = "posts"
    paginate_by = 12

    def get_queryset(self):
        """Show all posts with optimized queries."""
        from django.db.models import Prefetch

        return Post.objects.select_related(
            "author", "author__profile"
        ).prefetch_related(
            Prefetch(
                "images",
                queryset=PostImage.objects.order_by("order"),
            ),
            "tags",
            "likes",
            "comments",
        )

    def get_context_data(self, **kwargs):
        """Add user's liked posts and following status to context."""
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # Get IDs of posts liked by current user
            context["user_liked_posts"] = set(
                Like.objects.filter(user=self.request.user).values_list(
                    "post_id", flat=True
                )
            )
            # Get IDs of users that current user follows
            # (for Follow/Unfollow buttons)
            context["user_following_ids"] = set(
                self.request.user.following.values_list("id", flat=True)
            )
            # Get following count for empty feed message
            context["following_count"] = (
                self.request.user.get_following_count()
            )
        else:
            context["user_liked_posts"] = set()
            context["user_following_ids"] = set()
            context["following_count"] = 0
        return context


class NewsFeedView(ListView):
    """Display news feed - posts only from followed users."""

    model = Post
    template_name = "app/feed.html"
    context_object_name = "posts"
    paginate_by = 12

    def dispatch(self, request, *args, **kwargs):
        """Update last_news_feed_visit timestamp on visit."""
        response = super().dispatch(request, *args, **kwargs)
        if request.user.is_authenticated and hasattr(request.user, "profile"):
            request.user.profile.last_news_feed_visit = timezone.now()
            request.user.profile.save(update_fields=["last_news_feed_visit"])
        return response

    def get_queryset(self):
        """Show posts only from users being followed."""
        if not self.request.user.is_authenticated:
            return Post.objects.none()

        # Get users that current user follows (ManyToManyField)
        following_users = self.request.user.following.all()

        # Include own posts
        following_ids = list(following_users.values_list("id", flat=True))
        following_ids.append(self.request.user.id)

        from django.db.models import Prefetch

        return (
            Post.objects.filter(author_id__in=following_ids)
            .select_related("author", "author__profile")
            .prefetch_related(
                Prefetch(
                    "images",
                    queryset=PostImage.objects.order_by("order"),
                ),
                "tags",
                "likes",
                "comments",
            )
        )

    def get_context_data(self, **kwargs):
        """Add context for news feed."""
        context = super().get_context_data(**kwargs)
        context["is_news_feed"] = True

        if self.request.user.is_authenticated:
            # Get IDs of posts liked by current user
            context["user_liked_posts"] = set(
                Like.objects.filter(user=self.request.user).values_list(
                    "post_id", flat=True
                )
            )
            # Get IDs of users that current user follows
            context["user_following_ids"] = set(
                self.request.user.following.values_list("id", flat=True)
            )
            # Get following count for empty feed message
            context["following_count"] = (
                self.request.user.get_following_count()
            )
        else:
            context["user_liked_posts"] = set()
            context["user_following_ids"] = set()
            context["following_count"] = 0
        return context


# =============================================================================
# Authentication
# =============================================================================


class RegisterView(CreateView):
    """User registration view."""

    form_class = RegistrationForm
    template_name = "registration/register.html"
    success_url = "/"

    def form_valid(self, form):
        """Log in user after registration."""
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f"Welcome, {user.username}!")
        return redirect(self.success_url)


# =============================================================================
# Profile
# =============================================================================


class ProfileView(DetailView):
    """Display user profile."""

    model = User
    template_name = "app/profile.html"
    context_object_name = "profile_user"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        """Add user posts to context."""
        context = super().get_context_data(**kwargs)
        from django.db.models import Prefetch

        context["posts"] = (
            self.object.posts.select_related("author")
            .prefetch_related(
                Prefetch(
                    "images",
                    queryset=PostImage.objects.order_by("order"),
                )
            )
            .order_by("-created_at")
        )
        context["posts_count"] = context["posts"].count()

        context["followers_count"] = self.object.get_followers_count()
        context["following_count"] = self.object.get_following_count()

        # Check if current user is following target user
        if self.request.user.is_authenticated:
            context["is_following"] = self.request.user.is_following(
                self.object
            )
        else:
            context["is_following"] = False

        return context


class FollowersListView(ListView):
    """Display list of users who follow the target user."""

    model = Follow
    template_name = "app/followers_list.html"
    context_object_name = "follows"  # List of Follow objects
    paginate_by = 20

    def get_queryset(self):
        """
        Get Follow objects where target_user is being followed.
        Optimized with select_related to avoid N+1 queries.
        """
        # Get target user from URL
        self.target_user = get_object_or_404(
          User,
          username=self.kwargs["username"]
        )  # fmt: skip

        # Return Follow objects with optimized queries
        return (
            Follow.objects.filter(following=self.target_user)
            .select_related("follower", "follower__profile")
            .order_by("-created_at")  # Newest followers first
        )

    def get_context_data(self, **kwargs):
        """
        Add target_user and user's following status to context.
        user_following_ids: set of user IDs that current user follows
        (used in template to show Follow/Unfollow buttons).
        """
        context = super().get_context_data(**kwargs)
        context["target_user"] = self.target_user

        # Get IDs of users that current user follows
        # (for Follow/Unfollow buttons)
        if self.request.user.is_authenticated:
            context["user_following_ids"] = set(
                self.request.user.following.values_list("id", flat=True)
            )
        else:
            context["user_following_ids"] = set()

        return context


class FollowingListView(ListView):
    """Display list of users that the target user follows."""

    model = Follow
    template_name = "app/following_list.html"
    context_object_name = "follows"  # List of Follow objects
    paginate_by = 20

    def get_queryset(self):
        """
        Get Follow objects where target_user is the follower.
        Optimized with select_related to avoid N+1 queries.
        """
        # Get target user from URL
        self.target_user = get_object_or_404(
            User, username=self.kwargs["username"]
        )

        # Return Follow objects with optimized queries
        return (
            Follow.objects.filter(follower=self.target_user)
            .select_related("following", "following__profile")
            .order_by("-created_at")  # Newest follows first
        )

    def get_context_data(self, **kwargs):
        """
        Add target_user and user's following status to context.
        user_following_ids: set of user IDs that current user follows
        (used in template to show Follow/Unfollow buttons).
        """
        context = super().get_context_data(**kwargs)
        context["target_user"] = self.target_user

        # Get IDs of users that current user follows
        # (for Follow/Unfollow buttons)
        if self.request.user.is_authenticated:
            context["user_following_ids"] = set(
                self.request.user.following.values_list("id", flat=True)
            )
        else:
            context["user_following_ids"] = set()

        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Edit user profile."""

    model = Profile
    form_class = ProfileForm
    template_name = "app/profile_edit.html"
    success_url = "/"

    def get_object(self, queryset=None):
        """Get current user's profile."""
        return self.request.user.profile

    def get_success_url(self):
        """Redirect to user profile after edit."""
        return f"/profile/{self.request.user.username}/"

    def form_valid(self, form):
        """Show success message."""
        messages.success(self.request, "Profile updated successfully!")
        return super().form_valid(form)


# =============================================================================
# Posts
# =============================================================================


class PostDetailView(DetailView):
    """Display single post."""

    model = Post
    template_name = "app/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        """Optimize query."""
        from django.db.models import Prefetch

        return Post.objects.select_related("author").prefetch_related(
            Prefetch(
                "images",
                queryset=PostImage.objects.order_by("order"),
            ),
            "tags",
            "likes",
            "comments__author",
        )

    def get_context_data(self, **kwargs):
        """Add like status, comments and comment form to context."""
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["user_liked"] = self.object.likes.filter(
                user=self.request.user
            ).exists()
            context["comment_form"] = CommentForm()
        else:
            context["user_liked"] = False
        context["comments"] = self.object.comments.select_related("author")
        context["likes_count"] = self.object.likes.count()
        # Ensure images are ordered correctly
        context["images"] = self.object.images.order_by("order")
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Create new post with images."""

    model = Post
    form_class = PostForm
    template_name = "app/post_form.html"

    def get_context_data(self, **kwargs):
        """Add image formset to context."""
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["image_formset"] = PostImageFormSet(
                self.request.POST, self.request.FILES
            )
        else:
            context["image_formset"] = PostImageFormSet()
        return context

    def form_valid(self, form):
        """Save post and images, sync tags."""
        logger = logging.getLogger(__name__)

        # Rebuild formset with POST and FILES data
        image_formset = PostImageFormSet(self.request.POST, self.request.FILES)

        form.instance.author = self.request.user
        self.object = form.save()

        # Sync tags from caption
        sync_post_tags(self.object, form.cleaned_data["caption"])

        # Log formset state for debugging
        logger.info(
            f"Post {self.object.pk}: Formset total forms: {image_formset.total_form_count()}"
        )
        logger.info(
            f"Post {self.object.pk}: Files in request.FILES: {list(self.request.FILES.keys())}"
        )
        for key in self.request.FILES.keys():
            file = self.request.FILES[key]
            logger.info(
                f"Post {self.object.pk}: File '{key}': {file.name}, size: {file.size}"
            )

        # Set instance before validation
        image_formset.instance = self.object

        # Validate and save image formset
        if image_formset.is_valid():
            saved_instances = image_formset.save(commit=False)
            # Set order for each image based on form position
            for index, img in enumerate(saved_instances):
                img.order = index
                img.save()
            logger.info(
                f"Post {self.object.pk}: Saved {len(saved_instances)} image instances"
            )
            for img in saved_instances:
                logger.info(
                    f"Post {self.object.pk}: Saved image {img.pk} - order {img.order} - {img.image}"
                )
                if hasattr(img.image, "url"):
                    logger.info(
                        f"Post {self.object.pk}: Image URL: {img.image.url}"
                    )
        else:
            # If formset is invalid, show errors
            logger.error(
                f"Post {self.object.pk}: Formset errors: {image_formset.errors}"
            )
            logger.error(
                f"Post {self.object.pk}: Formset non_form_errors: {image_formset.non_form_errors()}"
            )
            for error_dict in image_formset.errors:
                for _field, errors in error_dict.items():
                    for error in errors:
                        messages.error(self.request, f"Image error: {error}")

        messages.success(self.request, "Post created successfully!")
        return redirect(self.object.get_absolute_url())


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Edit existing post."""

    model = Post
    form_class = PostForm
    template_name = "app/post_form.html"

    def test_func(self):
        """Check if user is post author."""
        post = self.get_object()
        return self.request.user == post.author

    def get_context_data(self, **kwargs):
        """Add image formset to context."""
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["image_formset"] = PostImageFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )
        else:
            context["image_formset"] = PostImageFormSet(instance=self.object)
        context["is_edit"] = True
        return context

    def form_valid(self, form):
        """Save post and images, sync tags."""
        context = self.get_context_data()
        image_formset = context["image_formset"]

        self.object = form.save()

        # Sync tags from caption
        sync_post_tags(self.object, form.cleaned_data["caption"])

        # Validate and save image formset
        if image_formset.is_valid():
            saved_instances = image_formset.save(commit=False)
            # Set order for each image based on form position
            for index, img in enumerate(saved_instances):
                img.order = index
                img.save()
        else:
            # If formset is invalid, show errors
            for error_dict in image_formset.errors:
                for _field, errors in error_dict.items():
                    for error in errors:
                        messages.error(self.request, f"Image error: {error}")

        messages.success(self.request, "Post updated successfully!")
        return redirect(self.object.get_absolute_url())


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete post."""

    model = Post
    template_name = "app/post_confirm_delete.html"
    success_url = "/"

    def test_func(self):
        """Check if user is post author."""
        post = self.get_object()
        return self.request.user == post.author

    def delete(self, request, *args, **kwargs):
        """Show success message on delete."""
        messages.success(request, "Post deleted successfully!")
        return super().delete(request, *args, **kwargs)


# =============================================================================
# Likes (AJAX)
# =============================================================================


@login_required
def toggle_like(request, pk):
    """Toggle like on a post (AJAX endpoint)."""
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    from django.db import IntegrityError

    post = get_object_or_404(Post, pk=pk)

    # Check if like already exists
    try:
        like = Like.objects.get(user=request.user, post=post)
        # Like exists, remove it
        like.delete()
        liked = False
    except Like.DoesNotExist:
        # Like doesn't exist, create it
        try:
            Like.objects.create(user=request.user, post=post)
            liked = True
        except IntegrityError:
            # Race condition: like was created by another request
            # Try to get it again
            try:
                like = Like.objects.get(user=request.user, post=post)
                liked = True
            except Like.DoesNotExist:
                # Still doesn't exist, something went wrong
                liked = False

    return JsonResponse(
        {
            "liked": liked,
            "likes_count": post.likes.count(),
        }
    )


@login_required
def toggle_follow(request, username):
    """Toggle follow on a user (AJAX endpoint)."""
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    target_user = get_object_or_404(User, username=username)

    if request.user == target_user:
        return JsonResponse(
            {"error": "You cannot follow yourself"}, status=400
        )

    # ManyToManyField approach - simpler and more efficient
    if request.user.following.filter(id=target_user.id).exists():
        request.user.following.remove(target_user)
        is_following = False
    else:
        request.user.following.add(target_user)
        is_following = True

    return JsonResponse(
        {
            "is_following": is_following,
            "followers_count": target_user.get_followers_count(),
            "following_count": request.user.get_following_count(),
        }
    )


# =============================================================================
# Comments (AJAX)
# =============================================================================


@login_required
def add_comment(request, pk):
    """Add comment to a post (AJAX endpoint)."""
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    post = get_object_or_404(Post, pk=pk)

    try:
        data = json.loads(request.body)
        text = data.get("text", "").strip()

        if not text:
            return JsonResponse(
                {"error": "Comment cannot be empty"}, status=400
            )

        if len(text) > 500:
            return JsonResponse({"error": "Comment too long"}, status=400)

        comment = Comment.objects.create(
            author=request.user,
            post=post,
            text=text,
        )

        created_at = comment.created_at.strftime("%b %d, %Y %H:%M")
        avatar_url = None
        if comment.author.profile.avatar:
            avatar_url = comment.author.profile.avatar.url

        return JsonResponse(
            {
                "success": True,
                "comment": {
                    "id": comment.pk,
                    "author": comment.author.username,
                    "author_avatar": avatar_url,
                    "text": comment.text,
                    "created_at": created_at,
                },
                "comments_count": post.comments.count(),
            }
        )
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({"error": "Invalid data"}, status=400)


# =============================================================================
# Health Check
# =============================================================================


def health_check(request):
    """Simple health check endpoint for Docker healthcheck."""
    from django.http import HttpResponse

    return HttpResponse("OK", content_type="text/plain")


@login_required
def delete_comment(request, pk, comment_pk):
    """Delete a comment (AJAX endpoint)."""
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    comment = get_object_or_404(Comment, pk=comment_pk, post_id=pk)

    # Only comment author can delete
    if request.user != comment.author:
        return JsonResponse({"error": "Permission denied"}, status=403)

    comment.delete()
    post = get_object_or_404(Post, pk=pk)

    return JsonResponse(
        {
            "success": True,
            "comments_count": post.comments.count(),
        }
    )


@login_required
def edit_comment(request, pk, comment_pk):
    """Edit a comment (AJAX endpoint)."""
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    comment = get_object_or_404(Comment, pk=comment_pk, post_id=pk)

    # Only comment author can edit
    if request.user != comment.author:
        return JsonResponse({"error": "Permission denied"}, status=403)

    try:
        data = json.loads(request.body)
        text = data.get("text", "").strip()

        if not text:
            return JsonResponse(
                {"error": "Comment cannot be empty"}, status=400
            )

        if len(text) > 500:
            return JsonResponse({"error": "Comment too long"}, status=400)

        comment.text = text
        comment.save()

        return JsonResponse(
            {
                "success": True,
                "text": comment.text,
            }
        )
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({"error": "Invalid data"}, status=400)


# =============================================================================
# Image Order (AJAX)
# =============================================================================


@login_required
def update_image_order(request, pk):
    """Update image order for a post (AJAX endpoint)."""
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    post = get_object_or_404(Post, pk=pk)

    # Check ownership
    if request.user != post.author:
        return JsonResponse({"error": "Permission denied"}, status=403)

    try:
        data = json.loads(request.body)
        order_list = data.get("order", [])

        # Update order for each image
        for index, image_id in enumerate(order_list):
            PostImage.objects.filter(pk=image_id, post=post).update(
                order=index
            )

        return JsonResponse({"success": True})
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({"error": "Invalid data"}, status=400)


# =============================================================================
# Tags
# =============================================================================


class TagPostsView(ListView):
    """Display posts by tag."""

    model = Post
    template_name = "app/tag_posts.html"
    context_object_name = "posts"
    paginate_by = 12

    def get_queryset(self):
        """Filter posts by tag."""
        from django.db.models import Prefetch

        self.tag = get_object_or_404(Tag, slug=self.kwargs["slug"])
        return (
            Post.objects.filter(tags=self.tag)
            .select_related("author")
            .prefetch_related(
                Prefetch(
                    "images",
                    queryset=PostImage.objects.order_by("order"),
                ),
                "likes",
            )
        )

    def get_context_data(self, **kwargs):
        """Add tag to context."""
        context = super().get_context_data(**kwargs)
        context["tag"] = self.tag
        return context
