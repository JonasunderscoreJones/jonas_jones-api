from django.http import JsonResponse


def debug_headers(request):
    return JsonResponse(dict(request.headers))