def level1_form_values(saved_level):
    return {
        "level_name" : saved_level.get("id",""),
        "level_greeting": saved_level.get("startDialog", ""),
        "level_picture": saved_level.get("levelPicture", ""),
    }


def level2_form_values(saved_level):
    query_restriction = saved_level.get("queryRestriction", {})
    row_restriction = query_restriction.get("rowRestriction", {})
    column_restriction = query_restriction.get("columnRestriction", {})
    row_messages = row_restriction.get("violationMessages", [])
    column_messages = column_restriction.get("violationMessages", [])
    row_column_messages = query_restriction.get("colAndRowViolationMessages",[])

    return {
        "max_columns": (
            column_restriction["maxNumber"]
            if column_restriction.get("maxNumber") is not None
            else ""
        ),
        "max_rows": (
            row_restriction["maxNumber"]
            if row_restriction.get("maxNumber") is not None
            else ""
        ),
        "too_many_rows_message": row_messages[0] if row_messages else "",
        "too_many_columns_message": column_messages[0] if column_messages else "",
        "too_many_rows_columns_message": (
            row_column_messages[0] if row_column_messages else ""
        ),
    }

def query_restriction_from_post(post_data):
    max_columns = post_data.get("max_columns", "").strip()
    max_rows = post_data.get("max_rows", "").strip()
    rows_message = post_data.get("too_many_rows_message", "").strip()
    columns_message = post_data.get("too_many_columns_message", "").strip()
    both_message = post_data.get(
        "too_many_rows_columns_message", ""
    ).strip()

    return {
        "rowRestriction": {
            "maxNumber": int(max_rows) if max_rows.isdigit() else None,
            "violationMessages": [rows_message] if rows_message else [],
        },
        "columnRestriction": {
            "maxNumber": int(max_columns) if max_columns.isdigit() else None,
            "violationMessages": [columns_message] if columns_message else [],
        },
        "colAndRowViolationMessages": [both_message] if both_message else [],
    }