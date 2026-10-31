import json

from django.shortcuts import redirect, render

from ..services.item_summary import get_item_summary
from .shared import get_steps


def create_level7_view(request):
    steps = get_steps(active_step=7)
    saved_level = request.session.get(
        "new_level",
        {},
    )
    unlock_condition = saved_level.get("unlockCondition", {})
    if not unlock_condition.get("requiresPassword", False):
        back_url_name = "create_level6"
    elif unlock_condition.get("showHintsOnFailure", False):
        back_url_name = "create_level62"
    else:
        back_url_name = "create_level61"
    summary = get_item_summary(saved_level)
    if request.method == "POST":
        print("createLevel7 Übersicht:")
        print(
            json.dumps(
                saved_level,
                ensure_ascii=False,
                indent=2,
            )
        )
        return redirect("create_level8")
    return render(
        request,
        "editor/createLevel7.html",
        {
            "steps": steps,
            "saved_level": saved_level,
            "summary": summary,
            "back_url_name": back_url_name,
        },
    )
