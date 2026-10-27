from copy import deepcopy
DEFAULT_MESSAGES = {
    "wrong_password": (
        "Das Passwort ist nicht korrekt. "
        "Versuche es bitte erneut."
    ),
    "wrong_password_new_hint": (
        "Das Passwort ist nicht korrekt. "
        "Ein neuer Hinweis wurde freigeschaltet."
    ),
    "not_a_table": (
        "Auf %s kann keine SQL-Abfrage ausgeführt werden, "
        "da es sich nicht um eine Tabelle handelt."
    ),
    "unknown_table": (
        "Die Tabelle ist nicht bekannt. "
        "Checke bitte den Tabellennamen."
    ),
    "locked_table": (
        "Die Tabelle ist noch nicht freigeschaltet."
    ),
    "sql_error": (
        "Die SQL-Abfrage konnte nicht gecallt werden. "
        "Check bitte die Syntax und versuche es erneut."
    ),
    "no_result": (
        "Die SQL-Abfrage hat kein Ergebnis geliefert."
    ),
    "row_restriction": (
        "Die Abfrage liefert zu viele Zeilen. "
        "Limitiere das Ergebnis bitte auf die notwendigen Zeilen ein."
    ),
    "col_restriction": (
        "Die Abfrage liefert zu viele Spalten. "
        "Choose bitte nur die benötigten Spalten aus."
    ),
    "row_and_col_restriction": (
        "Die Abfrage liefert zu viele Zeilen und Spalten. "
        "Limitiere das Ergebnis bitte auf die benötigten Zeilen "
        "und Spalten ein."
    ),
}

def normalize_game_messages(game_json):
    if not isinstance(game_json, dict):
        return {}

    levels = game_json.get("level", [])
    root_messages = game_json.get("messages")

    if not isinstance(root_messages, dict):
        root_messages = None
        if isinstance(levels, list):
            for level in levels:
                if not isinstance(level, dict):
                    continue
                level_messages = level.get("messages")
                if isinstance(level_messages, dict):
                    root_messages = deepcopy(level_messages)
                    break

        if root_messages is not None:
            game_json["messages"] = root_messages
        elif "messages" in game_json:
            game_json["messages"] = {}

    if isinstance(levels, list):
        for level in levels:
            if isinstance(level, dict):
                level.pop("messages", None)

    return game_json
def messages_form_values(saved_messages):
    return {
        key: saved_messages.get(key, default_value)
        for key, default_value in DEFAULT_MESSAGES.items()
    }


def messages_from_post(post_data):
    messages = {}
    for key, default_value in DEFAULT_MESSAGES.items():
        value = post_data.get(key, "").strip()
        messages[key] = value if value else default_value
    return messages