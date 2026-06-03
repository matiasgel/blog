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

class fotos(models.Model):
    image      = models.ImageField(
        upload_to="fotos/",
        null=True,
        blank=True,
        verbose_name="Imagen",
        help_text="Imagen opcional para la publicación",
    )
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la imagen")
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
    image      = models.ImageField(
        upload_to="posts/",
        null=True,
        blank=True,
        verbose_name="Imagen",
        help_text="Imagen opcional para la publicación",
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
    """Comentario en una publicación. Admite comentarios anónimos con aprobación."""
    post   = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Publicación",
    )
    # Null cuando el comentario es anónimo
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Autor",
        null=True,
        blank=True,
    )
    # Campos para comentarios anónimos
    author_name  = models.CharField(max_length=100, blank=True, verbose_name="Nombre")
    author_email = models.EmailField(blank=True, verbose_name="Email")

    body       = models.TextField(verbose_name="Contenido")
    approved   = models.BooleanField(default=False, verbose_name="Aprobado")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")

    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ["created_at"]

    def get_author_display(self):
        if self.author:
            return self.author.get_full_name() or self.author.username
        return self.author_name or "Anónimo"

    def __str__(self):
        return f"Comentario de {self.get_author_display()} en '{self.post.title}'"


class Rating(models.Model):
    """Puntaje anónimo (1-5 estrellas) para una publicación."""
    STAR_CHOICES = [(i, str(i)) for i in range(1, 6)]

    post        = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="ratings",
        verbose_name="Publicación",
    )
    value       = models.PositiveSmallIntegerField(
        choices=STAR_CHOICES,
        verbose_name="Puntaje",
    )
    session_key = models.CharField(max_length=40, verbose_name="Sesión")
    ip_address  = models.GenericIPAddressField(
        null=True, blank=True, verbose_name="IP"
    )
    created_at  = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")

    class Meta:
        verbose_name = "Puntaje"
        verbose_name_plural = "Puntajes"
        unique_together = [("post", "session_key")]

    def __str__(self):
        return f"{self.value}★ en '{self.post.title}'"
