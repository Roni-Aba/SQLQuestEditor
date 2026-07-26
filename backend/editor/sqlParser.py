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
    table_name = table_item.get(
        "tableName",
        table_item.get(
            "id",
            "",
        ),
    )

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


def format_sql_value(
    value,
    sql_type,
):
    normalized_sql_type = str(
        sql_type
    ).strip().upper()

    if value is None:
        return "NULL"

    if normalized_sql_type == "INTEGER":
        if isinstance(
            value,
            bool,
        ):
            return "1" if value else "0"

        normalized_value = str(
            value
        ).strip()

        if normalized_value == "":
            return "NULL"

        normalized_boolean = (
            normalized_value.lower()
        )

        if normalized_boolean in {
            "true",
            "yes",
            "on",
            "ja",
        }:
            return "1"

        if normalized_boolean in {
            "false",
            "no",
            "off",
            "nein",
        }:
            return "0"

        try:
            integer_value = int(
                normalized_value
            )

            return str(
                integer_value
            )

        except (
            TypeError,
            ValueError,
        ):
            try:
                float_value = float(
                    normalized_value
                )

                return str(
                    float_value
                )

            except (
                TypeError,
                ValueError,
            ):
                escaped_value = (
                    normalized_value.replace(
                        "'",
                        "''",
                    )
                )

                return f"'{escaped_value}'"

    normalized_value = str(
        value
    )

    escaped_value = (
        normalized_value.replace(
            "'",
            "''",
        )
    )

    return f"'{escaped_value}'"


def build_insert_sql(
    table_item,
):
    table_name = table_item.get(
        "tableName",
        table_item.get(
            "id",
            "",
        ),
    )

    description = table_item.get(
        "description",
        [],
    )

    table_data = table_item.get(
        "data",
        [],
    )

    if not isinstance(
        description,
        list,
    ):
        description = []

    if not isinstance(
        table_data,
        list,
    ):
        table_data = []

    if not table_data:
        return ""

    columns = []

    for description_entry in description:
        column = parse_description_column(
            description_entry
        )

        column_name = column.get(
            "name",
            "",
        )

        if not column_name:
            continue

        if column_name.lower() == "id":
            continue

        columns.append(
            column
        )

    if not columns:
        return ""

    quoted_table_name = (
        quote_sql_identifier(
            table_name
        )
    )

    insert_columns_sql = ", ".join(
        quote_sql_identifier(
            column["name"]
        )
        for column in columns
    )

    sql_rows = []

    for row in table_data:
        if not isinstance(
            row,
            dict,
        ):
            continue

        values = []

        for column in columns:
            column_name = column[
                "name"
            ]

            column_type = column[
                "type"
            ]

            value = row.get(
                column_name,
                None,
            )

            values.append(
                format_sql_value(
                    value,
                    column_type,
                )
            )

        sql_rows.append(
            f"    ({', '.join(values)})"
        )

    if not sql_rows:
        return ""

    values_sql = ",\n".join(
        sql_rows
    )

    return (
        f"INSERT INTO {quoted_table_name} "
        f"({insert_columns_sql}) VALUES\n"
        f"{values_sql};"
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

        insert_sql = (
            build_insert_sql(
                item
            )
        )

        sql_blocks.append(
            create_table_sql
        )

        if insert_sql:
            sql_blocks.append(
                insert_sql
            )

    return "\n\n".join(
        sql_blocks
    )