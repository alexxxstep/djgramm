"""Views for DJGramm."""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import PostForm, PostImageFormSet, ProfileForm, RegistrationForm
from .models import Like, Post, Profile, Tag, User

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
        """Optimize query with related objects."""
        return Post.objects.select_related(
            "author", "author__profile"
        ).prefetch_related("images", "tags", "likes")

    def get_context_data(self, **kwargs):
        """Add user's liked posts to context."""
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # Get IDs of posts liked by current user
            context["user_liked_posts"] = set(
                Like.objects.filter(user=self.request.user).values_list(
                    "post_id", flat=True
                )
            )
        else:
            context["user_liked_posts"] = set()
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
        context["posts"] = (
            self.object.posts.select_related("author")
            .prefetch_related("images")
            .order_by("-created_at")
        )
        context["posts_count"] = context["posts"].count()
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
        return Post.objects.select_related("author").prefetch_related(
            "images", "tags", "likes"
        )

    def get_context_data(self, **kwargs):
        """Add like status to context."""
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["user_liked"] = self.object.likes.filter(
                user=self.request.user
            ).exists()
        else:
            context["user_liked"] = False
        context["likes_count"] = self.object.likes.count()
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
        """Save post and images."""
        context = self.get_context_data()
        image_formset = context["image_formset"]

        form.instance.author = self.request.user
        self.object = form.save()

        if image_formset.is_valid():
            image_formset.instance = self.object
            image_formset.save()

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
        """Save post and images."""
        context = self.get_context_data()
        image_formset = context["image_formset"]

        self.object = form.save()

        if image_formset.is_valid():
            image_formset.save()

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

    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse(
        {
            "liked": liked,
            "likes_count": post.likes.count(),
        }
    )


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
        self.tag = get_object_or_404(Tag, slug=self.kwargs["slug"])
        return (
            Post.objects.filter(tags=self.tag)
            .select_related("author")
            .prefetch_related("images", "likes")
        )

    def get_context_data(self, **kwargs):
        """Add tag to context."""
        context = super().get_context_data(**kwargs)
        context["tag"] = self.tag
        return context
