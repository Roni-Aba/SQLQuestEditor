def update_password_requirement(unlock_condition, selected_item, post_data):
    requires_password = (
        post_data.get("requires_password", "false") == "true"
    )

    unlock_condition["requiredItems"] = selected_item.get(
        "unlockedItems", []
    )
    unlock_condition["requiresPassword"] = requires_password

    if not requires_password:
        unlock_condition["passwords"] = []
        unlock_condition["passwordHint"] = ""
        unlock_condition["successMessage"] = ""
        unlock_condition["showHintsOnFailure"] = False
        unlock_condition["failureHints"] = []

    return requires_password

def update_password_details(unlock_condition, post_data):
    raw_passwords = post_data.get("item_passwords", "").strip()
    passwords = [
        password.strip()
        for password in raw_passwords.replace(",", "\n").splitlines()
        if password.strip()
    ]
    show_hints = post_data.get("show_hints", "false") == "true"

    unlock_condition["passwords"] = passwords
    unlock_condition["passwordHint"] = post_data.get(
        "password_hint", ""
    ).strip()
    unlock_condition["successMessage"] = post_data.get(
        "success_message", ""
    ).strip()
    unlock_condition["showHintsOnFailure"] = show_hints

    if not show_hints:
        unlock_condition["failureHints"] = []

    return show_hints


def failure_hints_from_post(post_data):
    failure_hints = []

    for attempts, text in zip(
        post_data.getlist("hint_attempts[]"),
        post_data.getlist("hint_texts[]"),
    ):
        attempts = attempts.strip()
        text = text.strip()

        if not attempts or not text or not attempts.isdigit():
            continue

        failure_hints.append({
            "attempts": int(attempts),
            "message": text,
        })

    return failure_hints