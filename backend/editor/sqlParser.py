def map_json_type_to_sql_type(json_type):
    type_mapping = {
        "int": "INTEGER",
        "integer": "INTEGER",
        "number": "INTEGER",
        "varchar": "TEXT",
        "text": "TEXT",
        "bool": "INTEGER",
        "boolean": "INTEGER",
        "date": "TEXT",
    }
    return type_mapping.get(json_type.lower(), "TEXT")

def parse_description_column(description_entry):
    description_entry = description_entry.strip()
    if "(" not in description_entry or ")" not in description_entry:
        return {
            "name": description_entry,
            "type": "TEXT",
        }
    column_name = description_entry.split("(")[0].strip()
    column_type = description_entry.split("(")[1].replace(")", "").strip()
    return {
        "name": column_name,
        "type": map_json_type_to_sql_type(column_type),
    }

def build_create_table_sql(table_item):
    table_name = table_item.get("tableName", table_item.get("id", ""))
    description = table_item.get("description", [])
    columns = []
    has_id_column = False
    for description_entry in description:
        column = parse_description_column(description_entry)
        column_name = column["name"]
        column_type = column["type"]
        if column_name.lower() == "id":
            has_id_column = True
            columns.append("    'ID'\tINTEGER NOT NULL UNIQUE")
        else:
            columns.append(f"    '{column_name}' {column_type} NOT NULL")
    if not has_id_column:
        columns.insert(0, "    'ID'\tINTEGER NOT NULL UNIQUE")
    columns.append("    PRIMARY KEY('ID' AUTOINCREMENT)")
    columns_sql = ",\n".join(columns)
    return f"""-- DROP TABLE {table_name};
CREATE TABLE '{table_name}' (
{columns_sql}
);"""

def build_empty_insert_sql(table_item):
    table_name = table_item.get("tableName", table_item.get("id", ""))
    description = table_item.get("description", [])
    insert_columns = []
    for description_entry in description:
        column = parse_description_column(description_entry)
        column_name = column["name"]
        if column_name.lower() == "id":
            continue
        insert_columns.append(column_name)
    if not insert_columns:
        return ""
    column_sql = ", ".join([f"'{column}'" for column in insert_columns])
    empty_values_sql = ", ".join(["''" for column in insert_columns])
    return f"""INSERT INTO '{table_name}' ({column_sql}) VALUES
    ({empty_values_sql});"""

def build_level_sql(level):
    sql_blocks = []
    for item in level.get("items", []):
        if item.get("type") != "table":
            continue
        create_table_sql = build_create_table_sql(item)
        insert_sql = build_empty_insert_sql(item)
        sql_blocks.append(create_table_sql)
        if insert_sql:
            sql_blocks.append(insert_sql)
    return "\n\n".join(sql_blocks)
