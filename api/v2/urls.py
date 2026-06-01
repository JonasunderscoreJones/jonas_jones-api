from django.urls import path, include

from api.v2.views import ping, version

urlpatterns = [
    path("trigger/", include("api.v2.trigger.urls")),
    path("ping", ping, name="ping"),
    path("version", version, name="version"),
]