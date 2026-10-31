from copy import deepcopy

from .. import database, utils


SUPPORTED_ITEM_FIELDS = {
    "id", "password", "neededItems", "type", "unlocked",
    "boundingBoxImage", "boundingBoxIcon", "unlockHints",
    "nextDialog", "tableName", "description", "imageLink",
    "text", "nextLevelId",
}


def find_item(items, item_id):
    return next(
        (
            item
            for item in items
            if isinstance(item, dict) and item.get("id") == item_id
        ),
        None,
    )


def load_item_draft(request, saved_level, item_id):
    selected_item = find_item(saved_level.get("items", []), item_id)
    table_rows = None
    if isinstance(selected_item, dict) and selected_item.get("type") == "table":
        table_name = str(
            selected_item.get("tableName", selected_item.get("id", ""))
        ).strip()
        table_rows = database.get_editor_table_rows(
            request, saved_level, table_name
        )

    return utils.load_item_for_editing(
        saved_level, item_id, table_rows=table_rows
    )


def preserve_original_item_fields(current_item, original_item, saved_level):
    if not isinstance(original_item, dict):
        return

    if (
        current_item.get("type") == "exit"
        and "nextLevelId" in original_item
        and "nextLevelId" not in current_item
    ):
        current_item["nextLevelId"] = saved_level.get("item", {}).get(
            "nextLevelId", ""
        )

    for key, value in original_item.items():
        if key not in SUPPORTED_ITEM_FIELDS:
            current_item.setdefault(key, deepcopy(value))

    for key in ("password", "nextDialog", "boundingBoxImage", "boundingBoxIcon"):
        old_values = original_item.get(key)
        new_values = current_item.get(key)
        if isinstance(old_values, dict) and isinstance(new_values, dict):
            for nested_key, value in old_values.items():
                new_values.setdefault(nested_key, deepcopy(value))


def sync_edited_table_rows(request, saved_level, current_item, original_item):
    old_table_name = (
        database.table_name_for(original_item)
        if isinstance(original_item, dict) and original_item.get("type") == "table"
        else ""
    )
    if current_item.get("type") == "table":
        table_name = database.table_name_for(current_item)
        table_sources = saved_level.get("_import_table_sources", {})
        if old_table_name and old_table_name != table_name:
            original_name = table_sources.pop(old_table_name, None)
            if original_name:
                table_sources[table_name] = original_name
        saved_level["_import_table_sources"] = table_sources

        draft_rows = saved_level.get("item", {}).get("rows")
        if not isinstance(draft_rows, list):
            draft_rows = database.get_editor_table_rows(
                request, saved_level, old_table_name
            )
        database.set_editor_table_rows(
            request,
            saved_level,
            table_name,
            draft_rows,
            old_table_name=old_table_name,
        )
    elif old_table_name:
        database.remove_editor_table_rows(request, saved_level, old_table_name)


def replace_item_and_update_references(items, old_item_id, current_item):
    updated_items = []
    item_replaced = False

    for existing_item in items:
        if existing_item.get("id") == old_item_id:
            updated_items.append(current_item)
            item_replaced = True
        else:
            updated_items.append(existing_item)

    if not item_replaced:
        updated_items.append(current_item)

    if old_item_id != current_item.get("id"):
        for dependent in updated_items:
            if not isinstance(dependent, dict):
                continue
            needed_items = dependent.get("neededItems")
            if isinstance(needed_items, list):
                dependent["neededItems"] = [
                    current_item["id"] if needed == old_item_id else needed
                    for needed in needed_items
                ]

    return updated_items
