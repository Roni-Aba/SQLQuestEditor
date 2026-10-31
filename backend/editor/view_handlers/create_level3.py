import json

from django.conf import settings
from django.shortcuts import redirect, render

from ..services.exit_editor import update_exit_fields
from ..services.hint_editor import update_hint_field, update_hint_image
from ..services.item_draft import (
    clear_item_draft,
    clear_table_data_on_type_change,
    item_type_and_next_view,
)
from ..services.table_editor import (
    parse_table_columns,
    parse_table_rows,
    persist_draft_table_rows,
)
from .shared import (
    get_steps,
    redirect_after_item_section_edit,
    remember_item_summary_return,
)


def create_level3_view(request):
    steps = get_steps(active_step=3)
    saved_level = request.session.get("new_level", {})

    if request.method == "GET":
        return_to = request.GET.get("return_to", "")
        reset_item_draft = request.session.pop(
            "reset_item_draft_on_create_level3",
            False,
        )

        if return_to == "items":
            request.session["item_creation_return_to"] = "items"
            clear_item_draft(saved_level)
            request.session.pop("editing_item_id", None)
            request.session.pop("item_edit_mode", None)
            request.session.pop("editing_item_section", None)
            request.session["new_level"] = saved_level
            request.session.modified = True
        elif return_to == "summary":
            request.session["item_creation_return_to"] = "summary"
            request.session.modified = True
        elif (
            reset_item_draft
            and not request.session.get("item_edit_mode", False)
        ):
            clear_item_draft(saved_level)
            request.session["new_level"] = saved_level
            request.session.modified = True
        elif (
            not request.session.get("item_edit_mode", False)
            and request.session.get("item_creation_return_to")
            not in {"items", "summary", "level8"}
        ):
            request.session.pop("item_creation_return_to", None)
            request.session.modified = True

    return_to_item_summary = (
        request.session.get("item_creation_return_to") == "summary"
    )
    return_to_item_overview = (
        request.session.get("item_creation_return_to") == "items"
    )
    return_to_level8 = (
        request.session.get("item_creation_return_to") == "level8"
    )
    item = saved_level.get("item", {})
    form_values = {"item_type": item.get("type", "")}

    if request.method == "POST":
        return redirect("create_level31")

    return render(
        request,
        "editor/createLevel3.html",
        {
            "steps": steps,
            "saved_level": saved_level,
            "form_values": form_values,
            "is_item_edit": request.session.get("item_edit_mode", False),
            "editing_item_id": request.session.get("editing_item_id", ""),
            "return_to_item_overview": return_to_item_overview,
            "return_to_item_summary": return_to_item_summary,
            "return_to_level8": return_to_level8,
        },
    )


def create_level31_view(request):
    return_to_item_summary = remember_item_summary_return(request)
    return_to_item_overview = (
        request.session.get("item_creation_return_to") == "items"
    )
    steps = get_steps(active_step=3)
    saved_level = request.session.get("new_level", {})
    item = saved_level.get("item", {})

    type_options = [
        {"value": "table", "label": "Table"},
        {"value": "hint", "label": "Hint"},
        {"value": "exit", "label": "Exit"},
    ]
    form_values = {"item_type": item.get("type", "")}

    if request.method == "POST":
        item_type, next_view = item_type_and_next_view(request.POST)
        clear_table_data_on_type_change(
            request,
            saved_level,
            item,
            item_type,
        )

        item["type"] = item_type
        saved_level["item"] = item
        request.session["new_level"] = saved_level
        request.session.modified = True

        return redirect(next_view)

    return render(
        request,
        "editor/createLevel3-1.html",
        {
            "steps": steps,
            "saved_level": saved_level,
            "form_values": form_values,
            "type_options": type_options,
            "is_item_edit": request.session.get("item_edit_mode", False),
            "editing_item_id": request.session.get("editing_item_id", ""),
            "return_to_item_overview": return_to_item_overview,
            "return_to_item_summary": return_to_item_summary,
        },
    )


def create_level3exit_view(request):
    return_to_item_summary = remember_item_summary_return(request)
    return_to_item_overview = (
        request.session.get("item_creation_return_to") == "items"
    )
    steps = get_steps(active_step=3)
    saved_level = request.session.get("new_level", {})
    item = saved_level.get("item", {})

    form_values = {
        "exit_success_message": item.get("exitSuccessMessage", ""),
        "next_level_id": item.get("nextLevelId", ""),
    }

    if request.method == "POST":
        update_exit_fields(item, request.POST)

        saved_level["item"] = item
        request.session["new_level"] = saved_level
        request.session.modified = True

        print("createLevel3exit gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))

        return redirect_after_item_section_edit(
            request,
            "create_level4",
        )
    return render(
        request,
        "editor/createLevel3exit.html",
        {
            "steps": steps,
            "saved_level": saved_level,
            "form_values": form_values,
            "is_item_edit": request.session.get("item_edit_mode", False),
            "editing_item_id": request.session.get("editing_item_id", ""),
            "return_to_item_overview": return_to_item_overview,
            "return_to_item_summary": return_to_item_summary,
        },
    )


def create_level3hint_view(request):
    return_to_item_summary = remember_item_summary_return(request)
    return_to_item_overview = (
        request.session.get("item_creation_return_to") == "items"
    )
    steps = get_steps(active_step=3)
    saved_level = request.session.get("new_level", {})
    item = saved_level.get("item", {})

    current_hint_type = item.get("hintType", "")
    hint_options = [
        {"value": "text", "label": "Über einen Text"},
        {"value": "image", "label": "Über ein Bild"},
        {"value": "text_image", "label": "Über einen Text und ein Bild"},
    ]
    form_values = {
        "hint_type": current_hint_type,
        "hint_text": item.get("text", ""),
        "hint_image": item.get("imageLink", ""),
    }

    if request.method == "POST":
        hint_type = update_hint_field(item, request.POST)
        uploaded_image = request.FILES.get("hint_image")

        update_hint_image(item, saved_level, uploaded_image, hint_type, settings.BASE_DIR,)

        saved_level["item"] = item
        request.session["new_level"] = saved_level
        request.session.modified = True

        print("createLevel3hint gespeichert:")
        print(json.dumps(saved_level, ensure_ascii=False, indent=2))

        return redirect_after_item_section_edit(
            request,
            "create_level4",
        )

    return render(
        request,
        "editor/createLevel3hint.html",
        {
            "steps": steps,
            "saved_level": saved_level,
            "form_values": form_values,
            "hint_options": hint_options,
            "is_item_edit": request.session.get("item_edit_mode", False),
            "editing_item_id": request.session.get("editing_item_id", ""),
            "return_to_item_overview": return_to_item_overview,
            "return_to_item_summary": return_to_item_summary,
        },
    )


def create_level3table_view(request):
    return_to_item_summary = remember_item_summary_return(request)
    return_to_item_overview = (
        request.session.get("item_creation_return_to") == "items"
    )
    steps = get_steps(active_step=3)
    saved_level = request.session.get("new_level", {})
    item = saved_level.get("item", {})

    data_type_options = [
        {"value": "text", "label": "Text"},
        {"value": "number", "label": "Zahl"},
        {"value": "date", "label": "Datum"},
        {"value": "boolean", "label": "Boolean"},
    ]

    form_values = {
        "table_name": item.get("tableName", item.get("id", "")),
        "columns": item.get("columns", []),
        "rows": item.get("rows", []),
    }
    error_message = ""

    if request.method == "POST":
        columns, error_message = parse_table_columns(
            request.POST.getlist("column_ids[]"),
            request.POST.getlist("column_types[]"),
        )

        rows = []
        raw_rows_json = request.POST.get("rows_json", "[]")

        if not error_message:
            rows, error_message = parse_table_rows(
                raw_rows_json,
                columns,
            )

        form_values = {
            "table_name": item.get("id", ""),
            "columns": columns,
            "rows": rows,
        }

        if not columns and not error_message:
            error_message = "Lege mindestens eine Tabellenspalte an."

        if not error_message and not request.session.get("item_edit_mode"):
            persist_draft_table_rows(request, saved_level, item, rows)

        if not error_message:
            item_name = str(item.get("id", "")).strip()

            item["type"] = "table"
            item["tableName"] = item_name
            item["columns"] = columns
            item["rows"] = rows

            saved_level["item"] = item
            request.session["new_level"] = saved_level
            request.session.modified = True

            print("createLevel3table gespeichert:")
            print(json.dumps(saved_level, ensure_ascii=False, indent=2))

            return redirect_after_item_section_edit(
                request,
                "create_level4",
            )

    return render(
        request,
        "editor/createLevel3table.html",
        {
            "steps": steps,
            "saved_level": saved_level,
            "form_values": form_values,
            "data_type_options": data_type_options,
            "error_message": error_message,
            "is_item_edit": request.session.get("item_edit_mode", False),
            "editing_item_id": request.session.get("editing_item_id", ""),
            "return_to_item_overview": return_to_item_overview,
            "return_to_item_summary": return_to_item_summary,
        },
    )
