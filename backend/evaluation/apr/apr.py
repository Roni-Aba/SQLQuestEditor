from __future__ import annotations

import argparse
import csv
import re
from html.parser import HTMLParser
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DJANGO_TEMPLATE_ROOT = PROJECT_ROOT / "backend/editor/templates"
TEMPLATE_DIRECTORY = PROJECT_ROOT / "backend/editor/templates/editor"
CSS_DIRECTORY = PROJECT_ROOT / "backend/editor/static/editor"
CSV_FILE = Path(__file__).with_name("apr_all_templatesOld.csv")
RUN_ALL_TEMPLATES = True
POSITION = re.compile(r"\bposition\s*:\s*(absolute|fixed|relative|sticky)\b", re.IGNORECASE)
CSS_RULE = re.compile(r"([^{}]+)\{([^{}]*)\}", re.DOTALL)
CLASS_NAME = re.compile(r"\.([\w-]+)")
ID_NAME = re.compile(r"#([\w-]+)")
TEMPLATE_REFERENCE = re.compile(r'''{%\s*(?:include|extends)\s+["']([^"']+)["']''')
CSS_REFERENCE = re.compile(r'''{%\s*static\s+["']([^"']+\.css)["']''')


class TemplateParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.elements: list[tuple[str, set[str], str | None, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        self.elements.append((tag, set((attributes.get("class") or "").split()), attributes.get("id"), attributes.get("style") or ""))

    handle_startendtag = handle_starttag


def matches_selector(element: tuple[str, set[str], str | None, str], selector: str) -> bool:
    if "::" in selector:
        return False
    selector = re.split(r"\s+|[>+~]", selector.strip())[-1].split(":")[0]
    tag, classes, element_id, _ = element
    selector_tag = re.match(r"^[\w-]+", selector)
    return (
        (not selector_tag or selector_tag.group() == tag)
        and set(CLASS_NAME.findall(selector)).issubset(classes)
        and (not ID_NAME.findall(selector) or element_id in ID_NAME.findall(selector))
    )


def calculate_apr(html_files: list[Path], css_files: list[Path]) -> tuple[float, int, int]:
    parser = TemplateParser()
    for html_file in html_files:
        parser.feed(html_file.read_text(encoding="utf-8"))

    positions: dict[int, str] = {}
    for css_file in css_files:
        for selectors, declarations in CSS_RULE.findall(css_file.read_text(encoding="utf-8")):
            position = POSITION.search(declarations)
            if not position:
                continue
            for selector in selectors.split(","):
                for index, element in enumerate(parser.elements):
                    if matches_selector(element, selector):
                        positions[index] = position.group(1).lower()

    for index, element in enumerate(parser.elements):
        position = POSITION.search(element[3])
        if position:
            positions[index] = position.group(1).lower()

    positioned = len(positions)
    absolute = sum(position in {"absolute", "fixed"} for position in positions.values())
    score = round(absolute / positioned * 100, 2) if positioned else 0
    return score, absolute, positioned


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


def css_dependencies(html_files: list[Path]) -> list[Path]:
    css_files: set[Path] = set()
    for html_file in html_files:
        for css_name in CSS_REFERENCE.findall(html_file.read_text(encoding="utf-8")):
            css_file = CSS_DIRECTORY.parent / css_name
            if css_file.is_file():
                css_files.add(css_file)
        relative_name = html_file.relative_to(TEMPLATE_DIRECTORY)
        if relative_name.parts[0] == "components":
            css_file = CSS_DIRECTORY / relative_name.with_suffix(".css")
            if css_file.is_file():
                css_files.add(css_file)
    return sorted(css_files)


def write_csv_report(html_files: list[Path], output_path: Path) -> Path:
    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file, delimiter=";")
        writer.writerow(["Datei", "APR-Score (%)"])
        for html_file in html_files:
            dependencies = template_dependencies(html_file)
            score, _, _ = calculate_apr(dependencies, css_dependencies(dependencies))
            writer.writerow([html_file.relative_to(TEMPLATE_DIRECTORY), score])
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Berechnet den Absolute Positioning Ratio für Django-Templates.")
    parser.add_argument("--all-templates", action="store_true")
    parser.add_argument("--csv-output", type=Path, default=CSV_FILE)
    args = parser.parse_args()

    html_files = sorted(TEMPLATE_DIRECTORY.rglob("*.html"))
    score, absolute, positioned = calculate_apr(html_files, sorted(CSS_DIRECTORY.rglob("*.css")))
    print("\n" + "=" * 60)
    print("ABSOLUTE POSITIONING RATIO (APR)")
    print("=" * 60)
    print(f"\nAPR: {score} %")
    print(f"Absolut/fest positionierte Elemente: {absolute}")
    print(f"Alle explizit positionierten Elemente: {positioned}")
    if RUN_ALL_TEMPLATES or args.all_templates:
        print(f"\nCSV-Report erstellt: {write_csv_report(html_files, args.csv_output)}")


if __name__ == "__main__":
    main()
