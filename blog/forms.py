from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Formulario para crear y editar publicaciones."""

    class Meta:
        model  = Post
        # auto_now_add/auto_now quedan excluidos automáticamente (editable=False)
        fields = ["title", "body", "category", "tags", "published"]
        widgets = {
            "title":     forms.TextInput(attrs={"class": "form-control", "placeholder": "Título de la publicación"}),
            "body":      forms.Textarea(attrs={"class": "form-control", "rows": 8}),
            "category":  forms.Select(attrs={"class": "form-select"}),
            "tags":      forms.SelectMultiple(attrs={"class": "form-select", "size": 5}),
            "published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "title":     "Título",
            "body":      "Contenido",
            "category":  "Categoría",
            "tags":      "Etiquetas",
            "published": "¿Publicar?",
        }
        error_messages = {
            "title": {"required": "El título es obligatorio."},
            "body":  {"required": "El contenido es obligatorio."},
        }

    def clean_title(self):
        """Capa 4: validación personalizada con acceso al ORM."""
        title = self.cleaned_data["title"].strip()
        if len(title) < 10:
            raise forms.ValidationError(
                "Mínimo %(min)s caracteres.", params={"min": 10}
            )
        qs = Post.objects.filter(title__iexact=title)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe una publicación con ese título.")
        return title

    def clean(self):
        """Capa 5: validación cruzada — publicar requiere contenido mínimo."""
        cleaned   = super().clean()
        body      = cleaned.get("body", "")
        published = cleaned.get("published", False)

        if published and len(body) < 100:
            self.add_error(
                "body",
                "Para publicar, el contenido debe tener al menos 100 caracteres.",
            )
        return cleaned


class CommentForm(forms.ModelForm):
    """Formulario para agregar comentarios a una publicación."""

    class Meta:
        model  = Comment
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Escribí tu comentario...",
            }),
        }
        labels = {"body": "Comentario"}
        error_messages = {"body": {"required": "El comentario no puede estar vacío."}}
