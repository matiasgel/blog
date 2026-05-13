from django.urls import path
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
)

app_name = "blog"  # habilita namespace: {% url 'blog:post-list' %}

urlpatterns = [
    # "" coincide con /blog/ (include consume el prefijo)
    path("", PostListView.as_view(), name="post-list"),

    # <int:pk> → Http404 automático si el segmento no es int
    path("posts/<int:pk>/", PostDetailView.as_view(), name="post-detail"),

    path("posts/crear/", PostCreateView.as_view(), name="post-create"),
    path("posts/<int:pk>/editar/", PostUpdateView.as_view(), name="post-update"),
    path("posts/<int:pk>/eliminar/", PostDeleteView.as_view(), name="post-delete"),
]
