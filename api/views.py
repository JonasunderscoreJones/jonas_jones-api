from django.http import JsonResponse

from config import __version__


def ping(request):
    return JsonResponse({
        "message": "pong"
    })

def version(request):
    return JsonResponse({"version": __version__})