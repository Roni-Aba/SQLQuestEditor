from django.shortcuts import render

# Create your views here.
def start_page(request):
    return render(request, "editor/start.html")

def level_view(request):
    return render(request, "editor/level.html")