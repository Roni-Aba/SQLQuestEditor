from pathlib import PurePosixPath

from .. import database, utils


def select_game_json_entry(uploaded_entries):
    json_candidates = [
        (game_file, relative_name)
        for game_file, relative_name in uploaded_entries
        if PurePosixPath(
            str(relative_name).replace("\\", "/")
        ).suffix.lower() == ".json"
    ]
    preferred_json_names = {"sqlspellquest.json", "game.json"}

    return next(
        (
            (game_file, relative_name)
            for game_file, relative_name in json_candidates
            if PurePosixPath(
                str(relative_name).replace("\\", "/")
            ).name.lower() in preferred_json_names
        ),
        json_candidates[0] if len(json_candidates) == 1 else None,
    )


def copy_uploaded_files(workspace_path, uploaded_entries):
    seen_paths = set()

    for game_file, submitted_relative_name in uploaded_entries:
        relative_name = str(submitted_relative_name).replace("\\", "/")
        relative_path = PurePosixPath(relative_name)

        if (
            relative_path.is_absolute()
            or not relative_path.parts
            or ".." in relative_path.parts
        ):
            raise ValueError("Ungültiger Dateipfad im Spielordner.")

        normalized_path = str(relative_path).casefold()
        if normalized_path in seen_paths:
            raise ValueError(
                f'Der Dateipfad "{relative_name}" ist doppelt vorhanden.'
            )
        seen_paths.add(normalized_path)

        target_path = workspace_path.joinpath(*relative_path.parts)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        game_file.seek(0)
        with target_path.open("xb") as target_file:
            for chunk in game_file.chunks():
                target_file.write(chunk)


def build_import_sources(request, game_json, game_root):
    import_sources = {}
    for level in game_json.get("level", []):
        if not isinstance(level, dict):
            continue

        level_id = str(level.get("id", ""))
        database_path = database.get_level_database_path(request, level)
        level_folder = utils.sanitize_export_name(level_id, "level")
        asset_paths = {}
        level_items = level.get("items", [])
        if not isinstance(level_items, list):
            level_items = []

        for reference in [level.get("levelPicture", ""), *[
            item.get("imageLink", "") for item in level_items
            if isinstance(item, dict)
        ]]:
            if not reference:
                continue
            filename = utils.sanitize_export_name(reference)
            source = utils.find_export_asset(filename, [
                game_root / level_folder / "assets",
                game_root / "assets",
                game_root,
            ])
            if source is not None:
                asset_paths[filename] = str(source)
            else:
                asset_paths[filename] = str(
                    game_root / level_folder / "assets" / filename
                )

        import_sources[level_id] = {
            "folder": level_folder,
            "database": str(database_path) if database_path else "",
            "tables": {
                database.table_name_for(item): database.table_name_for(item)
                for item in level_items
                if isinstance(item, dict) and item.get("type") == "table"
            },
            "assets": asset_paths,
        }
    return import_sources


def build_import_manifest(game_root, import_sources):
    return {
        "files": [
            path.relative_to(game_root).as_posix()
            for path in game_root.rglob("*") if path.is_file()
        ],
        "folders": [source["folder"] for source in import_sources.values()],
        "databases": [
            source["database"] for source in import_sources.values()
            if source["database"]
        ],
    }
