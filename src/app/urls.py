"""URL patterns for DJGramm app."""

from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    # Health check (for Docker healthcheck)
    path("health/", views.health_check, name="health_check"),
    # Feed
    path("", views.FeedView.as_view(), name="feed"),
    path("news/", views.NewsFeedView.as_view(), name="news_feed"),
    # Authentication
    path("register/", views.RegisterView.as_view(), name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    # Profile (edit MUST be before <username> pattern!)
    path(
        "profile/edit/",
        views.ProfileEditView.as_view(),
        name="profile_edit",
    ),
    path(
        "profile/<str:username>/",
        views.ProfileView.as_view(),
        name="profile",
    ),
    path(
        "profile/<str:username>/follow/",
        views.toggle_follow,
        name="toggle_follow",
    ),
    path(
        "profile/<str:username>/followers/",
        views.FollowersListView.as_view(),
        name="followers_list",
    ),
    path(
        "profile/<str:username>/following/",
        views.FollowingListView.as_view(),
        name="following_list",
    ),
    # Posts
    path("post/new/", views.PostCreateView.as_view(), name="post_create"),
    path("post/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path(
        "post/<int:pk>/edit/",
        views.PostUpdateView.as_view(),
        name="post_update",
    ),
    path(
        "post/<int:pk>/delete/",
        views.PostDeleteView.as_view(),
        name="post_delete",
    ),
    path("post/<int:pk>/like/", views.toggle_like, name="toggle_like"),
    path(
        "post/<int:pk>/comment/",
        views.add_comment,
        name="add_comment",
    ),
    path(
        "post/<int:pk>/comment/<int:comment_pk>/delete/",
        views.delete_comment,
        name="delete_comment",
    ),
    path(
        "post/<int:pk>/comment/<int:comment_pk>/edit/",
        views.edit_comment,
        name="edit_comment",
    ),
    path(
        "post/<int:pk>/reorder-images/",
        views.update_image_order,
        name="reorder_images",
    ),
    # Tags
    path("tag/<slug:slug>/", views.TagPostsView.as_view(), name="tag_posts"),
    # OAuth
    path(
        "oauth/disconnect/<str:provider>/",
        views.disconnect_oauth,
        name="disconnect_oauth",
    ),
]
