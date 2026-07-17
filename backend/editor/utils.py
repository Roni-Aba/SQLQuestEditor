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
    requires_password = unlock_condition.get("requiresPassword", False)
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
        "unlocked": not requires_password,
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


def get_item_options_for_current_level(saved_level):
    item_options = []
    seen_item_ids = set()
    for item in saved_level.get("items", []):
        item_id = item.get("id", "").strip()
        if not item_id:
            continue
        if item_id in seen_item_ids:
            continue
        item_options.append({
            "value": item_id,
            "label": item_id,
        })
        seen_item_ids.add(item_id)
    return item_options


def load_item_for_editing(saved_level, item_id):
    items = saved_level.get("items", [])
    selected_item = next(
        (
            item
            for item in items
            if item.get("id") == item_id
        ),
        None,
    )
    if selected_item is None:
        return None
    unlock_hints = selected_item.get("unlockHints", [])
    failure_hints = []
    for hint in unlock_hints:
        attempts = hint.get("numWrongAttempts")
        message = hint.get("hint", "")
        if attempts is None or not message:
            continue
        failure_hints.append(
            {
                "attempts": attempts,
                "message": message,
            }
        )
    password_data = selected_item.get("password", {})
    next_dialog = selected_item.get("nextDialog", {})
    item_data = {
        "id": selected_item.get("id", ""),
        "type": selected_item.get("type", ""),
        "unlockedItems": selected_item.get("neededItems", []),
    }
    item_type = selected_item.get("type", "")
    if item_type == "table":
        item_data["tableName"] = selected_item.get(
            "tableName",
            selected_item.get("id", ""),
        )

        item_data["columns"] = parse_table_description(
            selected_item.get("description", [])
        )
    elif item_type == "hint":
        item_data["text"] = selected_item.get("text", "")
        item_data["imageLink"] = selected_item.get(
            "imageLink",
            "",
        )
        has_text = bool(item_data["text"])
        has_image = bool(item_data["imageLink"])
        if has_text and has_image:
            item_data["hintType"] = "text_image"
        elif has_image:
            item_data["hintType"] = "image"
        else:
            item_data["hintType"] = "text"
    elif item_type == "exit":
        item_data["exitSuccessMessage"] = next_dialog.get(
            "afterUnlock",
            "",
        )

        item_data["nextLevelId"] = selected_item.get(
            "nextLevelId",
            "",
        )
    saved_level["item"] = item_data
    saved_level["unlockCondition"] = {
        "requiredItems": selected_item.get("neededItems", []),
        "requiresPassword": not selected_item.get(
            "unlocked",
            True,
        ),
        "passwords": password_data.get(
            "unlockPasswords",
            [],
        ),
        "passwordHint": password_data.get(
            "passwordHint",
            "",
        ),
        "successMessage": next_dialog.get(
            "afterUnlock",
            "",
        ),
        "failureHints": failure_hints,
        "showHintsOnFailure": bool(failure_hints),
    }
    saved_level["position"] = {
        "boundingBoxImage": selected_item.get(
            "boundingBoxImage",
            {
                "x": 0,
                "y": 0,
                "width": 0,
                "height": 0,
            },
        ),
        "boundingBoxIcon": selected_item.get(
            "boundingBoxIcon",
            {
                "x": 0,
                "y": 0,
                "width": 0,
                "height": 0,
            },
        ),
    }

    return selected_item


def parse_table_description(description):
    type_mapping = {
        "varchar": "text",
        "text": "text",
        "int": "number",
        "integer": "number",
        "number": "number",
        "date": "date",
        "bool": "boolean",
        "boolean": "boolean",
    }
    columns = []
    for entry in description:
        entry = str(entry).strip()
        if not entry:
            continue
        if "(" not in entry or not entry.endswith(")"):
            columns.append(
                {
                    "id": entry,
                    "type": "text",
                }
            )
            continue
        column_id, raw_type = entry.rsplit("(", 1)
        column_id = column_id.strip()
        raw_type = raw_type[:-1].strip().lower()
        if not column_id:
            continue
        columns.append(
            {
                "id": column_id,
                "type": type_mapping.get(
                    raw_type,
                    raw_type,
                ),
            }
        )

    return columns