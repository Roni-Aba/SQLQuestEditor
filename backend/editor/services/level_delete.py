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
