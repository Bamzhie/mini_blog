from django.http import HttpResponse
from django.http import JsonResponse


def homepage(request):
    return JsonResponse(
        {
            "status": 200,
            "message": "Hello, world!",
        }
    )


def about(request):
    return HttpResponse("About page")
