import json
from .. import utils, database

def parse_table_columns(column_ids, column_types):
    columns = []
    error_message = ""

    for column_id, column_type in zip(column_ids, column_types):
        column_id = column_id.strip()
        column_type = column_type.strip()

        if not column_id and not column_type:
            continue

        if not column_id:
            error_message = "Jede Spalte benötigt einen Namen."
            break

        if column_type not in {"text", "number", "date", "boolean"}:
            error_message = (
                f"Der Datentyp der Spalte „{column_id}“ ist ungültig."
            )
            break

        if any(
            existing_column["id"].lower() == column_id.lower()
            for existing_column in columns
        ):
            error_message = (
                f"Der Spaltenname „{column_id}“ wurde mehrfach verwendet."
            )
            break

        columns.append({"id": column_id, "type": column_type})

    return columns, error_message

def parse_table_rows(raw_rows_json, columns):
    try:
        submitted_rows = json.loads(raw_rows_json)
    except json.JSONDecodeError:
        return [], "Die Tabellendaten konnten nicht verarbeitet werden."

    if not isinstance(submitted_rows, list):
        submitted_rows = []

    rows = []

    for submitted_row in submitted_rows:
        if not isinstance(submitted_row, dict):
            continue

        cleaned_row = {}
        row_has_value = False

        for column in columns:
            column_id = column["id"]
            column_type = column["type"]
            raw_value = submitted_row.get(column_id, "")
            cleaned_value = utils.convert_table_cell_value(
                raw_value,
                column_type,
            )

            if cleaned_value not in ("", None):
                row_has_value = True

            cleaned_row[column_id] = cleaned_value

        if row_has_value:
            rows.append(cleaned_row)

    return rows, ""

def persist_draft_table_rows(request, saved_level, item, rows):
    table_storage_key = database.get_editor_table_key(item)

    saved_level["databaseName"] = utils.database_name_for_level(
        saved_level.get("id", "")
    )

    old_table_name = ""
    editing_item_id = request.session.get("editing_item_id", "")

    for existing_item in saved_level.get("items", []):
        if (
            isinstance(existing_item, dict)
            and existing_item.get("id") == editing_item_id
            and existing_item.get("type") == "table"
        ):
            old_table_name = str(
                existing_item.get(
                    "tableName",
                    existing_item.get("id", ""),
                )
            ).strip()
            break

    database.set_editor_table_rows(
        request,
        saved_level,
        table_storage_key,
        rows,
        old_table_name=old_table_name,
    )