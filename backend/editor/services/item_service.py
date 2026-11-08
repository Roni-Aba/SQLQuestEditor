import json

from .. import database
from ..database import EDITOR_TO_JSON_TYPES

def build_item_for_json(saved_level):
    item_data = saved_level.get(
        "item",
        {},
    )

    unlock_condition = saved_level.get(
        "unlockCondition",
        {},
    )

    position = saved_level.get(
        "position",
        {},
    )

    required_items = item_data.get(
        "unlockedItems",
        unlock_condition.get("requiredItems", []),
    )

    failure_hints = unlock_condition.get(
        "failureHints",
        [],
    )

    unlock_hints = []

    requires_password = unlock_condition.get(
        "requiresPassword",
        False,
    )

    for hint in failure_hints:
        attempts = hint.get(
            "attempts"
        )

        message = hint.get(
            "message",
            "",
        )

        if attempts is None or not message:
            continue

        unlock_hints.append(
            {
                "numWrongAttempts": attempts,
                "hint": message,
            }
        )

    item = {
        "id": item_data.get(
            "id",
            "",
        ),
        "password": {
            "unlockPasswords": unlock_condition.get(
                "passwords",
                [],
            ),
            "passwordHint": unlock_condition.get(
                "passwordHint",
                "",
            ),
        },
        "neededItems": required_items,
        "type": item_data.get(
            "type",
            "",
        ),
        "unlocked": not requires_password,
        "boundingBoxImage": position.get(
            "boundingBoxImage",
            {
                "x": 0,
                "y": 0,
                "width": 0,
                "height": 0,
            },
        ),
        "boundingBoxIcon": position.get(
            "boundingBoxIcon",
            {
                "x": 0,
                "y": 0,
                "width": 0,
                "height": 0,
            },
        ),
        "unlockHints": unlock_hints,
        "nextDialog": {
            "afterUnlock": unlock_condition.get(
                "successMessage",
                "",
            ),
            "afterQuery": unlock_condition.get("afterQuery", ""),
        },
    }

    if item["type"] == "exit" and item_data.get("nextLevelId"):
        item["nextLevelId"] = item_data["nextLevelId"]

    if item["type"] == "table":
        table_name = str(
            item_data.get(
                "tableName",
                "",
            )
        ).strip()
        if not table_name:
            table_name = str(
                item_data.get(
                    "id",
                    "",
                )
            ).strip()
        item["tableName"] = table_name

        description = []

        columns = item_data.get(
            "columns",
            [],
        )

        if not isinstance(
            columns,
            list,
        ):
            columns = []

        for column in columns:
            if not isinstance(
                column,
                dict,
            ):
                continue

            column_id = str(
                column.get(
                    "id",
                    "",
                )
            ).strip()

            column_type = str(
                column.get(
                    "type",
                    "",
                )
            ).strip()

            if not column_id or not column_type:
                continue

            json_type = EDITOR_TO_JSON_TYPES.get(
                column_type,
                column_type,
            )

            description.append(
                f"{column_id} ({json_type})"
            )

        item["description"] = description

    if item["type"] == "hint":
        item["imageLink"] = item_data.get(
            "imageLink",
            "",
        )

        item["text"] = item_data.get(
            "text",
            "",
        )

    if item["type"] == "exit":
        item["nextDialog"]["afterUnlock"] = (
            item_data.get(
                "exitSuccessMessage",
                unlock_condition.get(
                    "successMessage",
                    "",
                ),
            )
        )
    return item


def save_current_item_to_new_level(
    saved_level,
):
    new_item = build_item_for_json(
        saved_level
    )

    if not new_item.get(
        "id"
    ):
        return saved_level

    items = saved_level.get(
        "items",
        [],
    )

    if not isinstance(
        items,
        list,
    ):
        items = []

    existing_index = None

    for index, item in enumerate(
        items
    ):
        if not isinstance(
            item,
            dict,
        ):
            continue

        if item.get(
            "id"
        ) == new_item.get(
            "id"
        ):
            existing_index = index
            break

    if existing_index is not None:
        items[existing_index] = new_item
    else:
        items.append(
            new_item
        )

    saved_level["items"] = items

    return saved_level


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

def remove_item_from_level(level_data, item_id):
    if not isinstance(level_data, dict):
        return {}

    items = level_data.get("items", [])
    if not isinstance(items, list):
        items = []

    cleaned_items = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("id") == item_id:
            continue

        needed_items = item.get("neededItems", [])
        if isinstance(needed_items, list):
            item["neededItems"] = [
                needed_item
                for needed_item in needed_items
                if needed_item != item_id
            ]

        unlocked_items = item.get("unlockedItems", [])
        if isinstance(unlocked_items, list):
            item["unlockedItems"] = [
                unlocked_item
                for unlocked_item in unlocked_items
                if unlocked_item != item_id
            ]

        unlock_condition = item.get("unlockCondition")
        if isinstance(unlock_condition, dict):
            required_items = unlock_condition.get("requiredItems", [])
            if isinstance(required_items, list):
                unlock_condition["requiredItems"] = [
                    required_item
                    for required_item in required_items
                    if required_item != item_id
                ]
        cleaned_items.append(item)

    level_data["items"] = cleaned_items

    current_item = level_data.get("item")
    if isinstance(current_item, dict) and current_item.get("id") == item_id:
        level_data.pop("item", None)
        level_data.pop("unlockCondition", None)
        level_data.pop("position", None)

    unlock_condition = level_data.get("unlockCondition")
    if isinstance(unlock_condition, dict):
        required_items = unlock_condition.get("requiredItems", [])
        if isinstance(required_items, list):
            unlock_condition["requiredItems"] = [
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