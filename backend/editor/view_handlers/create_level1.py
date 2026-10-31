import json
from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect, render

from .. import database, utils
from ..services.level_basics import level1_form_values
from .shared import get_steps, level_name_is_taken, save_new_level_session

def create_level1_view(request):
    steps = get_steps(active_step=1)
    saved_level = request.session.get("new_level", {})
    form_values = level1_form_values(saved_level)

    if request.method == "POST":
        level_id = request.POST.get("level_name", "").strip()
        start_dialog = request.POST.get("level_greeting", "").strip()
        if level_name_is_taken(request.session.get("game_json", {}), level_id):
            return render(request, "editor/createLevel1.html", {
                "steps": steps,
                "saved_level": saved_level,
                "form_values": {
                    "level_name": level_id,
                    "level_greeting": start_dialog,
                    "level_picture": saved_level.get("levelPicture", ""),
                },
                "error_message": f'Der Levelname "{level_id}" wird bereits verwendet.',
            })

        saved_level["id"] = level_id
        saved_level["databaseName"] = utils.database_name_for_level(level_id)
        database.finalize_editor_level_rows(
            request,
            saved_level,
            level_id,
        )
        saved_level["startDialog"] = start_dialog
        uploaded_picture = request.FILES.get("levelPicture")
        if uploaded_picture:
            upload_dir = (Path(settings.BASE_DIR) / "editor" / "static" / "editor" / "img" / "levels")
            upload_dir.mkdir(parents=True, exist_ok=True)
            storage = FileSystemStorage(location=upload_dir)
            level_picture_name = storage.save(
                uploaded_picture.name,
                uploaded_picture
            )
            saved_level["levelPicture"] = level_picture_name
            saved_level.setdefault("_new_asset_sources", {})[
                level_picture_name
            ] = str(upload_dir / level_picture_name)
        save_new_level_session(request, saved_level)
        print("createLevel1 gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))
        return redirect("create_level2")
    return render(request, "editor/createLevel1.html", {
        "steps": steps,
        "saved_level": saved_level,
        "form_values": form_values,
    })
