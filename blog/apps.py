from django.apps import AppConfig
from django.contrib import admin



class BlogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "blog"
    verbose_name = "BlogApp"
    def ready(self):
        admin.site.site_header = "BlogApp — Administración" # cabecera del login y barra superior
        admin.site.site_title = "BlogApp Admin" # <title> del browser
        admin.site.index_title = "Panel de Control"
        
