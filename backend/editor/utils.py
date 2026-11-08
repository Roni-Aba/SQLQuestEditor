def sanitize_export_name(
    value,
    fallback="file",
):
    from pathlib import Path

    clean_name = Path(
        str(value or "")
    ).name.strip()

    if not clean_name:
        clean_name = fallback

    invalid_characters = (
        '<>:"/\\|?*'
    )

    for character in invalid_characters:
        clean_name = clean_name.replace(
            character,
            "_",
        )

    return clean_name


def database_name_for_level(level_id, fallback="level"):
    return f"{sanitize_export_name(level_id, fallback=fallback)}.db"

def find_export_asset(
    filename,
    possible_directories,
):
    from pathlib import Path
    if not filename:
        return None
    clean_filename = Path(
        str(filename)
    ).name
    for directory in possible_directories:
        candidate = (
            Path(directory)
            / clean_filename
        )
        if candidate.is_file():
            return candidate
    return None
