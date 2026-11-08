from copy import deepcopy

from ..utils import database_name_for_level
from . import item_service

def build_level_edit_session(selected_level):
    if not isinstance(
        selected_level,
        dict,
    ):
        return {}

    query_restriction = selected_level.get(
        "queryRestriction",
        {},
    )

    if not isinstance(
        query_restriction,
        dict,
    ):
        query_restriction = {}

    items = selected_level.get(
        "items",
        [],
    )

    if not isinstance(
        items,
        list,
    ):
        items = []

    return {
        "id": selected_level.get(
            "id",
            "",
        ),
        "levelPicture": selected_level.get(
            "levelPicture",
            "",
        ),
        "databaseName": selected_level.get(
            "databaseName",
            "",
        ),
        "startDialog": selected_level.get(
            "startDialog",
            "",
        ),
        "queryRestriction": deepcopy(
            query_restriction
        ),
        "items": deepcopy(
            items
        ),
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
