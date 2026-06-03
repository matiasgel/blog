from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CommentForm, PostForm, RatingForm
from .models import Category, Post, Rating


class PostListView(ListView):
    """Lista de publicaciones publicadas con paginación."""
    model               = Post
    template_name       = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by         = 5

    def get_queryset(self):
        qs = (
            Post.objects.filter(published=True)
            .select_related("author", "category")
            .order_by("-created_at")
        )
        slug = self.request.GET.get("categoria")
        if slug:
            qs = qs.filter(category__slug=slug)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categorias"]        = Category.objects.all()
        ctx["total_publicados"]  = self.get_queryset().count()
        ctx["categoria_activa"]  = self.request.GET.get("categoria", "")
        return ctx


class PostDetailView(DetailView):
    """Detalle de una publicación con sus comentarios y puntaje."""
    model               = Post
    template_name       = "blog/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return Post.objects.select_related("author", "category").prefetch_related(
            "tags"
        )

    def _get_session_key(self, request):
        if not request.session.session_key:
            request.session.create()
        return request.session.session_key

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        post = self.object
        session_key = self._get_session_key(self.request)

        # Solo comentarios aprobados
        ctx["comments"] = post.comments.filter(approved=True).select_related("author")

        # Formulario de comentario (oculta nombre/email si está logueado)
        ctx["comment_form"] = CommentForm(user=self.request.user)

        # Rating: promedio y voto actual del visitante
        agg = post.ratings.aggregate(avg=Avg("value"), count=Count("id"))
        ctx["rating_avg"]   = round(agg["avg"], 1) if agg["avg"] else None
        ctx["rating_count"] = agg["count"]
        ctx["rating_form"]  = RatingForm()
        try:
            ctx["user_rating"] = post.ratings.get(session_key=session_key).value
        except Rating.DoesNotExist:
            ctx["user_rating"] = None

        return ctx

    def post(self, request, *args, **kwargs):
        """Procesa el formulario de comentario."""
        post = self.get_object()
        form = CommentForm(data=request.POST, user=request.user)
        if form.is_valid():
            comment      = form.save(commit=False)
            comment.post = post
            if request.user.is_authenticated:
                comment.author   = request.user
                comment.approved = True
                messages.success(request, "Comentario agregado.")
            else:
                comment.approved = False
                messages.info(
                    request,
                    "Tu comentario fue enviado y está pendiente de aprobación.",
                )
            comment.save()
            return redirect("blog:post-detail", pk=post.pk)
        self.object = post
        ctx = self.get_context_data(object=post)
        ctx["comment_form"] = form
        return self.render_to_response(ctx)


class RatePostView(View):
    """Registra o actualiza el puntaje de una publicación (anónimo o logueado)."""

    def _get_session_key(self, request):
        if not request.session.session_key:
            request.session.create()
        return request.session.session_key

    def _get_ip(self, request):
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk, published=True)
        form = RatingForm(data=request.POST)
        if form.is_valid():
            session_key = self._get_session_key(request)
            Rating.objects.update_or_create(
                post=post,
                session_key=session_key,
                defaults={
                    "value":      form.cleaned_data["value"],
                    "ip_address": self._get_ip(request),
                },
            )
            messages.success(request, "¡Gracias por tu puntaje!")
        else:
            messages.error(request, "Puntaje inválido.")
        return redirect("blog:post-detail", pk=post.pk)


class PostCreateView(LoginRequiredMixin, CreateView):
    """Crea una nueva publicación (requiere login)."""
    model         = Post
    form_class    = PostForm
    template_name = "blog/post_form.html"
    success_url   = reverse_lazy("blog:post-list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Publicación creada correctamente.")
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """Edita una publicación existente (requiere login)."""
    model         = Post
    form_class    = PostForm
    template_name = "blog/post_form.html"
    success_url   = reverse_lazy("blog:post-list")

    def form_valid(self, form):
        messages.success(self.request, "Publicación actualizada.")
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """Confirma y elimina una publicación (requiere login)."""
    model         = Post
    template_name = "blog/post_confirm_delete.html"
    success_url   = reverse_lazy("blog:post-list")

    def form_valid(self, form):
        messages.success(self.request, "Publicación eliminada.")
        return super().form_valid(form)


class RegisterView(View):
    """Registro de usuarios simples (sin acceso al admin)."""
    template_name = "registration/register.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("blog:post-list")
        return render(request, self.template_name, {"form": UserCreationForm()})

    def post(self, request):
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            # Garantizar que no sea staff ni superusuario
            user.is_staff     = False
            user.is_superuser = False
            user.save(update_fields=["is_staff", "is_superuser"])
            login(request, user)
            messages.success(request, f"¡Bienvenido/a, {user.username}! Tu cuenta fue creada.")
            return redirect("blog:post-list")
        return render(request, self.template_name, {"form": form})
