def update_exit_fields(item, post_data):
    item["type"] = "exit"
    item["exitSuccessMessage"] = post_data.get(
        "exit_success_message", ""
    ).strip()
    item["nextLevelId"] = post_data.get(
        "next_level_id", ""
    ).strip()