from pathlib import PurePosixPath


def select_game_json_entry(uploaded_entries):
    json_candidates = [
        (game_file, relative_name)
        for game_file, relative_name in uploaded_entries
        if PurePosixPath(
            str(relative_name).replace("\\", "/")
        ).suffix.lower() == ".json"
    ]
    preferred_json_names = {"sqlspellquest.json", "game.json"}

    return next(
        (
            (game_file, relative_name)
            for game_file, relative_name in json_candidates
            if PurePosixPath(
                str(relative_name).replace("\\", "/")
            ).name.lower() in preferred_json_names
        ),
        json_candidates[0] if len(json_candidates) == 1 else None,
    )


def copy_uploaded_files(workspace_path, uploaded_entries):
    seen_paths = set()

    for game_file, submitted_relative_name in uploaded_entries:
        relative_name = str(submitted_relative_name).replace("\\", "/")
        relative_path = PurePosixPath(relative_name)

        if (
            relative_path.is_absolute()
            or not relative_path.parts
            or ".." in relative_path.parts
        ):
            raise ValueError("Ungültiger Dateipfad im Spielordner.")

        normalized_path = str(relative_path).casefold()
        if normalized_path in seen_paths:
            raise ValueError(
                f'Der Dateipfad "{relative_name}" ist doppelt vorhanden.'
            )
        seen_paths.add(normalized_path)

        target_path = workspace_path.joinpath(*relative_path.parts)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        game_file.seek(0)
        with target_path.open("xb") as target_file:
            for chunk in game_file.chunks():
                target_file.write(chunk)
