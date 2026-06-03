from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import urls as auth_urls
from django.conf import settings
from django.conf.urls.static import static
from blog.views import RegisterView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("blog/", include("blog.urls", namespace="blog")),
    path("", include("blog.urls", namespace="blog_root")),
    path("cuenta/", include(auth_urls)),
    path("cuenta/registro/", RegisterView.as_view(), name="register"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

