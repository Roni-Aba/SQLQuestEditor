from django.shortcuts import redirect


def level_name_is_taken(game_json, level_name, editing_level_id=None):
    levels = game_json.get("level", []) if isinstance(game_json, dict) else []
    if not isinstance(levels, list):
        return False
    return any(
        isinstance(level, dict)
        and level.get("id") == level_name
        and level.get("id") != editing_level_id
        for level in levels
    )


def save_new_level_session(request, saved_level):
    request.session["new_level"] = saved_level
    request.session.modified = True


def get_steps(active_step):
    steps = []
    for number in range(0, 9):
        steps.append({"number": number, "active": number <= active_step})
    return steps

def remember_item_summary_return(request):
    if (
            request.method == "GET"
            and request.GET.get("return_to") == "summary"
    ):
        request.session["item_creation_return_to"] = "summary"
        request.session.modified = True

    return (
        request.session.get("item_creation_return_to")
        == "summary"
    )


def redirect_after_item_section_edit(
        request,
        default_view_name,
):
    if not request.session.get("item_edit_mode"):
        if request.session.get("item_creation_return_to") == "summary":
            request.session.pop("item_creation_return_to", None)
            request.session.modified = True
            return redirect("create_level7")
        return redirect(default_view_name)

    editing_item_id = request.session.get(
        "editing_item_id"
    )

    request.session.pop(
        "editing_item_section",
        None,
    )
    request.session.modified = True

    if not editing_item_id:
        return redirect(default_view_name)

    return redirect(
        "edit_item",
        item_id=editing_item_id,
    )


def set_guided_level_creation(request, active):
    if active:
        request.session["guided_level_creation"] = True
    else:
        request.session.pop("guided_level_creation", None)
    request.session.modified = True
