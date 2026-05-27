from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import urls as auth_urls


urlpatterns = [
    path("admin/", admin.site.urls),
    path("blog/", include("blog.urls", namespace="blog")),
    path("", include("blog.urls", namespace="blog_root")),
    path("cuenta/", include(auth_urls)),

]
