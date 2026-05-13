from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    """Categoría de publicaciones."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Etiqueta para clasificación múltiple de publicaciones."""
    name = models.CharField(max_length=50, unique=True, verbose_name="Nombre")
    slug = models.SlugField(max_length=50, unique=True, verbose_name="Slug")

    class Meta:
        verbose_name = "Etiqueta"
        verbose_name_plural = "Etiquetas"
        ordering = ["name"]

    def __str__(self):
        return self.name


class PublishedManager(models.Manager):
    """Manager que filtra solo publicaciones publicadas."""
    def get_queryset(self):
        return super().get_queryset().filter(published=True)

    def recientes(self, n=10):
        """Top N publicados — con only() para eficiencia."""
        return (
            self.get_queryset()
            .select_related("author")
            .only("title", "created_at", "author__username")
            .order_by("-created_at")[:n]
        )


class Post(models.Model):
    """Publicación del blog."""
    title      = models.CharField(max_length=200, verbose_name="Título")
    body       = models.TextField(verbose_name="Contenido")
    author     = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Autor",
    )
    category   = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
        verbose_name="Categoría",
    )
    tags       = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="posts",
        verbose_name="Etiquetas",
    )
    published  = models.BooleanField(default=False, verbose_name="Publicado")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado el")

    # Managers — siempre declarar el default primero
    objects   = models.Manager()
    published_posts = PublishedManager()

    class Meta:
        verbose_name = "Publicación"
        verbose_name_plural = "Publicaciones"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Comentario en una publicación."""
    post   = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Publicación",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Autor",
    )
    body       = models.TextField(verbose_name="Contenido")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")

    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ["created_at"]

    def __str__(self):
        return f"Comentario de {self.author.username} en '{self.post.title}'"
