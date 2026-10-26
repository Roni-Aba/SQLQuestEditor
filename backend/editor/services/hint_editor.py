from pathlib import Path
from django.core.files.storage import FileSystemStorage

def update_hint_field(item, post_data):
    hint_type = post_data.get("hint_type","").strip()
    hint_text = post_data.get("hint_text","").strip()

    if hint_type not in {"text", "image", "text_image"}:
        hint_type = "text"

    item["type"] = "hint"
    item["hintType"] = hint_type
    item["text"] = (
        hint_text if hint_type in {"text", "text_image"} else ""
    )
    return hint_type

def update_hint_image(item, saved_level, uploaded_image, hint_type, base_dir):
    if uploaded_image:
        upload_dir = (
            Path(base_dir) / "editor" / "static" / "editor" / "img" / "hints"
        )
        upload_dir.mkdir(parents=True, exist_ok=True)

        storage = FileSystemStorage(location=upload_dir)
        filename = storage.save(uploaded_image.name, uploaded_image)

        item["imageLink"] = filename
        saved_level.setdefault("_new_asset_sources", {})[
            filename
        ] = str(upload_dir / filename)
    elif hint_type == "text":
        item["imageLink"] = ""