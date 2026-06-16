from django.shortcuts import render
from pathlib import Path
from django.conf import settings
import json
# Create your views here.
def start_page(request):
    return render(request, "editor/start.html")

def level_view(request):

    return render(request, "editor/level.html", {
        "nameOfLevels": []
    })


def upload_json_view(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("json_file")

        if not uploaded_file:
            return render(request, "editor/start.html", {"error": "No file uploaded."})

        fileContent = uploaded_file.read().decode("utf-8")
        game= json.loads(fileContent)

        nameOfLevels = []
        for level in game["level"]:
            nameOfLevels.append(level["id"])
        return render(request, "editor/level.html", {

            "nameOfLevels": nameOfLevels
        })
    return render(request, "editor/start.html")

def component_test_view(request):
    steps = [
        {"number": 1, "active": True},{"number": 2, "active": True},
        {"number": 3, "active": True},{"number": 4, "active": True},
        {"number": 5, "active": False},{"number": 6, "active": False},
        {"number": 7, "active": False},{"number": 8, "active": False},
    ]
    return render(request, "editor/test.html", {"steps": steps,})

def create_level(request):
    steps = [
        {"number": 1, "active": False},
        {"number": 2, "active": False},
        {"number": 3, "active": False},
        {"number": 4, "active": False},
        {"number": 5, "active": False},
        {"number": 6, "active": False},
        {"number": 7, "active": False},
        {"number": 8, "active": False},
    ]

    context = {
        "steps": steps,
    }

    return render(request, "editor/createLevel.html", context)