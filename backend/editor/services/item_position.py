def _box_from_post(post_data, prefix):
    return {
        "x": int(post_data.get(f"{prefix}_x", "0")),
        "y": int(post_data.get(f"{prefix}_y", "0")),
        "width": int(post_data.get(f"{prefix}_width", "0")),
        "height": int(post_data.get(f"{prefix}_height", "0")),
    }


def position_from_post(post_data):
    return {
        "boundingBoxImage": _box_from_post(post_data, "image"),
        "boundingBoxIcon": _box_from_post(post_data, "icon"),
    }

def position_form_values(saved_level):
    position = saved_level.get("position", {})
    image = position.get("boundingBoxImage", {})
    icon = position.get("boundingBoxIcon", {})
    level_picture = saved_level.get("levelPicture", "")

    return {
        "level_picture_path": (
            f"editor/img/levels/{level_picture}"
            if level_picture else ""
        ),
        "image_x": image.get("x", ""),
        "image_y": image.get("y", ""),
        "image_width": image.get("width", ""),
        "image_height": image.get("height", ""),
        "icon_x": icon.get("x", ""),
        "icon_y": icon.get("y", ""),
        "icon_width": icon.get("width", ""),
        "icon_height": icon.get("height", ""),
    }