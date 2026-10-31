from pathlib import Path, PurePosixPath

from .. import database, utils


def write_level_databases(
    request, zip_file, export_game_json, temp_directory, managed_archive_paths
):
    levels = export_game_json.get("level", [])
    if not isinstance(levels, list):
        levels = []

    for level_index, level in enumerate(levels):
        if not isinstance(level, dict):
            continue

        level_id = level.get("id", f"level{level_index}")
        level_folder = level.pop(
            "_exportFolder",
            utils.sanitize_export_name(level_id, fallback=f"level{level_index}"),
        )
        safe_level_id = utils.sanitize_export_name(
            level_id, fallback=f"level{level_index}"
        )
        sql_archive_path = (
            f"{level_folder}/databases/create_{safe_level_id}.sql"
        )
        database_archive_path = (
            f"{level_folder}/databases/{level['databaseName']}"
        )
        managed_archive_paths.update(
            (sql_archive_path, database_archive_path)
        )

        database_path = temp_directory / f"{safe_level_id}_{level_index}.db"
        level_table_rows = database.get_export_table_rows(request, level)
        source = request.session.get("import_sources", {}).get(str(level_id), {})
        if source and not source.get("database"):
            raise FileNotFoundError(
                f'Die Level-Datenbank für "{level_id}" wurde nicht gefunden.'
            )
        database.create_level_database(
            database_path,
            level,
            level_table_rows,
            source_database=source.get("database"),
            source_tables=source.get("tables"),
        )

        level_sql = database.database_dump(database_path)
        zip_file.writestr(sql_archive_path, level_sql)
        zip_file.write(database_path, database_archive_path)


def write_prepared_assets(zip_file, asset_files):
    for archive_path, source_path in asset_files.items():
        zip_file.write(source_path, archive_path)


def write_imported_files(request, zip_file, asset_files, managed_archive_paths):
    game_root_value = request.session.get("game_root")
    if not game_root_value:
        return

    game_root = Path(game_root_value)
    if not game_root.is_dir():
        raise FileNotFoundError("Der importierte Spielordner fehlt.")

    imported_sources = request.session.get("import_sources", {})
    manifest = request.session.get("import_manifest", {})
    managed_input_paths = {
        Path(path) for path in manifest.get("databases", [])
    }
    imported_json = request.session.get("import_json_path")
    if imported_json:
        managed_input_paths.add(Path(imported_json))

    active_folders = {
        source["folder"]: utils.sanitize_export_name(level_id)
        for level_id, source in imported_sources.items()
        if source.get("folder")
    }
    deliberate_replacements = {
        f'{utils.sanitize_export_name(level_id)}/assets/{filename}': Path(path)
        for level_id, source in imported_sources.items()
        for filename, path in source.get("replacements", {}).items()
    }
    all_folders = set(manifest.get("folders", []))
    input_files = set(manifest.get("files", []))
    input_files.update(
        path.relative_to(game_root).as_posix()
        for path in game_root.rglob("*") if path.is_file()
    )

    for relative_name in sorted(input_files):
        input_path = game_root / relative_name
        parts = PurePosixPath(relative_name).parts
        if parts and parts[0] in all_folders and parts[0] not in active_folders:
            continue
        if not input_path.is_file():
            raise FileNotFoundError(
                f'Die importierte Datei "{relative_name}" fehlt.'
            )
        if input_path in managed_input_paths:
            continue
        if parts and parts[0] in active_folders:
            archive_path = PurePosixPath(
                active_folders[parts[0]], *parts[1:]
            ).as_posix()
        else:
            archive_path = relative_name
        if archive_path in managed_archive_paths:
            continue
        if archive_path in asset_files:
            if Path(asset_files[archive_path]) != input_path:
                if deliberate_replacements.get(archive_path) == Path(
                    asset_files[archive_path]
                ):
                    continue
                raise ValueError(
                    f'Die Datei "{archive_path}" würde im Export überschrieben.'
                )
            continue
        zip_file.write(input_path, archive_path)
