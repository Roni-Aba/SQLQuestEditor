import re
from pathlib import Path


EXPECTED_COMPONENTS = [
    "statusbar/statusbar.html",
    "tag/tag.html",
    "tableitem.html"
]


def calculate_crr(html_path: str):

    html = Path(html_path).read_text(
        encoding="utf-8",
        errors="ignore"
    )

    pattern = re.compile(
        r"""{%\s*include\s+["']([^"']+)["'][^%]*%}"""
    )

    includes = set(
        pattern.findall(html)
    )

    reused = 0

    for expected in EXPECTED_COMPONENTS:

        for include in includes:

            if include.endswith(expected):
                reused += 1
                break

    total = len(EXPECTED_COMPONENTS)

    if total == 0:
        score = 0
    else:
        score = (
            reused
            / total
            * 100
        )

    return (
        round(score, 2),
        reused,
        total
    )


if __name__ == "__main__":

    score, reused, expected = calculate_crr(
        "level.html"
    )

    print(f"CRR: {score} %")
    print(f"Verwendete Komponenten: {reused}")
    print(f"Erwartete Komponenten: {expected}")