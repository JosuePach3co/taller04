from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def index(request):
    # return HttpResponse("¡Bienvenido a la aplicación Django!")
    return render(request, 'homepage/index.html')