def build_item_for_json(saved_level):
    item_data = saved_level.get("item", {})
    unlock_condition = saved_level.get("unlockCondition", {})
    position = saved_level.get("position", {})

    required_items = unlock_condition.get(
        "requiredItems",
        item_data.get("unlockedItems", [])
    )
    failure_hints = unlock_condition.get("failureHints", [])
    unlock_hints = []
    for hint in failure_hints:
        attempts = hint.get("attempts")
        message = hint.get("message", "")
        if attempts is None or not message:
            continue
        unlock_hints.append({
            "numWrongAttempts": attempts,
            "hint": message,
        })
    item = {
        "id": item_data.get("id", ""),
        "password": {
            "unlockPasswords": unlock_condition.get("passwords", []),
            "passwordHint": unlock_condition.get("passwordHint", ""),
        },
        "neededItems": required_items,
        "type": item_data.get("type", ""),
        "unlocked": item_data.get("unlocked", False),
        "boundingBoxImage": position.get("boundingBoxImage", {
            "x": 0,
            "y": 0,
            "width": 0,
            "height": 0,
        }),
        "boundingBoxIcon": position.get("boundingBoxIcon", {
            "x": 0,
            "y": 0,
            "width": 0,
            "height": 0,
        }),
        "unlockHints": unlock_hints,
        "nextDialog": {
            "afterUnlock": unlock_condition.get("successMessage", ""),
            "afterQuery": "",
        },
    }
    if item["type"] == "table":
        item["tableName"] = item_data.get("tableName", item_data.get("id", ""))
        type_mapping = {
            "text": "varchar",
            "number": "int",
            "date": "date",
            "boolean": "bool",
        }
        description = []
        for column in item_data.get("columns", []):
            column_id = column.get("id", "")
            column_type = column.get("type", "")
            if not column_id or not column_type:
                continue
            json_type = type_mapping.get(column_type, column_type)
            description.append(f"{column_id} ({json_type})")
        item["description"] = description
    if item["type"] == "hint":
        item["imageLink"] = item_data.get("imageLink", "")
        item["text"] = item_data.get("text", "")
    if item["type"] == "exit":
        item["nextDialog"]["afterUnlock"] = item_data.get(
            "exitSuccessMessage",
            unlock_condition.get("successMessage", "")
        )
        #item["nextLevelId"] = item_data.get("nextLevelId", "")
    return item

def save_current_item_to_new_level(saved_level):
    new_item = build_item_for_json(saved_level)
    if not new_item.get("id"):
        return saved_level
    items = saved_level.get("items", [])
    existing_index = None
    for index, item in enumerate(items):
        if item.get("id") == new_item.get("id"):
            existing_index = index
            break
    if existing_index is not None:
        items[existing_index] = new_item
    else:
        items.append(new_item)
    saved_level["items"] = items
    return saved_level

def save_new_level_to_game_json(request):
    game_json = request.session.get("game_json", {})
    saved_level = request.session.get("new_level", {})
    saved_level = save_current_item_to_new_level(saved_level)
    level_id = saved_level.get("id", "")
    if not level_id:
        return game_json, saved_level
    new_level = {
        "id": saved_level.get("id", ""),
        "levelPicture": saved_level.get("levelPicture", ""),
        "databaseName": saved_level.get(
            "databaseName",
            saved_level.get("id", "")
        ) + ".db",
        "startDialog": saved_level.get("startDialog", ""),
        "queryRestriction": saved_level.get("queryRestriction", {}),
        "items": saved_level.get("items", []),
    }
    levels = game_json.get("level", [])
    existing_index = None
    for index, level in enumerate(levels):
        if level.get("id") == level_id:
            existing_index = index
            break
    if existing_index is not None:
        levels[existing_index] = new_level
    else:
        levels.append(new_level)
    game_json["level"] = levels
    request.session["game_json"] = game_json
    request.session["new_level"] = saved_level
    request.session.modified = True
    return game_json, saved_level