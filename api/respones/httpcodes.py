from django.http import JsonResponse

def custom_400_response(request, exception):
    return JsonResponse({
        "message": "Bad Request"
    }, status=400)

def custom_403_response(request, exception):
    return JsonResponse({
        "message": "Permission Denied"
    }, status=403)

def custom_404_response(request, exception):
    return JsonResponse({
        "message": "Not Found"
    }, status=404)

def custom_500_response(request):
    return JsonResponse({
        "message": "Internal Server Error"
    }, status=500)