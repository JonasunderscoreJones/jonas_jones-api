import os

from django.conf import settings
from django.urls import path, include
from django.core.management import execute_from_command_line
from dotenv import load_dotenv

from db.driver import PostgresDriver

DB_DRIVER = PostgresDriver()

settings.configure(
    DEBUG=True,
    ROOT_URLCONF=__name__,
    SECRET_KEY="dev",
    ALLOWED_HOSTS=["*"],
    MIDDLEWARE=[],
)

urlpatterns = [
    path("api/", include("api.urls")),
]


if __name__ == "__main__":
    load_dotenv()
    import django
    django.setup()
    from django.core.management.commands.runserver import Command as runserver
    runserver.default_port = os.getenv("PORT", "6969")
    execute_from_command_line(["main.py", "runserver"])