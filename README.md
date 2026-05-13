# BlogApp — Proyecto de desarrollo de clase

Proyecto Django para desarrollar los ejemplos del **Módulo V: Vistas, Templates y Formularios**.

> Este directorio está en `.gitignore` — no se versiona.

## Setup rápido

```powershell
# 1. Crear y activar el entorno virtual
cd blog
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Aplicar migraciones
python manage.py migrate

# 4. Cargar datos de precarga (categorías, tags, posts, comentarios)
python manage.py loaddata blog/fixtures/initial_data.json

# 5. Levantar el servidor
python manage.py runserver
```

Abrir: http://127.0.0.1:8000/blog/

## Usuarios precargados

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| `admin`  | `admin123` | Superusuario |
| `maria`  | `admin123` | Usuario |
| `juan`   | `admin123` | Usuario |

Panel admin: http://127.0.0.1:8000/admin/

## Modelos

| Modelo | Descripción |
|--------|-------------|
| `Category` | Categoría de publicaciones (FK en Post) |
| `Tag` | Etiquetas M2M en publicaciones |
| `Post` | Publicación con título, cuerpo, autor, categoría, tags, publicado |
| `Comment` | Comentario en una publicación (FK inversa `post.comments`) |

## URLs disponibles

| URL | Vista | Nombre |
|-----|-------|--------|
| `/blog/` | `PostListView` | `blog:post-list` |
| `/blog/posts/<pk>/` | `PostDetailView` | `blog:post-detail` |
| `/blog/posts/crear/` | `PostCreateView` | `blog:post-create` |
| `/blog/posts/<pk>/editar/` | `PostUpdateView` | `blog:post-update` |
| `/blog/posts/<pk>/eliminar/` | `PostDeleteView` | `blog:post-delete` |

## Estructura

```
blog/
├── manage.py
├── requirements.txt
├── README.md
├── blog_project/
│   ├── settings.py
│   └── urls.py
└── blog/
    ├── models.py       ← Category, Tag, Post, Comment + PublishedManager
    ├── views.py        ← PostListView, DetailView, CreateView, UpdateView, DeleteView
    ├── forms.py        ← PostForm (ModelForm con clean_title + clean), CommentForm
    ├── urls.py         ← urlpatterns con namespace="blog"
    ├── admin.py
    ├── fixtures/
    │   └── initial_data.json
    └── templates/blog/
        ├── base.html
        ├── post_list.html
        ├── post_detail.html
        ├── post_form.html
        └── post_confirm_delete.html
```
