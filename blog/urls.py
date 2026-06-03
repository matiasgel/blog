from django.urls import path
from django.contrib.auth import urls as auth_urls
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    RatePostView,
    FotosCarouselView,
)

app_name = "blog"

urlpatterns = [
    path("", PostListView.as_view(), name="post-list"),
    path("fotos/", FotosCarouselView.as_view(), name="fotos-carousel"),
    path("posts/<int:pk>/", PostDetailView.as_view(), name="post-detail"),
    path("posts/crear/", PostCreateView.as_view(), name="post-create"),
    path("posts/<int:pk>/editar/", PostUpdateView.as_view(), name="post-update"),
    path("posts/<int:pk>/eliminar/", PostDeleteView.as_view(), name="post-delete"),
    path("posts/<int:pk>/votar/", RatePostView.as_view(), name="post-rate"),
]