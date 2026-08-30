import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_ROOT = PROJECT_ROOT / "backend/editor/templates"

PAGE_PROFILES = {
    "levelgrunddaten": {
        "expected": {
            "editor/components/button/button.html",
            "editor/components/navbar/navbar.html",
            "editor/components/statusBar/statusBar.html",
            "editor/partials/levelGrunddatenForm.html",
            "editor/components/helper/helper.html",
        },
        "templates": {
            "Ansatz B": "editor/createLevel1.html",
            "Ansatz C": "editor/createLevel1agent.html",
        },
    },
    "auswahl": {
        "expected": {
            "editor/components/navbar/navbar.html",
            "editor/components/button/button.html",
            "editor/components/helper/helper.html",
        },
        "templates": {
            "Ansatz B": "editor/auswahl.html",
            "Ansatz C": "editor/auswahl3.html",
        },
    },
}

INCLUDE_PATTERN = re.compile(
    r"""{%\s*include\s+["']([^"']+)["'][^%]*%}"""
)
EXTENDS_PATTERN = re.compile(
    r"""{%\s*extends\s+["']([^"']+)["']\s*%}"""
)


def collect_templates(template: Path, visited=None):
    if visited is None:
        visited = set()

    if template in visited:
        return set()

    visited.add(template)
    html = template.read_text(encoding="utf-8", errors="ignore")
    referenced_templates = set(INCLUDE_PATTERN.findall(html))
    referenced_templates.update(EXTENDS_PATTERN.findall(html))

    for reference in referenced_templates.copy():
        referenced_template = TEMPLATE_ROOT / reference

        if referenced_template.exists():
            referenced_templates.update(collect_templates(referenced_template, visited))

    return referenced_templates


def calculate_crr(template_name: str, expected_components: set[str]):
    templates = collect_templates(TEMPLATE_ROOT / template_name)
    reused = expected_components & templates
    missing = expected_components - templates
    total = len(expected_components)
    score = len(reused) / total * 100 if total else None

    return score, reused, missing


def print_result(label: str, template_name: str, expected_components: set[str]):
    score, reused, missing = calculate_crr(template_name, expected_components)

    print(f"\n{label}: {template_name}")

    for component in sorted(reused):
        print(f"✓ {component}")

    for component in sorted(missing):
        print(f"✗ {component}")

    print(f"CRR: {score:.2f} % ({len(reused)} von {len(expected_components)})")


if __name__ == "__main__":
    for page_name, profile in PAGE_PROFILES.items():
        print(f"\n{'=' * 60}\n{page_name.upper()}\n{'=' * 60}")

        for label, template_name in profile["templates"].items():
            print_result(label, template_name, profile["expected"])
