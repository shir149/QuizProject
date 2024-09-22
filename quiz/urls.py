from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("synaptic/", include("synaptic.urls")),
    path("admin/", admin.site.urls),
]
