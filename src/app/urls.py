"""URL patterns for DJGramm app."""

from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    # Feed
    path("", views.FeedView.as_view(), name="feed"),
    # Authentication
    path("register/", views.RegisterView.as_view(), name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    # Profile (edit MUST be before <username> pattern!)
    path("profile/edit/", views.ProfileEditView.as_view(), name="profile_edit"),
    path("profile/<str:username>/", views.ProfileView.as_view(), name="profile"),
    # Posts
    path("post/new/", views.PostCreateView.as_view(), name="post_create"),
    path("post/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("post/<int:pk>/edit/", views.PostUpdateView.as_view(), name="post_update"),
    path("post/<int:pk>/delete/", views.PostDeleteView.as_view(), name="post_delete"),
    path("post/<int:pk>/like/", views.toggle_like, name="toggle_like"),
    # Tags
    path("tag/<slug:slug>/", views.TagPostsView.as_view(), name="tag_posts"),
]
