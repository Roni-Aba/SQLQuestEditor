from django.shortcuts import render
from pathlib import Path
from django.conf import settings
import json
# Create your views here.
def start_page(request):
    return render(request, "editor/start.html")

def level_view(request):
    gameFile = Path(settings.BASE_DIR / "SQLSpellQuest.json")

    with open(gameFile, "r", encoding="utf-8") as file:
        game = json.load(file)

    nameOfLevels = []
    levelList = game["level"]
    for x in levelList:
        nameOfLevels.append(x["id"])
    return render(request, "editor/level.html", {
        "nameOfLevels": nameOfLevels,
    })