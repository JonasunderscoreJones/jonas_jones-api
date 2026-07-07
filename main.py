import os

from django.conf import settings
from django.urls import path, include
from django.core.management import execute_from_command_line
from dotenv import load_dotenv

from api.respones.httpcodes import custom_400_response, custom_403_response, custom_404_response, custom_500_response
from db.driver import PostgresDriver

DB_DRIVER = PostgresDriver()

settings.configure(
    DEBUG=False,
    ROOT_URLCONF=__name__,
    SECRET_KEY="dev",
    ALLOWED_HOSTS=["*"],
)

urlpatterns = [
    path("", include("api.urls")),
]

handler400 = custom_400_response
handler403 = custom_403_response
handler404 = custom_404_response
handler500 = custom_500_response


if __name__ == "__main__":
    load_dotenv()
    import django
    django.setup()
    from django.core.management.commands.runserver import Command as runserver
    runserver.default_port = os.getenv("PORT", "6969")
    execute_from_command_line(["main.py", "runserver"])