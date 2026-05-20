from django.urls import path

from api.v1.debug.views import debug_headers


urlpatterns = [
    path("headers", debug_headers, name="headers"),
]