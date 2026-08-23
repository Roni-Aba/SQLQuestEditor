from __future__ import annotations

import argparse
import csv
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable, Sequence

if __package__:
    from .bootstrap_classes import is_bootstrap_class
else:
    from bootstrap_classes import is_bootstrap_class


BUR_DIRECTORY = Path(__file__).resolve().parent
PROJECT_ROOT = BUR_DIRECTORY.parents[2]
DJANGO_TEMPLATE_ROOT = PROJECT_ROOT / "backend/editor/templates"
TEMPLATE_DIRECTORY = PROJECT_ROOT / "backend/editor/templates/editor"
HTML_FILES = (
    TEMPLATE_DIRECTORY / "base.html",
    TEMPLATE_DIRECTORY / "createLevel.html",
)
ALL_TEMPLATES_CSV_FILE = BUR_DIRECTORY / "bur_all_templates.csv"
RUN_ALL_TEMPLATES = True
DJANGO_TEMPLATE_TOKEN = re.compile(r"{%.*?%}|{{.*?}}", re.DOTALL)
TEMPLATE_REFERENCE = re.compile(r'''{%\s*(?:include|extends)\s+["']([^"']+)["']''')


class ClassAttributeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.class_values: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        for name, value in attrs:
            if name.lower() == "class" and value:
                self.class_values.append(value)


def extract_css_classes(html: str) -> list[str]:
    parser = ClassAttributeParser()
    parser.feed(html)
    parser.close()

    classes: list[str] = []
    for value in parser.class_values:
        classes.extend(DJANGO_TEMPLATE_TOKEN.sub(" ", value).split())
    return classes


def calculate_bur(
    html_paths: Iterable[str | Path],
) -> tuple[float, list[str], list[str], int]:
    used_classes: list[str] = []

    for html_path in html_paths:
        path = Path(html_path)
        if not path.is_file():
            raise FileNotFoundError(f"HTML-Datei nicht gefunden: {path}")
        used_classes.extend(extract_css_classes(path.read_text(encoding="utf-8")))

    bootstrap_classes = [css_class for css_class in used_classes if is_bootstrap_class(css_class)]
    custom_classes = [css_class for css_class in used_classes if not is_bootstrap_class(css_class)]
    total = len(used_classes)
    score = round((len(bootstrap_classes) / total * 100) if total else 0, 2)
    return score, bootstrap_classes, custom_classes, total


def template_sort_key(html_file: Path) -> tuple[int, str]:
    try:
        relative_name = html_file.resolve().relative_to(TEMPLATE_DIRECTORY).as_posix()
    except ValueError:
        return 2, html_file.name
    if relative_name.startswith("components/"):
        return 0, relative_name
    if relative_name.startswith("partials/"):
        return 1, relative_name
    return 2, relative_name


def all_template_files() -> list[Path]:
    return sorted(TEMPLATE_DIRECTORY.rglob("*.html"), key=template_sort_key)


def template_dependencies(html_file: Path, seen: set[Path] | None = None) -> list[Path]:
    seen = seen or set()
    html_file = html_file.resolve()
    if html_file in seen:
        return []
    seen.add(html_file)

    dependencies = [html_file]
    for template_name in TEMPLATE_REFERENCE.findall(html_file.read_text(encoding="utf-8")):
        template_file = DJANGO_TEMPLATE_ROOT / template_name
        if not template_file.is_file():
            raise FileNotFoundError(f"Inkludiertes Template nicht gefunden: {template_name}")
        dependencies.extend(template_dependencies(template_file, seen))
    return sorted(dependencies, key=template_sort_key)


def calculate_bur_for_template(html_file: Path) -> tuple[float, list[str], list[str], int]:
    return calculate_bur(template_dependencies(html_file))


def write_csv_report(html_files: Iterable[Path], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file, delimiter=";")
        writer.writerow(["Datei", "BUR-Score (%)"])
        for html_file in html_files:
            score, _, _, _ = calculate_bur_for_template(html_file)
            try:
                file_name = html_file.resolve().relative_to(TEMPLATE_DIRECTORY).as_posix()
            except ValueError:
                file_name = html_file.name
            writer.writerow([file_name, score])
    return output_path


def print_report(
    html_files: Sequence[Path],
    score: float,
    bootstrap: Sequence[str],
    custom: Sequence[str],
    total: int,
) -> None:
    print("\n" + "=" * 60)
    print("BOOTSTRAP USAGE RATIO (BUR)")
    print("=" * 60)
    print("\nAnalysierte Template-Quellen:")
    for html_file in html_files:
        print(f"  - {html_file}")

    print(f"\nBUR: {score} %")
    print(f"Bootstrap-Klassenvorkommen: {len(bootstrap)}")
    print(f"Custom-/unbekannte Klassenvorkommen: {len(custom)}")
    print(f"Alle statischen Klassenvorkommen: {total}")

    for title, classes, symbol in (
        ("ERKANNTE BOOTSTRAP-KLASSEN", bootstrap, "✓"),
        ("CUSTOM / UNBEKANNTE KLASSEN", custom, "✗"),
        ("EINZIGARTIGE BOOTSTRAP-KLASSEN", sorted(set(bootstrap)), "✓"),
        ("EINZIGARTIGE CUSTOM-KLASSEN", sorted(set(custom)), "✗"),
    ):
        print("\n" + "-" * 60)
        print(title)
        print("-" * 60)
        for css_class in classes:
            print(f"{symbol} {css_class}")

    print(f"\nAnzahl unterschiedlicher Bootstrap-Klassen: {len(set(bootstrap))}")
    print(f"Anzahl unterschiedlicher Custom-Klassen: {len(set(custom))}")
    print("\n" + "=" * 60)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Berechnet den Bootstrap Usage Ratio für Django-Templates.",
    )
    parser.add_argument("html_files", nargs="*", type=Path, metavar="HTML_DATEI")
    parser.add_argument("--all-templates", action="store_true")
    parser.add_argument(
        "--csv-output",
        type=Path,
        default=ALL_TEMPLATES_CSV_FILE,
        metavar="DATEI.csv",
        help=f"Zielpfad für --all-templates (Standard: {ALL_TEMPLATES_CSV_FILE}).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    run_all_templates = RUN_ALL_TEMPLATES or args.all_templates
    if run_all_templates and args.html_files:
        raise SystemExit("--all-templates kann nicht mit einzelnen Dateien kombiniert werden.")

    html_files = (
        all_template_files()
        if run_all_templates
        else args.html_files or list(HTML_FILES)
    )
    score, bootstrap, custom, total = calculate_bur(html_files)
    print_report(html_files, score, bootstrap, custom, total)
    if run_all_templates:
        print(f"\nCSV-Report erstellt: {write_csv_report(html_files, args.csv_output)}")


if __name__ == "__main__":
    main()
