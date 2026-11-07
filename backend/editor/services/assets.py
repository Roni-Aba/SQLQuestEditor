from pathlib import Path

from django.core.files.storage import FileSystemStorage


def save_uploaded_image(uploaded_image, base_dir, folder):
    upload_dir = Path(base_dir) / "editor" / "static" / "editor" / "img" / folder
    upload_dir.mkdir(parents=True, exist_ok=True)
    storage = FileSystemStorage(location=upload_dir)
    filename = storage.save(uploaded_image.name, uploaded_image)
    return filename, str(upload_dir / filename)
