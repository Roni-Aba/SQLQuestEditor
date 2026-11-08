from pathlib import Path
from copy import deepcopy


def prepare_game_json_for_export(
    game_json,
    base_dir,
    game_root=None,
    import_sources=None,
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
    game_root = Path(game_root) if game_root else None

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
        if level_folder.casefold() in used_level_names:
            raise ValueError(
                f'Die Levelnamen erzeugen denselben Exportordner "{level_folder}".'
            )
        used_level_names.add(
            level_folder.casefold()
        )
        original_level_folder = level_folder
        imported_source = (import_sources or {}).get(str(requested_level_id), {})
        imported_assets = imported_source.get("assets", {})
        imported_image_directories = []
        if game_root is not None:
            imported_image_directories = [
                game_root / original_level_folder / "assets",
                game_root / "assets",
                game_root,
            ]
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

            source_path = resolve_export_asset(
                clean_level_picture, imported_assets,
                level_image_directories + imported_image_directories,
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
        database_filename = database_name_for_level(
            requested_level_id,
            fallback=f"level{level_index}",
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

            item.pop("data", None)

            image_link = item.get(
                "imageLink",
                "",
            )

            if not image_link:
                continue

            clean_image_link = (sanitize_export_name(image_link,fallback="hint_image",))
            item["imageLink"] = (clean_image_link)
            source_path = resolve_export_asset(
                clean_image_link, imported_assets,
                item_image_directories + imported_image_directories,
            )

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


def database_name_for_level(level_id, fallback="level"):
    return f"{sanitize_export_name(level_id, fallback=fallback)}.db"

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


def resolve_export_asset(filename, imported_assets, possible_directories):
    if filename in imported_assets:
        source = Path(imported_assets[filename])
        if source.is_file():
            return source
        raise FileNotFoundError(f'Das Bild "{filename}" wurde nicht gefunden.')
    source = find_export_asset(filename, possible_directories)
    if source is None:
        raise FileNotFoundError(f'Das Bild "{filename}" wurde nicht gefunden.')
    return source
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
