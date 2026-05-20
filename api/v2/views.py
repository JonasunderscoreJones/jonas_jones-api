from django.http import JsonResponse, HttpResponsePermanentRedirect


def ping(request):
    return JsonResponse({
        "message": "pong"
    })

def version(request):
    return HttpResponsePermanentRedirect("/api/version")