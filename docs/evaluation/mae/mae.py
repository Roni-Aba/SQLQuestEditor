from __future__ import annotations

import argparse
from pathlib import Path

try:
    from PIL import Image
except ImportError as error:
    raise SystemExit("Pillow fehlt. Installiere es mit: python -m pip install Pillow") from error


def load_image(image_path: Path) -> Image.Image:
    with Image.open(image_path) as image:
        rgba_image = image.convert("RGBA")
    background = Image.new("RGB", rgba_image.size, "white")
    background.paste(rgba_image, mask=rgba_image.getchannel("A"))
    return background


def calculate_mae(reference: Image.Image, generated: Image.Image) -> float:
    if reference.size != generated.size:
        raise ValueError(
            f"Die Bilder müssen gleich groß sein: {reference.size} und {generated.size}."
        )
    difference = sum(
        abs(reference_value - generated_value)
        for reference_pixel, generated_pixel in zip(reference.getdata(), generated.getdata())
        for reference_value, generated_value in zip(reference_pixel, generated_pixel)
    )
    return difference / (reference.width * reference.height * 3 * 255) * 100


def main() -> None:
    parser = argparse.ArgumentParser(description="Berechnet den Mean Absolute Error zweier Screenshots.")
    parser.add_argument("figma_image", type=Path, metavar="FIGMA.png")
    parser.add_argument("page_screenshot", type=Path, metavar="SEITE.png")
    args = parser.parse_args()

    score = calculate_mae(load_image(args.figma_image), load_image(args.page_screenshot))
    print(f"MAE: {score:.4f} %")


if __name__ == "__main__":
    main()
