from copy import deepcopy

from .. import database
from ..utils import database_name_for_level
from . import item_service
from .assets import save_uploaded_image
from .game_messages import normalize_game_messages


# Grunddaten und SQL-Beschränkungen

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


def update_level_basics(saved_level, level_name, level_greeting):
    saved_level["id"] = level_name
    saved_level["databaseName"] = database_name_for_level(level_name)
    saved_level["startDialog"] = level_greeting


def update_level_picture(saved_level, uploaded_picture, base_dir):
    if not uploaded_picture:
        return

    filename, source_path = save_uploaded_image(uploaded_picture, base_dir, "levels")
    saved_level["levelPicture"] = filename
    saved_level.setdefault("_new_asset_sources", {})[filename] = source_path


def level1_form_values(saved_level):
    return {
        "level_name" : saved_level.get("id",""),
        "level_greeting": saved_level.get("startDialog", ""),
        "level_picture": saved_level.get("levelPicture", ""),
    }


def level2_form_values(saved_level):
    query_restriction = saved_level.get("queryRestriction", {})
    row_restriction = query_restriction.get("rowRestriction", {})
    column_restriction = query_restriction.get("columnRestriction", {})
    row_messages = row_restriction.get("violationMessages", [])
    column_messages = column_restriction.get("violationMessages", [])
    row_column_messages = query_restriction.get("colAndRowViolationMessages",[])

    return {
        "max_columns": (
            column_restriction["maxNumber"]
            if column_restriction.get("maxNumber") is not None
            else ""
        ),
        "max_rows": (
            row_restriction["maxNumber"]
            if row_restriction.get("maxNumber") is not None
            else ""
        ),
        "too_many_rows_message": row_messages[0] if row_messages else "",
        "too_many_columns_message": column_messages[0] if column_messages else "",
        "too_many_rows_columns_message": (
            row_column_messages[0] if row_column_messages else ""
        ),
    }


def query_restriction_from_post(post_data):
    max_columns = post_data.get("max_columns", "").strip()
    max_rows = post_data.get("max_rows", "").strip()
    rows_message = post_data.get("too_many_rows_message", "").strip()
    columns_message = post_data.get("too_many_columns_message", "").strip()
    both_message = post_data.get(
        "too_many_rows_columns_message", ""
    ).strip()

    return {
        "rowRestriction": {
            "maxNumber": int(max_rows) if max_rows.isdigit() else None,
            "violationMessages": [rows_message] if rows_message else [],
        },
        "columnRestriction": {
            "maxNumber": int(max_columns) if max_columns.isdigit() else None,
            "violationMessages": [columns_message] if columns_message else [],
        },
        "colAndRowViolationMessages": [both_message] if both_message else [],
    }


# Bearbeitungsentwurf und JSON

def build_level_edit_session(selected_level):
    if not isinstance(selected_level, dict):
        return {}

    query_restriction = selected_level.get("queryRestriction", {})
    if not isinstance(query_restriction, dict):
        query_restriction = {}

    items = selected_level.get("items", [])
    if not isinstance(items, list):
        items = []

    return {
        "id": selected_level.get("id", ""),
        "levelPicture": selected_level.get("levelPicture", ""),
        "databaseName": selected_level.get("databaseName", ""),
        "startDialog": selected_level.get("startDialog", ""),
        "queryRestriction": deepcopy(query_restriction),
        "items": deepcopy(items),
    }


def build_level_for_json(saved_level):
    database_name = database_name_for_level(saved_level.get("id", ""))

    items = deepcopy(saved_level.get("items", []))
    if not isinstance(items, list):
        items = []

    for item in items:
        if isinstance(item, dict):
            item.pop("data", None)

    return {
        "id": saved_level.get(
            "id",
            "",
        ),
        "levelPicture": saved_level.get(
            "levelPicture",
            "",
        ),
        "databaseName": database_name,
        "startDialog": saved_level.get(
            "startDialog",
            "",
        ),
        "queryRestriction": saved_level.get(
            "queryRestriction",
            {},
        ),
        "items": items,
    }


# Speichern und Verweise

def save_new_level_to_game_json(
    request,
):
    game_json = request.session.get(
        "game_json",
        {},
    )

    if not isinstance(
        game_json,
        dict,
    ):
        game_json = {}

    saved_level = request.session.get(
        "new_level",
        {},
    )

    if not isinstance(
        saved_level,
        dict,
    ):
        saved_level = {}

    saved_level.pop("messages", None)

    saved_level = (
        item_service.save_current_item_to_new_level(
            saved_level
        )
    )

    level_id = saved_level.get(
        "id",
        "",
    )

    if not level_id:
        return game_json, saved_level

    new_level = build_level_for_json(saved_level)
    auto_saved_level_id = request.session.get("auto_saved_level_id", level_id)

    if request.session.get("editing_level_id"):
        request.session["new_level"] = saved_level
        request.session.modified = True
        return game_json, saved_level

    levels = game_json.get(
        "level",
        [],
    )

    if not isinstance(
        levels,
        list,
    ):
        levels = []

    for level in levels:
        if isinstance(level, dict):
            level.pop("messages", None)

    existing_index = None

    for index, level in enumerate(
        levels
    ):
        if not isinstance(
            level,
            dict,
        ):
            continue

        if level.get(
            "id"
        ) == auto_saved_level_id:
            existing_index = index
            break

    if existing_index is not None:
        levels[existing_index] = new_level
    else:
        levels.append(
            new_level
        )

    game_json["level"] = levels

    request.session["game_json"] = (
        game_json
    )

    request.session["new_level"] = (
        saved_level
    )
    request.session["auto_saved_level_id"] = level_id

    request.session.modified = True

    return game_json, saved_level


def replace_or_append_level(levels, level_for_json, editing_level_id):
    level_id = str(level_for_json.get("id", "")).strip()
    updated_levels = []
    level_was_replaced = False

    for level in levels:
        if not isinstance(level, dict):
            updated_levels.append(level)
            continue

        existing_level_id = level.get("id")
        should_replace = (
            editing_level_id and existing_level_id == editing_level_id
        )
        if not editing_level_id:
            should_replace = existing_level_id == level_id

        if should_replace and not level_was_replaced:
            updated_levels.append(deepcopy(level_for_json))
            level_was_replaced = True
        else:
            updated_levels.append(level)

    if not level_was_replaced:
        updated_levels.append(deepcopy(level_for_json))

    return updated_levels


def update_exit_level_references(levels, old_level_id, new_level_id):
    if not old_level_id or old_level_id == new_level_id:
        return

    for level in levels:
        if not isinstance(level, dict):
            continue

        for item in level.get("items", []):
            if (
                isinstance(item, dict)
                and item.get("type") == "exit"
                and item.get("nextLevelId") == old_level_id
            ):
                item["nextLevelId"] = new_level_id


def update_import_sources(
    import_sources, saved_level, editing_level_id, level_id
):
    if not editing_level_id or editing_level_id not in import_sources:
        return False

    source = import_sources.pop(editing_level_id)
    source["tables"] = saved_level.get(
        "_import_table_sources",
        source["tables"],
    )
    new_assets = saved_level.get("_new_asset_sources", {})
    source["assets"].update(new_assets)
    source.setdefault("replacements", {}).update(new_assets)
    import_sources[level_id] = source
    return True


def save_level_to_game_json(request, saved_level, level_for_json, editing_level_id):
    """Commit a validated level draft and finish the editing session."""
    game_json = request.session.get("game_json", {})
    level_id = str(level_for_json.get("id", "")).strip()

    has_table_draft = bool(saved_level.get(database.EDITOR_LEVEL_DRAFT_KEY))
    database.finalize_editor_level_rows(request, saved_level, level_id)

    if not isinstance(game_json, dict):
        game_json = {}
    game_json = normalize_game_messages(game_json)

    levels = game_json.get("level", [])
    if not isinstance(levels, list):
        levels = []

    updated_levels = replace_or_append_level(
        levels,
        level_for_json,
        editing_level_id,
    )
    update_exit_level_references(
        updated_levels,
        editing_level_id,
        level_id,
    )

    game_json["level"] = updated_levels
    request.session["game_json"] = game_json

    import_sources = request.session.get("import_sources", {})
    if update_import_sources(
        import_sources,
        saved_level,
        editing_level_id,
        level_id,
    ):
        request.session["import_sources"] = import_sources

    if editing_level_id and editing_level_id != level_id:
        if has_table_draft:
            database.remove_editor_level_rows(request, editing_level_id)
        else:
            database.move_editor_level_rows(
                request,
                editing_level_id,
                level_id,
            )

    request.session.pop("editing_level_id", None)
    request.session.pop("auto_saved_level_id", None)
    request.session.pop("editing_item_id", None)
    request.session.pop("item_edit_mode", None)
    request.session.pop("editing_item_section", None)
    request.session.pop("new_level", None)
    request.session.pop("item_creation_return_to", None)
    request.session.pop("reset_item_draft_on_create_level3", None)
    request.session.modified = True
    return game_json


# Löschen

def referencing_level_ids(levels, target_level_id):
    references = []

    for level in levels:
        if not isinstance(level, dict) or level.get("id") == target_level_id:
            continue

        items = level.get("items", [])
        if not isinstance(items, list):
            continue

        if any(
            isinstance(item, dict)
            and item.get("type") == "exit"
            and item.get("nextLevelId") == target_level_id
            for item in items
        ):
            references.append(level.get("id", ""))

    return references


def remove_level_from_list(levels, level_id):
    return [
        level
        for level in levels
        if not (isinstance(level, dict) and level.get("id") == level_id)
    ]
