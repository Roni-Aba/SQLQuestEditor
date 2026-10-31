import json

from django.shortcuts import redirect, render

from ..services.level_basics import (
    level2_form_values,
    query_restriction_from_post,
)
from .shared import get_steps

def create_level2_view(request):
    steps = get_steps(active_step=2)
    saved_level = request.session.get("new_level", {})
    form_values = level2_form_values(saved_level)

    if request.method == "POST":
        saved_level["queryRestriction"] = query_restriction_from_post(request.POST)
        request.session["new_level"] = saved_level
        request.session.modified = True

        print("createLevel2 gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))
        return redirect("create_level3")

    return render(request, "editor/createLevel2.html", {
        "steps": steps,
        "saved_level": saved_level,
        "form_values": form_values,
    })
