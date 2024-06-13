from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.views.generic import RedirectView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    # path('', RedirectView.as_view(url='/user/intro', permanent=False)),
    path("admin/", admin.site.urls),
    path("user/", include("users.urls")),
    path("store/", include("store.urls")),
    # path("chat/", include("chat.urls")),
    path("restaurants/", include("restaurant2.urls")),
    path("", include_docs_urls(title="OverSea APIs") ),
    path(
        "schema",
        get_schema_view(
            title="OverSea APIs",
            description="APIs for Humascot OverSea",
            version="1.0.0",
        ),
        name="openapi-shecma",
    ),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
