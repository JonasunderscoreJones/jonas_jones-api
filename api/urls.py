from xml.etree.ElementInclude import include

from django.urls import path, include
from api.views import ping, version

urlpatterns = [
    path("v1/", include("api.v1.urls")),
    path("v2/", include("api.v2.urls")),
    path("ping", ping, name="ping"),
    path("version", version, name="version"),
]