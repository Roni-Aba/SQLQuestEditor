from .. import database
import json

def clear_item_draft(saved_level):
    for key in ("item", "unlockCondition", "position"):
        saved_level.pop(key, None)


def get_item_options_for_current_level(
    saved_level,
):
    item_options = []
    seen_item_ids = set()

    items = saved_level.get(
        "items",
        [],
    )

    if not isinstance(
        items,
        list,
    ):
        return item_options

    for item in items:
        if not isinstance(
            item,
            dict,
        ):
            continue

        item_id = str(
            item.get(
                "id",
                "",
            )
        ).strip()

        if not item_id:
            continue

        if item_id in seen_item_ids:
            continue

        item_options.append(
            {
                "value": item_id,
                "label": item_id,
            }
        )

        seen_item_ids.add(
            item_id
        )

    return item_options


def item_type_and_next_view(post_data):
    next_views = {
        "table": "create_level3table",
        "hint": "create_level3hint",
        "exit": "create_level3exit",
    }
    item_type = post_data.get("item_type", "").strip()
    if item_type not in next_views:
        item_type = "table"
    return item_type, next_views[item_type]

def clear_table_data_on_type_change(request, saved_level, item, new_type):
    if item.get("type") != "table" or new_type == "table":
        return

    table_name = database.get_editor_table_key(item)
    if not request.session.get("editing_item_id"):
        database.remove_editor_table_rows(
            request,
            saved_level,
            table_name,
        )

    for key in ("tableName", "columns", "rows"):
        item.pop(key, None)

def parse_unlocked_item(raw_value):
    try:
        items = json.loads(raw_value)
    except json.JSONDecodeError:
        return []
    return items if isinstance(items, list) else []

def has_item_name_conflict(saved_level, item, item_name, editing_item_id):
    existing_items = saved_level.get("items", [])
    if not isinstance(existing_items, list):
        return False

    return any(
        isinstance(existing_item, dict)
        and existing_item.get("id") != editing_item_id
        and (
            str(existing_item.get("id", "")).strip() == item_name
            or (
                item.get("type") == "table"
                and str(existing_item.get("tableName", "")).strip()
                == item_name
            )
        )
        for existing_item in existing_items
    )


def set_item_requirements(saved_level, item, unlocked_items):
    item["unlockedItems"] = [
        str(item_id).strip()
        for item_id in unlocked_items
        if str(item_id).strip()
    ]
    unlock_condition = saved_level.get("unlockCondition")
    if isinstance(unlock_condition, dict):
        unlock_condition["requiredItems"] = item["unlockedItems"]


def set_item_name_and_sync_table(request, saved_level, item, item_name):
    old_table_name = (
        database.table_name_for(item)
        if item.get("type") == "table"
        else ""
    )
    item["id"] = item_name
    if item.get("type") == "table":
        item["tableName"] = item_name
        if not request.session.get("item_edit_mode"):
            database.finalize_editor_table_rows(
                request,
                saved_level,
                item,
            )
            database.move_editor_table_rows(
                request,
                saved_level,
                old_table_name,
                item_name,
            )

def remove_item_from_level(
    level_data,
    item_id,
):
    if not isinstance(
        level_data,
        dict,
    ):
        return {}

    items = level_data.get(
        "items",
        [],
    )

    if not isinstance(
        items,
        list,
    ):
        items = []

    cleaned_items = []

    for item in items:
        if not isinstance(
            item,
            dict,
        ):
            continue

        if item.get(
            "id"
        ) == item_id:
            continue

        needed_items = item.get(
            "neededItems",
            [],
        )

        if isinstance(
            needed_items,
            list,
        ):
            item["neededItems"] = [
                needed_item
                for needed_item in needed_items
                if needed_item != item_id
            ]

        unlocked_items = item.get(
            "unlockedItems",
            [],
        )

        if isinstance(
            unlocked_items,
            list,
        ):
            item["unlockedItems"] = [
                unlocked_item
                for unlocked_item in unlocked_items
                if unlocked_item != item_id
            ]

        unlock_condition = item.get(
            "unlockCondition"
        )

        if isinstance(
            unlock_condition,
            dict,
        ):
            required_items = (
                unlock_condition.get(
                    "requiredItems",
                    [],
                )
            )

            if isinstance(
                required_items,
                list,
            ):
                unlock_condition[
                    "requiredItems"
                ] = [
                    required_item
                    for required_item in required_items
                    if required_item != item_id
                ]

        cleaned_items.append(
            item
        )

    level_data["items"] = (
        cleaned_items
    )

    current_item = level_data.get(
        "item"
    )

    if (
        isinstance(
            current_item,
            dict,
        )
        and current_item.get(
            "id"
        ) == item_id
    ):
        level_data.pop(
            "item",
            None,
        )

        level_data.pop(
            "unlockCondition",
            None,
        )

        level_data.pop(
            "position",
            None,
        )

    unlock_condition = level_data.get(
        "unlockCondition"
    )

    if isinstance(
        unlock_condition,
        dict,
    ):
        required_items = (
            unlock_condition.get(
                "requiredItems",
                [],
            )
        )

        if isinstance(
            required_items,
            list,
        ):
            unlock_condition[
                "requiredItems"
            ] = [
                required_item
                for required_item in required_items
                if required_item != item_id
            ]

    return level_data


def remove_item_from_game_levels(levels, level_id, item_id):
    updated_levels = []

    for level in levels:
        if isinstance(level, dict) and level.get("id") == level_id:
            level = remove_item_from_level(level, item_id)
        updated_levels.append(level)

    return updated_levels

def remove_deleted_table_rows(request, saved_level, item_id):
    deleted_item = next(
        (
            item
            for item in saved_level.get("items", [])
            if isinstance(item, dict) and item.get("id") == item_id
        ),
        None,
    )

    if not isinstance(deleted_item, dict) or deleted_item.get("type") != "table":
        return

    table_name = str(
        deleted_item.get("tableName", deleted_item.get("id", ""))
    ).strip()
    database.remove_editor_table_rows(request, saved_level, table_name)