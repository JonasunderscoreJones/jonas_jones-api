from django.urls import path, include

from api.v1.views import ping, version

urlpatterns = [
    path("debug/", include("api.v1.debug.urls")),
    path("kcomebacks/", include("api.v1.kcomebacks.urls")),
    path("ping", ping, name="ping"),
    path("version", version, name="version"),
]