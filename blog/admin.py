from django.contrib import admin
from .models import Category, Comment, Post, Rating, Tag, fotos


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display  = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display   = ["title", "author", "category", "published", "created_at"]
    list_filter    = ["published", "category"]
    search_fields  = ["title", "body"]
    filter_horizontal = ["tags"]
    date_hierarchy = "created_at"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display   = ["__str__", "post", "approved", "created_at"]
    list_filter    = ["approved", "created_at"]
    list_editable  = ["approved"]
    search_fields  = ["author__username", "author_name", "body"]
    raw_id_fields  = ["post"]
    actions        = ["approve_comments", "reject_comments"]

    @admin.action(description="Aprobar comentarios seleccionados")
    def approve_comments(self, request, queryset):
        updated = queryset.update(approved=True)
        self.message_user(request, f"{updated} comentario(s) aprobado(s).")

    @admin.action(description="Rechazar comentarios seleccionados")
    def reject_comments(self, request, queryset):
        updated = queryset.update(approved=False)
        self.message_user(request, f"{updated} comentario(s) rechazado(s).")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Los moderadores (staff, no superadmin) solo ven comentarios pendientes por defecto
            return qs.select_related("post", "author")
        return qs.select_related("post", "author")


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display  = ["post", "value", "session_key", "ip_address", "created_at"]
    list_filter   = ["value"]
    search_fields = ["post__title"]
    readonly_fields = ["post", "value", "session_key", "ip_address", "created_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
    
    
@admin.register(fotos)
class FotosAdmin(admin.ModelAdmin):
    list_display  = ["nombre", "image"]
    search_fields = ["nombre"]