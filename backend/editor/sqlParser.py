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
    normalized_type = str(json_type).strip().lower()
    return type_mapping.get(
        normalized_type,
        "TEXT",
    )


def quote_sql_identifier(identifier):
    normalized_identifier = str(identifier).replace('"','""')
    return f'"{normalized_identifier}"'


def parse_description_column(
    description_entry,
):
    """
    Zerlegt beispielsweise:

        name (varchar)

    in:

        {
            "name": "name",
            "type": "TEXT",
        }
    """
    description_entry = str(description_entry).strip()

    if not description_entry:
        return {
            "name": "",
            "type": "TEXT",
        }

    if ("(" not in description_entry or not description_entry.endswith(")")):
        return {
            "name": description_entry,
            "type": "TEXT",
        }

    column_name, raw_column_type = (description_entry.rsplit("(",1,))
    column_name = column_name.strip()
    raw_column_type = (raw_column_type[:-1].strip())
    return {
        "name": column_name,
        "type": map_json_type_to_sql_type(
            raw_column_type
        ),
    }


def build_create_table_sql(
    table_item,
):
    table_name = str(
        table_item.get(
            "tableName",
            "",
        )
    ).strip()
    if not table_name:
        table_name = str(
            table_item.get(
                "id",
                "",
            )
        ).strip()

    description = table_item.get(
        "description",
        [],
    )

    if not isinstance(
        description,
        list,
    ):
        description = []

    columns = []
    has_id_column = False

    for description_entry in description:
        column = parse_description_column(
            description_entry
        )

        column_name = column.get(
            "name",
            "",
        )

        column_type = column.get(
            "type",
            "TEXT",
        )

        if not column_name:
            continue

        quoted_column_name = (
            quote_sql_identifier(
                column_name
            )
        )

        if column_name.lower() == "id":
            has_id_column = True

            columns.append(
                f"    {quoted_column_name} "
                f"INTEGER PRIMARY KEY AUTOINCREMENT"
            )

        else:
            columns.append(
                f"    {quoted_column_name} "
                f"{column_type} NOT NULL"
            )

    if not has_id_column:
        columns.insert(
            0,
            (
                '    "ID" INTEGER '
                "PRIMARY KEY AUTOINCREMENT"
            ),
        )

    columns_sql = ",\n".join(
        columns
    )

    quoted_table_name = (
        quote_sql_identifier(
            table_name
        )
    )

    return (
        f"-- DROP TABLE IF EXISTS "
        f"{quoted_table_name};\n"
        f"CREATE TABLE {quoted_table_name} (\n"
        f"{columns_sql}\n"
        f");"
    )


def build_level_sql(
    level,
):


    sql_blocks = []

    items = level.get(
        "items",
        [],
    )

    if not isinstance(
        items,
        list,
    ):
        items = []

    for item in items:
        if not isinstance(
            item,
            dict,
        ):
            continue

        if item.get(
            "type"
        ) != "table":
            continue

        create_table_sql = (
            build_create_table_sql(
                item
            )
        )

        sql_blocks.append(
            create_table_sql
        )

    return "\n\n".join(
        sql_blocks
    )
