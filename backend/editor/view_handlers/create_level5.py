import json

from django.shortcuts import redirect, render

from ..services.item_position import position_form_values, position_from_post
from .shared import (
    get_steps,
    redirect_after_item_section_edit,
    remember_item_summary_return,
)


def create_level5_view(request):
    steps = get_steps(active_step=5)
    saved_level = request.session.get("new_level", {})
    item_type = saved_level.get("item", {}).get("type", "")
    form_values = {
        "item_type": item_type,
    }
    if request.method == "POST":
        print("createLevel5 gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))
        return redirect("create_level51")
    return render(request, "editor/createLevel5.html", {
        "steps": steps,
        "saved_level": saved_level,
        "form_values": form_values,
        "back_url_name": "create_level4",
    })


def create_level51_view(request):
    return_to_item_summary = remember_item_summary_return(request)
    steps = get_steps(active_step=5)
    saved_level = request.session.get("new_level", {})
    form_values = position_form_values(saved_level)

    if request.method == "POST":
        saved_level["position"] = position_from_post(request.POST)
        request.session["new_level"] = saved_level
        request.session.modified = True

        print("createLevel5-1 gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))

        return redirect_after_item_section_edit(
            request,
            "create_level6",
        )

    return render(
        request,
        "editor/createLevel51.html",
        {
            "steps": steps,
            "saved_level": saved_level,
            "form_values": form_values,
            "is_item_edit": request.session.get("item_edit_mode", False),
            "editing_item_id": request.session.get("editing_item_id", ""),
            "return_to_item_summary": return_to_item_summary,
        },
    )
