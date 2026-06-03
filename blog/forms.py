from django import forms
from .models import Post, Comment, Rating


class PostForm(forms.ModelForm):
    """Formulario para crear y editar publicaciones."""

    class Meta:
        model  = Post
        # auto_now_add/auto_now quedan excluidos automáticamente (editable=False)
        fields = ["title", "body", "category", "tags", "image", "published"]
        widgets = {
            "title":     forms.TextInput(attrs={"class": "form-control", "placeholder": "Título de la publicación"}),
            "body":      forms.Textarea(attrs={"class": "form-control", "rows": 8}),
            "category":  forms.Select(attrs={"class": "form-select"}),
            "tags":      forms.SelectMultiple(attrs={"class": "form-select", "size": 5}),
            "image":     forms.ClearableFileInput(attrs={"class": "form-control"}),
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
    """Formulario para agregar comentarios a una publicación.
    Los campos author_name/author_email son obligatorios solo para anónimos
    (validación en la vista, no en el form, para simplificar).
    """

    class Meta:
        model  = Comment
        fields = ["author_name", "author_email", "body"]
        widgets = {
            "author_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Tu nombre",
            }),
            "author_email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Tu email (opcional)",
            }),
            "body": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Escribí tu comentario...",
            }),
        }
        labels = {
            "author_name":  "Nombre",
            "author_email": "Email",
            "body":         "Comentario",
        }
        error_messages = {"body": {"required": "El comentario no puede estar vacío."}}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Si el usuario está logueado, ocultamos los campos de nombre/email
        if user and user.is_authenticated:
            self.fields.pop("author_name")
            self.fields.pop("author_email")
        else:
            self.fields["author_name"].required = True


class RatingForm(forms.Form):
    """Formulario de puntaje (1-5 estrellas) para una publicación."""
    value = forms.ChoiceField(
        choices=[(i, f"{i} estrella{'s' if i > 1 else ''}") for i in range(1, 6)],
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        label="Tu puntaje",
    )

class RawForm(forms.Form):
    """Formulario para crear publicaciones usando directamente forms.Form."""

    title = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Título de la publicación"}),
        label="Título",
        error_messages={"required": "El título es obligatorio."},
    )
    body = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 8}),
        label="Contenido",
        error_messages={"required": "El contenido es obligatorio."},
    )
    category = forms.ChoiceField(
        choices=[],  # Las opciones deben ser configuradas dinámicamente
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Categoría",
    )
    tags = forms.MultipleChoiceField(
        choices=[],  # Las opciones deben ser configuradas dinámicamente
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": 5}),
        label="Etiquetas",
    )
    published = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="¿Publicar?",
    )

    def clean_title(self):
        """Validación personalizada para el título."""
        title = self.cleaned_data["title"].strip()
        if len(title) < 10:
            raise forms.ValidationError(
                "Mínimo %(min)s caracteres.", params={"min": 10}
            )
        qs = Post.objects.filter(title__iexact=title)
        if qs.exists():
            raise forms.ValidationError("Ya existe una publicación con ese título.")
        return title

    def clean(self):
        """Validación cruzada: publicar requiere contenido mínimo."""
        cleaned = super().clean()
        body = cleaned.get("body", "")
        published = cleaned.get("published", False)
        if published and len(body) < 50:
            raise forms.ValidationError(
                "Para publicar, el contenido debe tener al menos 50 caracteres."
            )
        return cleaned
