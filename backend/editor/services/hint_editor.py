from .assets import save_uploaded_image

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
        filename, source_path = save_uploaded_image(uploaded_image, base_dir, "hints")

        item["imageLink"] = filename
        saved_level.setdefault("_new_asset_sources", {})[
            filename
        ] = source_path
    elif hint_type == "text":
        item["imageLink"] = ""
