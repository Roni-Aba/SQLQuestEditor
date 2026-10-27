def get_item_summary(saved_level):
    item = saved_level.get("item", {})
    unlock_condition = saved_level.get(
        "unlockCondition",
        {},
    )
    position = saved_level.get(
        "position",
        {},
    )

    return {
        "item_name": item.get("id", ""),
        "required_items": unlock_condition.get(
            "requiredItems",
            item.get("unlockedItems", []),
        ),
        "passwords": unlock_condition.get(
            "passwords",
            [],
        ),
        "password_hint": unlock_condition.get(
            "passwordHint",
            "",
        ),
        "success_message": unlock_condition.get(
            "successMessage",
            "",
        ),
        "failure_hints": unlock_condition.get(
            "failureHints",
            [],
        ),
        "bounding_box_image": position.get(
            "boundingBoxImage",
            {},
        ),
        "bounding_box_icon": position.get(
            "boundingBoxIcon",
            {},
        ),
        "item_type": item.get(
            "type",
            "",
        ),
        "table_name": item.get(
            "tableName",
            "",
        ),
        "columns": item.get(
            "columns",
            [],
        ),
        "text": item.get(
            "text",
            "",
        ),
        "image_link": item.get(
            "imageLink",
            "",
        ),
        "exit_success_message": item.get(
            "exitSuccessMessage",
            "",
        ),
        "next_level_id": item.get(
            "nextLevelId",
            "",
        ),
    }
