from .. import database, utils
import json

def clear_item_draft(saved_level):
    for key in ("item", "unlockCondition", "position"):
        saved_level.pop(key, None)


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
