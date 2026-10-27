from copy import deepcopy

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
