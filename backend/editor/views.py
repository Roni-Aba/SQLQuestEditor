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