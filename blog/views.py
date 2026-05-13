from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CommentForm, PostForm
from .models import Category, Post


class PostListView(ListView):
    """Lista de publicaciones publicadas con paginación."""
    model               = Post
    template_name       = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by         = 5

    def get_queryset(self):
        # select_related previene N+1 al acceder a post.author / post.category
        return (
            Post.objects.filter(published=True)
            .select_related("author", "category")
            .prefetch_related("comments__author")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        # super() es OBLIGATORIO — preserva page_obj, paginator, etc.
        ctx = super().get_context_data(**kwargs)
        ctx["categorias"]       = Category.objects.all()
        ctx["total_publicados"] = self.get_queryset().count()
        return ctx


class PostDetailView(DetailView):
    """Detalle de una publicación con sus comentarios."""
    model               = Post
    template_name       = "blog/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return Post.objects.select_related("author", "category").prefetch_related(
            "comments__author", "tags"
        )

    def get_context_data(self, **kwargs):
        ctx              = super().get_context_data(**kwargs)
        ctx["comment_form"] = CommentForm()
        return ctx

    def post(self, request, *args, **kwargs):
        """Procesa el formulario de comentario."""
        post = self.get_object()
        form = CommentForm(data=request.POST)
        if form.is_valid():
            comment        = form.save(commit=False)
            comment.post   = post
            comment.author = request.user
            comment.save()
            messages.success(request, "Comentario agregado.")
            return redirect("blog:post-detail", pk=post.pk)
        ctx = self.get_context_data(object=post)
        ctx["comment_form"] = form
        return self.render_to_response(ctx)


class PostCreateView(CreateView):
    """Crea una nueva publicación."""
    model         = Post
    form_class    = PostForm
    template_name = "blog/post_form.html"
    success_url   = reverse_lazy("blog:post-list")

    def form_valid(self, form):
        # Asigna el autor antes de guardar (POST data no incluye el autor)
        form.instance.author = self.request.user
        messages.success(self.request, "Publicación creada correctamente.")
        return super().form_valid(form)


class PostUpdateView(UpdateView):
    """Edita una publicación existente."""
    model         = Post
    form_class    = PostForm
    template_name = "blog/post_form.html"
    success_url   = reverse_lazy("blog:post-list")

    def form_valid(self, form):
        messages.success(self.request, "Publicación actualizada.")
        return super().form_valid(form)


class PostDeleteView(DeleteView):
    """Confirma y elimina una publicación."""
    model         = Post
    template_name = "blog/post_confirm_delete.html"
    success_url   = reverse_lazy("blog:post-list")

    def form_valid(self, form):
        messages.success(self.request, "Publicación eliminada.")
        return super().form_valid(form)
