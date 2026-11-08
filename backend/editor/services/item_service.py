import json
from copy import deepcopy

from .. import database
from ..database import EDITOR_TO_JSON_TYPES, editor_columns_from_description
from .assets import save_uploaded_image


SUPPORTED_ITEM_FIELDS = {
    "id", "password", "neededItems", "type", "unlocked",
    "boundingBoxImage", "boundingBoxIcon", "unlockHints",
    "nextDialog", "tableName", "description", "imageLink",
    "text", "nextLevelId",
}


# Entwurf und Zusammenfassung

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


def get_item_summary(saved_level):
    item = saved_level.get("item", {})
    unlock_condition = saved_level.get("unlockCondition", {})
    position = saved_level.get("position", {})

    return {
        "item_name": item.get("id", ""),
        "required_items": unlock_condition.get(
            "requiredItems", item.get("unlockedItems", [])
        ),
        "passwords": unlock_condition.get("passwords", []),
        "password_hint": unlock_condition.get("passwordHint", ""),
        "success_message": unlock_condition.get("successMessage", ""),
        "failure_hints": unlock_condition.get("failureHints", []),
        "bounding_box_image": position.get("boundingBoxImage", {}),
        "bounding_box_icon": position.get("boundingBoxIcon", {}),
        "item_type": item.get("type", ""),
        "table_name": item.get("tableName", ""),
        "columns": item.get("columns", []),
        "text": item.get("text", ""),
        "image_link": item.get("imageLink", ""),
        "exit_success_message": item.get("exitSuccessMessage", ""),
        "next_level_id": item.get("nextLevelId", ""),
    }


# Typ und Inhalte

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


def update_hint_field(item, post_data):
    hint_type = post_data.get("hint_type","").strip()
    hint_text = post_data.get("hint_text","").strip()

    if hint_type not in {"text", "image", "text_image"}:
        hint_type = "text"

    item["type"] = "hint"
    item["hintType"] = hint_type
    item["text"] = (
        hint_text if hint_type in {"text", "text_image"} else ""
    )
    return hint_type


def update_hint_image(item, saved_level, uploaded_image, hint_type, base_dir):
    if uploaded_image:
        filename, source_path = save_uploaded_image(uploaded_image, base_dir, "hints")

        item["imageLink"] = filename
        saved_level.setdefault("_new_asset_sources", {})[
            filename
        ] = source_path
    elif hint_type == "text":
        item["imageLink"] = ""


def update_exit_fields(item, post_data):
    item["type"] = "exit"
    item["exitSuccessMessage"] = post_data.get(
        "exit_success_message", ""
    ).strip()
    item["nextLevelId"] = post_data.get(
        "next_level_id", ""
    ).strip()


# Name und Voraussetzungen

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


# Passwort und Fehlversuchhinweise

def update_password_requirement(unlock_condition, selected_item, post_data):
    requires_password = (
        post_data.get("requires_password", "false") == "true"
    )

    unlock_condition["requiredItems"] = selected_item.get(
        "unlockedItems", []
    )
    unlock_condition["requiresPassword"] = requires_password

    if not requires_password:
        unlock_condition["passwords"] = []
        unlock_condition["passwordHint"] = ""
        unlock_condition["successMessage"] = ""
        unlock_condition["showHintsOnFailure"] = False
        unlock_condition["failureHints"] = []

    return requires_password


def update_password_details(unlock_condition, post_data):
    raw_passwords = post_data.get("item_passwords", "").strip()
    passwords = [
        password.strip()
        for password in raw_passwords.replace(",", "\n").splitlines()
        if password.strip()
    ]
    show_hints = post_data.get("show_hints", "false") == "true"

    unlock_condition["passwords"] = passwords
    unlock_condition["passwordHint"] = post_data.get(
        "password_hint", ""
    ).strip()
    unlock_condition["successMessage"] = post_data.get(
        "success_message", ""
    ).strip()
    unlock_condition["showHintsOnFailure"] = show_hints

    if not show_hints:
        unlock_condition["failureHints"] = []

    return show_hints


def failure_hints_from_post(post_data):
    failure_hints = []

    for attempts, text in zip(
        post_data.getlist("hint_attempts[]"),
        post_data.getlist("hint_texts[]"),
    ):
        attempts = attempts.strip()
        text = text.strip()

        if not attempts or not text or not attempts.isdigit():
            continue

        failure_hints.append({
            "attempts": int(attempts),
            "message": text,
        })

    return failure_hints


# Position

def _box_from_post(post_data, prefix):
    return {
        "x": int(post_data.get(f"{prefix}_x", "0")),
        "y": int(post_data.get(f"{prefix}_y", "0")),
        "width": int(post_data.get(f"{prefix}_width", "0")),
        "height": int(post_data.get(f"{prefix}_height", "0")),
    }


def position_from_post(post_data):
    return {
        "boundingBoxImage": _box_from_post(post_data, "image"),
        "boundingBoxIcon": _box_from_post(post_data, "icon"),
    }


def position_form_values(saved_level):
    position = saved_level.get("position", {})
    image = position.get("boundingBoxImage", {})
    icon = position.get("boundingBoxIcon", {})
    level_picture = saved_level.get("levelPicture", "")

    return {
        "level_picture_path": (
            f"editor/img/levels/{level_picture}"
            if level_picture else ""
        ),
        "image_x": image.get("x", ""),
        "image_y": image.get("y", ""),
        "image_width": image.get("width", ""),
        "image_height": image.get("height", ""),
        "icon_x": icon.get("x", ""),
        "icon_y": icon.get("y", ""),
        "icon_width": icon.get("width", ""),
        "icon_height": icon.get("height", ""),
    }


# Bearbeitung

def find_item(items, item_id):
    return next(
        (
            item
            for item in items
            if isinstance(item, dict) and item.get("id") == item_id
        ),
        None,
    )


def load_item_for_editing(saved_level, item_id, table_rows=None):
    items = saved_level.get("items", [])
    if not isinstance(items, list):
        return None

    selected_item = find_item(items, item_id)
    if selected_item is None:
        return None

    unlock_hints = selected_item.get("unlockHints", [])
    if not isinstance(unlock_hints, list):
        unlock_hints = []

    failure_hints = []
    for hint in unlock_hints:
        if not isinstance(hint, dict):
            continue

        attempts = hint.get("numWrongAttempts")
        message = hint.get("hint", "")
        if attempts is None or not message:
            continue

        failure_hints.append({"attempts": attempts, "message": message})

    password_data = selected_item.get("password", {})
    if not isinstance(password_data, dict):
        password_data = {}

    next_dialog = selected_item.get("nextDialog", {})
    if not isinstance(next_dialog, dict):
        next_dialog = {}

    item_data = {
        "id": selected_item.get("id", ""),
        "type": selected_item.get("type", ""),
        "unlockedItems": selected_item.get("neededItems", []),
    }
    item_type = selected_item.get("type", "")

    if item_type == "table":
        table_name = str(selected_item.get("tableName", "")).strip()
        if not table_name:
            table_name = str(selected_item.get("id", "")).strip()
        item_data["tableName"] = table_name
        item_data["columns"] = editor_columns_from_description(
            selected_item.get("description", [])
        )
        item_data["rows"] = table_rows if isinstance(table_rows, list) else []

    elif item_type == "hint":
        item_data["text"] = selected_item.get("text", "")
        item_data["imageLink"] = selected_item.get("imageLink", "")
        has_text = bool(item_data["text"])
        has_image = bool(item_data["imageLink"])

        if has_text and has_image:
            item_data["hintType"] = "text_image"
        elif has_image:
            item_data["hintType"] = "image"
        else:
            item_data["hintType"] = "text"

    elif item_type == "exit":
        item_data["exitSuccessMessage"] = next_dialog.get("afterUnlock", "")
        item_data["nextLevelId"] = selected_item.get("nextLevelId", "")

    saved_level["item"] = item_data
    saved_level["unlockCondition"] = {
        "requiredItems": selected_item.get("neededItems", []),
        "requiresPassword": not selected_item.get("unlocked", True),
        "passwords": password_data.get("unlockPasswords", []),
        "passwordHint": password_data.get("passwordHint", ""),
        "successMessage": next_dialog.get("afterUnlock", ""),
        "afterQuery": next_dialog.get("afterQuery", ""),
        "failureHints": failure_hints,
        "showHintsOnFailure": bool(failure_hints),
    }
    saved_level["position"] = {
        "boundingBoxImage": selected_item.get(
            "boundingBoxImage", {"x": 0, "y": 0, "width": 0, "height": 0}
        ),
        "boundingBoxIcon": selected_item.get(
            "boundingBoxIcon", {"x": 0, "y": 0, "width": 0, "height": 0}
        ),
    }
    return selected_item


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

    return load_item_for_editing(
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


# Löschen

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
