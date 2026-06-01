from django.urls import path

from api.v2.trigger.views import trigger_kcomebacks_fetcher

urlpatterns = [
    path("kcomebacks", trigger_kcomebacks_fetcher, name="kcomebacks fetching trigger"),
]