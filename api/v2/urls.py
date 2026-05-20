from django.urls import path

from api.v2.views import ping, version

urlpatterns = [
    path("ping", ping, name="ping"),
    path("version", version, name="version"),
]