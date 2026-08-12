import json
import sqlite3
import tempfile
import uuid
from copy import deepcopy
from pathlib import Path


EDITOR_TABLE_ROWS_FILENAME = ".editor-table-rows.json"
EDITOR_LEVEL_DRAFT_KEY = "_editor_table_rows_key"
EDITOR_TABLE_DRAFT_KEY = "_editor_table_rows_table_key"

TYPE_MAPPING = {
    "text": "TEXT",
    "varchar": "TEXT",
    "date": "TEXT",
    "number": "INTEGER",
    "int": "INTEGER",
    "integer": "INTEGER",
    "boolean": "INTEGER",
    "bool": "INTEGER",
}


def quote_identifier(identifier):
    normalized_identifier = str(identifier).replace('"', '""')
    return f'"{normalized_identifier}"'


def sanitize_path_component(value, fallback):
    clean_value = Path(str(value or "")).name.strip() or fallback

    for character in '<>:"/\\|?*':
        clean_value = clean_value.replace(character, "_")

    return clean_value


def table_name_for(table_item):
    return str(
        table_item.get(
            "tableName",
            table_item.get("id", ""),
        )
    ).strip()


def get_editor_table_key(table_item):
    """Return a stable internal key while a table item has no name yet."""
    table_name = table_name_for(table_item)
    if table_name:
        return table_name

    draft_key = str(
        table_item.get(EDITOR_TABLE_DRAFT_KEY, "")
    ).strip()
    if draft_key:
        return draft_key

    draft_key = f"table-{uuid.uuid4().hex}"
    table_item[EDITOR_TABLE_DRAFT_KEY] = draft_key
    return draft_key


def start_new_editor_workspace(request):
    workspace_path = Path(
        tempfile.mkdtemp(prefix="sql-quest-editor-")
    )
    request.session["game_workspace"] = str(workspace_path)
    request.session["game_root"] = str(workspace_path)
    clear_editor_table_rows(request)


def _editor_workspace_path(request):
    workspace_value = request.session.get("game_workspace", "")
    workspace_path = Path(workspace_value) if workspace_value else None

    if workspace_path is None or not workspace_path.is_dir():
        workspace_path = Path(
            tempfile.mkdtemp(prefix="sql-quest-editor-")
        )
        request.session["game_workspace"] = str(workspace_path)
        request.session.setdefault("game_root", str(workspace_path))
        request.session.modified = True

    return workspace_path


def _editor_table_rows_path(request):
    return _editor_workspace_path(request) / EDITOR_TABLE_ROWS_FILENAME


def clear_editor_table_rows(request):
    _save_editor_table_rows(request, {})


def get_level_database_path(request, level):
    game_root_value = request.session.get("game_root", "")
    game_root = Path(game_root_value) if game_root_value else None

    if game_root is None or not game_root.is_dir():
        return None

    level_id = sanitize_path_component(level.get("id", ""), "level")
    database_name = sanitize_path_component(
        level.get("databaseName", ""),
        f"{level_id}.db",
    )

    candidates = [
        game_root / level_id / "databases" / database_name,
        game_root / level_id / database_name,
        game_root / "databases" / database_name,
        game_root / database_name,
    ]

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    matching_databases = [
        candidate
        for candidate in game_root.rglob(database_name)
        if candidate.is_file()
    ]
    if not matching_databases:
        return None

    return min(
        matching_databases,
        key=lambda candidate: (
            level_id not in candidate.parts,
            len(candidate.parts),
        ),
    )


def _read_only_connection(database_path):
    database_uri = f"{Path(database_path).resolve().as_uri()}?mode=ro"
    return sqlite3.connect(database_uri, uri=True)


def _description_columns(description):
    if not isinstance(description, list):
        return []

    columns = []
    for entry in description:
        normalized_entry = str(entry).strip()
        if not normalized_entry:
            continue

        if "(" in normalized_entry and normalized_entry.endswith(")"):
            column_name, raw_type = normalized_entry.rsplit("(", 1)
            column_name = column_name.strip()
            column_type = raw_type[:-1].strip().lower()
        else:
            column_name = normalized_entry
            column_type = "text"

        if column_name:
            columns.append({"id": column_name, "type": column_type})

    return columns


def read_table_rows(database_path, table_item):
    table_name = table_name_for(table_item)
    if not table_name or database_path is None:
        return None

    with _read_only_connection(database_path) as connection:
        table = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table_name,),
        ).fetchone()
        if table is None:
            return None

        connection.row_factory = sqlite3.Row
        database_rows = connection.execute(
            f"SELECT * FROM {quote_identifier(table_name)}"
        ).fetchall()

    description_columns = _description_columns(
        table_item.get("description", [])
    )
    requested_columns = [column["id"] for column in description_columns]
    boolean_columns = {
        column["id"]
        for column in description_columns
        if column["type"] in {"bool", "boolean"}
    }

    rows = []
    for database_row in database_rows:
        columns = requested_columns or database_row.keys()
        row = {}

        for column_name in columns:
            if column_name not in database_row.keys():
                continue

            value = database_row[column_name]
            row[column_name] = (
                bool(value)
                if column_name in boolean_columns and value is not None
                else value
            )

        rows.append(row)

    return rows


def get_editor_level_key(request, level):
    editing_level_id = request.session.get("editing_level_id", "")
    if editing_level_id:
        return str(editing_level_id)

    if not isinstance(level, dict):
        return str(level or "")

    draft_key = str(level.get(EDITOR_LEVEL_DRAFT_KEY, "")).strip()
    if draft_key:
        return draft_key

    level_id = str(level.get("id", "")).strip()
    if level_id:
        return level_id

    draft_key = f"draft-{uuid.uuid4().hex}"
    level[EDITOR_LEVEL_DRAFT_KEY] = draft_key
    return draft_key


def _editor_table_rows(request):
    state_path = _editor_table_rows_path(request)
    if not state_path.is_file():
        return {}

    try:
        table_rows = json.loads(
            state_path.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError):
        return {}

    return table_rows if isinstance(table_rows, dict) else {}


def get_editor_table_rows(request, level, table_name):
    level_rows = _editor_table_rows(request).get(
        get_editor_level_key(request, level),
        {},
    )
    if not isinstance(level_rows, dict):
        return []

    rows = level_rows.get(str(table_name), [])
    return deepcopy(rows) if isinstance(rows, list) else []


def get_export_table_rows(request, level):
    level_key = str(level.get("id", ""))
    stored_rows = _editor_table_rows(request).get(level_key, {})
    table_rows = (
        deepcopy(stored_rows)
        if isinstance(stored_rows, dict)
        else {}
    )

    draft_level = request.session.get("new_level", {})
    if (
        not isinstance(draft_level, dict)
        or str(draft_level.get("id", "")) != level_key
    ):
        return table_rows

    draft_items = draft_level.get("items", [])
    if not isinstance(draft_items, list):
        draft_items = []

    current_item = draft_level.get("item")
    if isinstance(current_item, dict):
        draft_items = [*draft_items, current_item]

    for item in draft_items:
        if not isinstance(item, dict) or item.get("type") != "table":
            continue

        table_name = table_name_for(item)
        rows = item.get("rows")
        if table_name and table_name not in table_rows and isinstance(rows, list):
            table_rows[table_name] = deepcopy(rows)

    return table_rows


def _save_editor_table_rows(request, table_rows):
    state_path = _editor_table_rows_path(request)
    temporary_path = state_path.with_name(
        f"{state_path.name}.tmp"
    )
    temporary_path.write_text(
        json.dumps(table_rows, ensure_ascii=False),
        encoding="utf-8",
    )
    temporary_path.replace(state_path)
    request.session.modified = True


def set_editor_table_rows(
    request,
    level,
    table_name,
    rows,
    old_table_name="",
):
    level_key = get_editor_level_key(request, level)
    if not level_key or not table_name:
        return

    table_rows = deepcopy(_editor_table_rows(request))
    level_rows = table_rows.setdefault(level_key, {})
    if not isinstance(level_rows, dict):
        level_rows = {}
        table_rows[level_key] = level_rows

    if old_table_name and old_table_name != table_name:
        level_rows.pop(str(old_table_name), None)

    level_rows[str(table_name)] = deepcopy(rows if isinstance(rows, list) else [])
    _save_editor_table_rows(request, table_rows)


def remove_editor_table_rows(request, level, table_name):
    table_rows = deepcopy(_editor_table_rows(request))
    level_key = get_editor_level_key(request, level)
    level_rows = table_rows.get(level_key, {})

    if isinstance(level_rows, dict):
        level_rows.pop(str(table_name), None)
        if not level_rows:
            table_rows.pop(level_key, None)

    _save_editor_table_rows(request, table_rows)


def remove_editor_level_rows(request, level_id):
    table_rows = deepcopy(_editor_table_rows(request))
    table_rows.pop(str(level_id), None)
    _save_editor_table_rows(request, table_rows)


def move_editor_level_rows(request, old_level_id, new_level_id):
    old_level_id = str(old_level_id or "")
    new_level_id = str(new_level_id or "")
    if not old_level_id or not new_level_id or old_level_id == new_level_id:
        return

    table_rows = deepcopy(_editor_table_rows(request))
    old_level_rows = table_rows.pop(old_level_id, {})
    new_level_rows = table_rows.get(new_level_id, {})

    if isinstance(old_level_rows, dict):
        table_rows[new_level_id] = {
            **old_level_rows,
            **(new_level_rows if isinstance(new_level_rows, dict) else {}),
        }

    _save_editor_table_rows(request, table_rows)


def finalize_editor_level_rows(request, level, level_id):
    if not isinstance(level, dict):
        return

    draft_key = str(level.pop(EDITOR_LEVEL_DRAFT_KEY, "")).strip()
    if draft_key and draft_key != str(level_id):
        move_editor_level_rows(request, draft_key, level_id)


def finalize_editor_table_rows(request, level, table_item):
    """Move rows from a temporary table key to the final table name."""
    if not isinstance(table_item, dict):
        return

    table_name = table_name_for(table_item)
    draft_key = str(
        table_item.pop(EDITOR_TABLE_DRAFT_KEY, "")
    ).strip()
    if not table_name or not draft_key or table_name == draft_key:
        return

    table_rows = deepcopy(_editor_table_rows(request))
    level_key = get_editor_level_key(request, level)
    level_rows = table_rows.get(level_key, {})
    if not isinstance(level_rows, dict) or draft_key not in level_rows:
        return

    level_rows[table_name] = level_rows.pop(draft_key)
    table_rows[level_key] = level_rows
    _save_editor_table_rows(request, table_rows)


def initialize_editor_table_rows(request, game_json):
    clear_editor_table_rows(request)

    levels = game_json.get("level", [])
    if not isinstance(levels, list):
        request.session.modified = True
        return game_json

    for level in levels:
        if not isinstance(level, dict):
            continue

        database_path = get_level_database_path(request, level)
        items = level.get("items", [])
        if not isinstance(items, list):
            continue

        for item in items:
            if not isinstance(item, dict):
                continue

            embedded_rows = item.pop("data", [])
            if item.get("type") != "table":
                continue

            table_name = table_name_for(item)
            if not table_name:
                continue

            rows = read_table_rows(database_path, item)
            if rows is None:
                rows = embedded_rows if isinstance(embedded_rows, list) else []

            set_editor_table_rows(request, level, table_name, rows)

    request.session.modified = True
    return game_json


def _create_table(connection, table_item, rows):
    table_name = table_name_for(table_item)
    if not table_name:
        return

    columns = _description_columns(table_item.get("description", []))
    column_definitions = []
    has_id_column = False

    for column in columns:
        column_name = column["id"]
        if column_name.lower() == "id":
            has_id_column = True
            column_definitions.append(
                f"{quote_identifier(column_name)} INTEGER PRIMARY KEY AUTOINCREMENT"
            )
        else:
            sql_type = TYPE_MAPPING.get(column["type"], "TEXT")
            column_definitions.append(
                f"{quote_identifier(column_name)} {sql_type} NOT NULL"
            )

    if not has_id_column:
        column_definitions.insert(0, '"ID" INTEGER PRIMARY KEY AUTOINCREMENT')

    connection.execute(
        f"CREATE TABLE {quote_identifier(table_name)} "
        f"({', '.join(column_definitions)})"
    )

    data_columns = [
        column for column in columns if column["id"].lower() != "id"
    ]
    if not data_columns or not isinstance(rows, list):
        return

    column_names = [column["id"] for column in data_columns]
    quoted_columns = ", ".join(map(quote_identifier, column_names))
    placeholders = ", ".join("?" for _ in column_names)
    values = [
        tuple(row.get(column_name, "") for column_name in column_names)
        for row in rows
        if isinstance(row, dict)
    ]
    if values:
        connection.executemany(
            f"INSERT INTO {quote_identifier(table_name)} "
            f"({quoted_columns}) VALUES ({placeholders})",
            values,
        )


def create_level_database(database_path, level, table_rows):
    database_path = Path(database_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(database_path) as connection:
        items = level.get("items", [])
        for item in items if isinstance(items, list) else []:
            if not isinstance(item, dict) or item.get("type") != "table":
                continue

            rows = (
                table_rows.get(table_name_for(item), [])
                if isinstance(table_rows, dict)
                else []
            )
            _create_table(connection, item, rows)


def database_dump(database_path):
    if database_path is None or not Path(database_path).is_file():
        return ""

    with sqlite3.connect(database_path) as connection:
        return "\n".join(connection.iterdump())
