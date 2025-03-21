from django.contrib import admin
from django.urls import path
from . import views
from myapp.views import (
    CreatePostView,
    CommentOnPostView,
    # GetPostsView,
    GetPostWithCommentsView,
    UpdatePostView,
    DeletePostView,
    DeleteCommentView,
)

from myapp.auth import (
    RegisterView,
    LoginView,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.homepage),
    path("about/", views.about),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("posts/", CreatePostView.as_view(), name="create_post"),
    path(
        "posts/<int:post_id>/comment/",
        CommentOnPostView.as_view(),
        name="comment_on_post",
    ),
    # path("posts/all/", GetPostsView.as_view(), name="get_all_posts"),
    path(
        "posts/all/",
        GetPostWithCommentsView.as_view(),
        name="get_post_with_comments",
    ),
    path("posts/<int:pk>/update/", UpdatePostView.as_view(), name="update_post"),
    path("posts/<int:pk>/delete/", DeletePostView.as_view(), name="delete_post"),
    path("posts/<int:pk>/", DeleteCommentView.as_view(), name="delete_comment"),
]
