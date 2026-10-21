from .. import database, utils

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
