def level_name_is_taken(game_json, level_name, editing_level_id=None):
    levels = game_json.get("level", []) if isinstance(game_json, dict) else []
    if not isinstance(levels, list):
        return False
    return any(
        isinstance(level, dict)
        and level.get("id") == level_name
        and level.get("id") != editing_level_id
        for level in levels
    )


def save_new_level_session(request, saved_level):
    request.session["new_level"] = saved_level
    request.session.modified = True


def get_steps(active_step):
    steps = []
    for number in range(0, 9):
        steps.append({"number": number, "active": number <= active_step})
    return steps