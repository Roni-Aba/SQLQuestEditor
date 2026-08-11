from pathlib import Path
from copy import deepcopy
def prepare_game_json_for_export(
    game_json,
    base_dir,
):
    if not isinstance(
        game_json,
        dict,
    ):
        game_json = {}

    export_game_json = deepcopy(
        game_json
    )

    asset_files = {}

    base_dir = Path(
        base_dir
    )

    level_image_directories = [
        (
            base_dir
            / "editor"
            / "static"
            / "editor"
            / "img"
            / "levels"
        ),
    ]

    item_image_directories = [
        (
            base_dir
            / "editor"
            / "static"
            / "editor"
            / "img"
            / "hints"
        ),
        (
            base_dir
            / "editor"
            / "static"
            / "editor"
            / "img"
            / "items"
        ),
        (
            base_dir
            / "editor"
            / "static"
            / "editor"
            / "img"
        ),
    ]
    levels = export_game_json.get(
        "level",
        [],
    )
    if not isinstance(
        levels,
        list,
    ):
        levels = []
        export_game_json["level"] = levels
    used_level_names = set()
    for level_index, level in enumerate(
        levels
    ):
        if not isinstance(
            level,
            dict,
        ):
            continue
        requested_level_id = level.get(
            "id",
            f"level{level_index}",
        )
        level_folder = sanitize_export_name(
            requested_level_id,
            fallback=f"level{level_index}",
        )
        original_level_folder = level_folder
        counter = 2
        while level_folder in used_level_names:
            level_folder = (
                f"{original_level_folder}_"
                f"{counter}"
            )
            counter += 1
        used_level_names.add(
            level_folder
        )
        level_asset_names = {}
        level_picture = level.get(
            "levelPicture",
            "",
        )

        if level_picture:
            clean_level_picture = (
                sanitize_export_name(
                    level_picture,
                    fallback="level_background",
                )
            )

            level["levelPicture"] = (
                clean_level_picture
            )

            source_path = find_export_asset(
                clean_level_picture,
                level_image_directories,
            )

            if source_path is not None:
                exported_filename = (
                    _reserve_asset_filename(
                        clean_level_picture,
                        source_path,
                        level_asset_names,
                    )
                )

                archive_path = (
                    f"{level_folder}/assets/"
                    f"{exported_filename}"
                )

                asset_files[
                    archive_path
                ] = source_path
                level["levelPicture"] = (
                    exported_filename
                )
        database_filename = (
            f"{level_folder}.db"
        )

        level["databaseName"] = (
            database_filename
        )

        items = level.get(
            "items",
            [],
        )

        if not isinstance(
            items,
            list,
        ):
            items = []
            level["items"] = items

        for item in items:
            if not isinstance(
                item,
                dict,
            ):
                continue

            image_link = item.get(
                "imageLink",
                "",
            )

            if not image_link:
                continue

            clean_image_link = (sanitize_export_name(image_link,fallback="hint_image",))
            item["imageLink"] = (clean_image_link)
            source_path = find_export_asset(
                clean_image_link,
                item_image_directories,
            )

            if source_path is None:
                continue

            exported_filename = (
                _reserve_asset_filename(
                    clean_image_link,
                    source_path,
                    level_asset_names,
                )
            )

            archive_path = (
                f"{level_folder}/assets/"
                f"{exported_filename}"
            )

            asset_files[
                archive_path
            ] = source_path

            item["imageLink"] = (
                exported_filename
            )

        level["_exportFolder"] = (
            level_folder
        )

    return (
        export_game_json,
        asset_files,
    )
def sanitize_export_name(
    value,
    fallback="file",
):
    from pathlib import Path

    clean_name = Path(
        str(value or "")
    ).name.strip()

    if not clean_name:
        clean_name = fallback

    invalid_characters = (
        '<>:"/\\|?*'
    )

    for character in invalid_characters:
        clean_name = clean_name.replace(
            character,
            "_",
        )

    return clean_name

def find_export_asset(
    filename,
    possible_directories,
):
    from pathlib import Path
    if not filename:
        return None
    clean_filename = Path(
        str(filename)
    ).name
    for directory in possible_directories:
        candidate = (
            Path(directory)
            / clean_filename
        )
        if candidate.is_file():
            return candidate
    return None
def _reserve_asset_filename(
    requested_filename,
    source_path,
    level_asset_names,
):

    requested_filename = sanitize_export_name(
        requested_filename,
        fallback="asset",
    )

    current_source = level_asset_names.get(
        requested_filename
    )

    if (
        current_source is None
        or current_source == source_path
    ):
        level_asset_names[
            requested_filename
        ] = source_path

        return requested_filename

    requested_path = Path(
        requested_filename
    )

    stem = (
        requested_path.stem
        or "asset"
    )

    suffix = requested_path.suffix
    counter = 2

    while True:
        candidate = (
            f"{stem}_{counter}{suffix}"
        )

        if candidate not in level_asset_names:
            level_asset_names[
                candidate
            ] = source_path

            return candidate

        if (
            level_asset_names[candidate]
            == source_path
        ):
            return candidate

        counter += 1

def convert_table_cell_value(
    raw_value,
    column_type,
):
    if column_type == "boolean":
        if isinstance(raw_value, bool):
            return raw_value

        normalized_value = str(
            raw_value
        ).strip().lower()

        return normalized_value in {
            "true",
            "1",
            "yes",
            "on",
            "ja",
        }

    if raw_value is None:
        return ""

    normalized_value = str(
        raw_value
    ).strip()

    if column_type == "number":
        if normalized_value == "":
            return ""

        try:
            if "." in normalized_value:
                return float(normalized_value)

            return int(normalized_value)

        except ValueError:
            return normalized_value

    return normalized_value


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

    required_items = unlock_condition.get(
        "requiredItems",
        item_data.get(
            "unlockedItems",
            [],
        ),
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
            "afterQuery": "",
        },
    }

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

        type_mapping = {
            "text": "varchar",
            "number": "int",
            "date": "date",
            "boolean": "bool",
        }

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

            json_type = type_mapping.get(
                column_type,
                column_type,
            )

            description.append(
                f"{column_id} ({json_type})"
            )

        item["description"] = description

        item["data"] = []

        rows = item_data.get(
            "rows",
            [],
        )

        if not isinstance(
            rows,
            list,
        ):
            rows = []

        for row in rows:
            if not isinstance(
                row,
                dict,
            ):
                continue

            cleaned_row = {}
            row_has_value = False

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
                        "text",
                    )
                ).strip()

                if not column_id:
                    continue

                cleaned_value = (
                    convert_table_cell_value(
                        row.get(
                            column_id,
                            "",
                        ),
                        column_type,
                    )
                )

                if column_type == "boolean":
                    if cleaned_value is True:
                        row_has_value = True
                elif cleaned_value not in (
                    "",
                    None,
                ):
                    row_has_value = True

                cleaned_row[column_id] = (
                    cleaned_value
                )

            if cleaned_row and row_has_value:
                item["data"].append(
                    cleaned_row
                )

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


def save_new_level_to_game_json(
    request,
):
    game_json = request.session.get(
        "game_json",
        {},
    )

    if not isinstance(
        game_json,
        dict,
    ):
        game_json = {}

    saved_level = request.session.get(
        "new_level",
        {},
    )

    if not isinstance(
        saved_level,
        dict,
    ):
        saved_level = {}

    saved_level = (
        save_current_item_to_new_level(
            saved_level
        )
    )

    level_id = saved_level.get(
        "id",
        "",
    )

    if not level_id:
        return game_json, saved_level

    database_name = saved_level.get(
        "databaseName",
        saved_level.get(
            "id",
            "",
        ),
    )

    if database_name and not database_name.endswith(
        ".db"
    ):
        database_name = (
            f"{database_name}.db"
        )

    new_level = {
        "id": saved_level.get(
            "id",
            "",
        ),
        "levelPicture": saved_level.get(
            "levelPicture",
            "",
        ),
        "databaseName": database_name,
        "startDialog": saved_level.get(
            "startDialog",
            "",
        ),
        "queryRestriction": saved_level.get(
            "queryRestriction",
            {},
        ),
        "items": saved_level.get(
            "items",
            [],
        ),
    }

    levels = game_json.get(
        "level",
        [],
    )

    if not isinstance(
        levels,
        list,
    ):
        levels = []

    existing_index = None

    for index, level in enumerate(
        levels
    ):
        if not isinstance(
            level,
            dict,
        ):
            continue

        if level.get(
            "id"
        ) == level_id:
            existing_index = index
            break

    if existing_index is not None:
        levels[existing_index] = new_level
    else:
        levels.append(
            new_level
        )

    game_json["level"] = levels

    request.session["game_json"] = (
        game_json
    )

    request.session["new_level"] = (
        saved_level
    )

    request.session.modified = True

    return game_json, saved_level


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


def load_item_for_editing(
    saved_level,
    item_id,
):
    items = saved_level.get(
        "items",
        [],
    )

    if not isinstance(
        items,
        list,
    ):
        return None

    selected_item = next(
        (
            item
            for item in items
            if (
                isinstance(
                    item,
                    dict,
                )
                and item.get(
                    "id"
                ) == item_id
            )
        ),
        None,
    )

    if selected_item is None:
        return None

    unlock_hints = selected_item.get(
        "unlockHints",
        [],
    )

    if not isinstance(
        unlock_hints,
        list,
    ):
        unlock_hints = []

    failure_hints = []

    for hint in unlock_hints:
        if not isinstance(
            hint,
            dict,
        ):
            continue

        attempts = hint.get(
            "numWrongAttempts"
        )

        message = hint.get(
            "hint",
            "",
        )

        if attempts is None or not message:
            continue

        failure_hints.append(
            {
                "attempts": attempts,
                "message": message,
            }
        )

    password_data = selected_item.get(
        "password",
        {},
    )

    if not isinstance(
        password_data,
        dict,
    ):
        password_data = {}

    next_dialog = selected_item.get(
        "nextDialog",
        {},
    )

    if not isinstance(
        next_dialog,
        dict,
    ):
        next_dialog = {}

    item_data = {
        "id": selected_item.get(
            "id",
            "",
        ),
        "type": selected_item.get(
            "type",
            "",
        ),
        "unlockedItems": selected_item.get(
            "neededItems",
            [],
        ),
    }

    item_type = selected_item.get(
        "type",
        "",
    )

    if item_type == "table":
        table_name = str(
            selected_item.get(
                "tableName",
                "",
            )
        ).strip()
        if not table_name:
            table_name = str(
                selected_item.get(
                    "id",
                    "",
                )
            ).strip()
        item_data["tableName"] = table_name

        item_data["columns"] = (
            parse_table_description(
                selected_item.get(
                    "description",
                    [],
                )
            )
        )

        table_data = selected_item.get(
            "data",
            [],
        )

        if not isinstance(
            table_data,
            list,
        ):
            table_data = []

        item_data["rows"] = table_data

    elif item_type == "hint":
        item_data["text"] = (
            selected_item.get(
                "text",
                "",
            )
        )

        item_data["imageLink"] = (
            selected_item.get(
                "imageLink",
                "",
            )
        )

        has_text = bool(
            item_data["text"]
        )

        has_image = bool(
            item_data["imageLink"]
        )

        if has_text and has_image:
            item_data["hintType"] = (
                "text_image"
            )

        elif has_image:
            item_data["hintType"] = (
                "image"
            )

        else:
            item_data["hintType"] = (
                "text"
            )

    elif item_type == "exit":
        item_data[
            "exitSuccessMessage"
        ] = next_dialog.get(
            "afterUnlock",
            "",
        )

        item_data[
            "nextLevelId"
        ] = selected_item.get(
            "nextLevelId",
            "",
        )

    saved_level["item"] = item_data

    saved_level[
        "unlockCondition"
    ] = {
        "requiredItems": selected_item.get(
            "neededItems",
            [],
        ),
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
        "showHintsOnFailure": bool(
            failure_hints
        ),
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


def parse_table_description(
    description,
):
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

    if not isinstance(
        description,
        list,
    ):
        return columns

    for entry in description:
        entry = str(
            entry
        ).strip()

        if not entry:
            continue

        if (
            "(" not in entry
            or not entry.endswith(
                ")"
            )
        ):
            columns.append(
                {
                    "id": entry,
                    "type": "text",
                }
            )

            continue

        column_id, raw_type = (
            entry.rsplit(
                "(",
                1,
            )
        )

        column_id = column_id.strip()

        raw_type = (
            raw_type[:-1]
            .strip()
            .lower()
        )

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
