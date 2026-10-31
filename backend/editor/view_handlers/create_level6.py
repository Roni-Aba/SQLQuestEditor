import json

from django.shortcuts import redirect, render

from ..services.item_unlock import (
    update_password_requirement,
    update_password_details,
    failure_hints_from_post,
)
from .shared import get_steps, remember_item_summary_return


def redirect_after_item_password_edit(
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


def create_level6_view(request):
    return_to_item_summary = remember_item_summary_return(request)
    steps = get_steps(active_step=6)
    saved_level = request.session.get("new_level", {})
    unlock_condition = saved_level.get("unlockCondition", {})
    selected_item = saved_level.get("item", {})

    required_items = unlock_condition.get(
        "requiredItems",
        selected_item.get("unlockedItems", []),
    )
    requires_password = unlock_condition.get("requiresPassword", False)
    form_values = {
        "required_items": required_items,
        "requires_password": "true" if requires_password else "false",
    }

    if request.method == "POST":
        requires_password = update_password_requirement(
            unlock_condition,
            selected_item,
            request.POST,
        )

        saved_level["unlockCondition"] = unlock_condition
        request.session["new_level"] = saved_level
        request.session.modified = True

        print("createLevel6 gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))

        if requires_password:
            return redirect("create_level61")

        return redirect_after_item_password_edit(
            request,
            "create_level7",
        )

    return render(
        request,
        "editor/createLevel6.html",
        {
            "steps": steps,
            "saved_level": saved_level,
            "form_values": form_values,
            "is_item_edit": request.session.get("item_edit_mode", False),
            "editing_item_id": request.session.get("editing_item_id", ""),
            "return_to_item_summary": return_to_item_summary,
        },
    )


def create_level61_view(request):
    return_to_item_summary = remember_item_summary_return(request)
    steps = get_steps(active_step=6)
    saved_level = request.session.get("new_level", {})
    unlock_condition = saved_level.get("unlockCondition", {})

    passwords = unlock_condition.get("passwords", [])
    if not isinstance(passwords, list):
        passwords = []

    form_values = {
        "item_passwords": ", ".join(passwords),
        "password_hint": unlock_condition.get("passwordHint", ""),
        "success_message": unlock_condition.get("successMessage", ""),
        "show_hints": (
            "true"
            if unlock_condition.get("showHintsOnFailure", False)
            else "false"
        ),
    }

    if request.method == "POST":
        show_hints = update_password_details(
            unlock_condition,
            request.POST,
        )

        saved_level["unlockCondition"] = unlock_condition
        request.session["new_level"] = saved_level
        request.session.modified = True

        print("createLevel6-1 gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))

        if show_hints:
            return redirect("create_level62")

        return redirect_after_item_password_edit(
            request,
            "create_level7",
        )

    return render(
        request,
        "editor/createLevel6-1.html",
        {
            "steps": steps,
            "saved_level": saved_level,
            "form_values": form_values,
            "is_item_edit": request.session.get("item_edit_mode", False),
            "editing_item_id": request.session.get("editing_item_id", ""),
            "return_to_item_summary": return_to_item_summary,
        },
    )


def create_level62_view(request):
    return_to_item_summary = remember_item_summary_return(request)
    steps = get_steps(active_step=6)
    saved_level = request.session.get("new_level", {})
    unlock_condition = saved_level.get("unlockCondition", {})

    failure_hints = unlock_condition.get("failureHints", [])
    if not isinstance(failure_hints, list):
        failure_hints = []

    form_values = {
        "failure_hints": failure_hints,
    }

    if request.method == "POST":
        unlock_condition["failureHints"] = failure_hints_from_post(
            request.POST
        )

        saved_level["unlockCondition"] = unlock_condition
        request.session["new_level"] = saved_level
        request.session.modified = True

        print("createLevel6-2 gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))

        return redirect_after_item_password_edit(
            request,
            "create_level7",
        )

    return render(
        request,
        "editor/createLevel6-2.html",
        {
            "steps": steps,
            "saved_level": saved_level,
            "form_values": form_values,
            "is_item_edit": request.session.get("item_edit_mode", False),
            "editing_item_id": request.session.get("editing_item_id", ""),
            "return_to_item_summary": return_to_item_summary,
        },
    )
