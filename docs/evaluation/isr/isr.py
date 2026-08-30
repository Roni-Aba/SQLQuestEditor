from __future__ import annotations

import argparse
import csv
import re
from html.parser import HTMLParser
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DJANGO_TEMPLATE_ROOT = PROJECT_ROOT / "backend/editor/templates"
TEMPLATE_DIRECTORY = PROJECT_ROOT / "backend/editor/templates/editor"
CSV_FILE = Path(__file__).with_name("isr_all_templates.csv")
RUN_ALL_TEMPLATES = True
TEMPLATE_REFERENCE = re.compile(r'''{%\s*(?:include|extends)\s+["']([^"']+)["']''')


class InlineStyleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.elements = 0
        self.inline_styles = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.elements += 1
        self.inline_styles += any(name.lower() == "style" for name, _ in attrs)

    handle_startendtag = handle_starttag


def calculate_isr(html_files: list[Path]) -> tuple[float, int, int]:
    parser = InlineStyleParser()
    for html_file in html_files:
        parser.feed(html_file.read_text(encoding="utf-8"))
    score = round(parser.inline_styles / parser.elements * 100, 2) if parser.elements else 0
    return score, parser.inline_styles, parser.elements


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
    return dependencies


def write_csv_report(html_files: list[Path], output_path: Path) -> Path:
    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file, delimiter=";")
        writer.writerow(["Datei", "ISR-Score (%)"])
        for html_file in html_files:
            score, _, _ = calculate_isr(template_dependencies(html_file))
            writer.writerow([html_file.relative_to(TEMPLATE_DIRECTORY), score])
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Berechnet den Inline Style Ratio für Django-Templates.")
    parser.add_argument("html_files", nargs="*", type=Path, metavar="HTML_DATEI")
    parser.add_argument("--all-templates", action="store_true")
    parser.add_argument("--csv-output", type=Path, default=CSV_FILE)
    args = parser.parse_args()
    run_all_templates = RUN_ALL_TEMPLATES or args.all_templates
    if run_all_templates and args.html_files:
        raise SystemExit("--all-templates kann nicht mit einzelnen Dateien kombiniert werden.")
    html_files = sorted(TEMPLATE_DIRECTORY.rglob("*.html")) if run_all_templates else args.html_files
    if not html_files:
        raise SystemExit("Keine HTML-Dateien angegeben.")

    score, inline_styles, elements = calculate_isr(html_files)
    print("\n" + "=" * 60)
    print("INLINE STYLE RATIO (ISR)")
    print("=" * 60)
    print(f"\nISR: {score} %")
    print(f"Elemente mit Inline-Style: {inline_styles}")
    print(f"Alle HTML-Elemente: {elements}")
    if run_all_templates:
        print(f"\nCSV-Report erstellt: {write_csv_report(html_files, args.csv_output)}")


if __name__ == "__main__":
    main()
