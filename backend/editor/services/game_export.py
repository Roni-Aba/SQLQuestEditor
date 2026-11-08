import io
import json
import tempfile
import zipfile
from copy import deepcopy
from pathlib import Path, PurePosixPath

from .. import database, utils
from ..utils import database_name_for_level, find_export_asset, sanitize_export_name


def build_game_export(request, base_dir):
    game_json = request.session.get("game_json", {})
    if not isinstance(game_json, dict):
        game_json = {}

    export_game_json, asset_files = prepare_game_json_for_export(
        game_json,
        base_dir,
        request.session.get("game_root"),
        request.session.get("import_sources", {}),
    )

    zip_buffer = io.BytesIO()
    managed_archive_paths = {"SQLSpellQuest.json"}

    with tempfile.TemporaryDirectory() as temp_directory:
        with zipfile.ZipFile(
            zip_buffer, "w", zipfile.ZIP_DEFLATED
        ) as zip_file:
            write_level_databases(
                request,
                zip_file,
                export_game_json,
                Path(temp_directory),
                managed_archive_paths,
            )
            json_string = json.dumps(
                export_game_json, ensure_ascii=False, indent=2
            )
            zip_file.writestr("SQLSpellQuest.json", json_string)
            write_prepared_assets(zip_file, asset_files)
            write_imported_files(
                request, zip_file, asset_files, managed_archive_paths
            )

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def prepare_game_json_for_export(
    game_json, base_dir, game_root=None, import_sources=None
):
    if not isinstance(game_json, dict):
        game_json = {}

    export_game_json = deepcopy(game_json)
    asset_files = {}
    base_dir = Path(base_dir)
    game_root = Path(game_root) if game_root else None

    level_image_directories = [
        base_dir / "editor" / "static" / "editor" / "img" / "levels",
    ]
    item_image_directories = [
        base_dir / "editor" / "static" / "editor" / "img" / "hints",
        base_dir / "editor" / "static" / "editor" / "img" / "items",
        base_dir / "editor" / "static" / "editor" / "img",
    ]

    levels = export_game_json.get("level", [])
    if not isinstance(levels, list):
        levels = []
        export_game_json["level"] = levels

    used_level_names = set()
    for level_index, level in enumerate(levels):
        if not isinstance(level, dict):
            continue

        requested_level_id = level.get("id", f"level{level_index}")
        level_folder = sanitize_export_name(
            requested_level_id, fallback=f"level{level_index}"
        )
        if level_folder.casefold() in used_level_names:
            raise ValueError(
                f'Die Levelnamen erzeugen denselben Exportordner "{level_folder}".'
            )
        used_level_names.add(level_folder.casefold())

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
        level_picture = level.get("levelPicture", "")
        if level_picture:
            clean_level_picture = sanitize_export_name(
                level_picture, fallback="level_background"
            )
            level["levelPicture"] = clean_level_picture
            source_path = resolve_export_asset(
                clean_level_picture,
                imported_assets,
                level_image_directories + imported_image_directories,
            )
            if source_path is not None:
                exported_filename = _reserve_asset_filename(
                    clean_level_picture, source_path, level_asset_names
                )
                archive_path = f"{level_folder}/assets/{exported_filename}"
                asset_files[archive_path] = source_path
                level["levelPicture"] = exported_filename

        database_filename = database_name_for_level(
            requested_level_id, fallback=f"level{level_index}"
        )
        level["databaseName"] = database_filename

        items = level.get("items", [])
        if not isinstance(items, list):
            items = []
            level["items"] = items

        for item in items:
            if not isinstance(item, dict):
                continue

            item.pop("data", None)
            image_link = item.get("imageLink", "")
            if not image_link:
                continue

            clean_image_link = sanitize_export_name(image_link, fallback="hint_image")
            item["imageLink"] = clean_image_link
            source_path = resolve_export_asset(
                clean_image_link,
                imported_assets,
                item_image_directories + imported_image_directories,
            )
            exported_filename = _reserve_asset_filename(
                clean_image_link, source_path, level_asset_names
            )
            archive_path = f"{level_folder}/assets/{exported_filename}"
            asset_files[archive_path] = source_path
            item["imageLink"] = exported_filename

        level["_exportFolder"] = level_folder

    return export_game_json, asset_files


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
