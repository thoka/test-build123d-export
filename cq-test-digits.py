"""

Test the export capabilities of CadQuery using the helper script cq-digits.py.

It produces the following files in the out/ folder:
- cq-digits.step
- cq-digits.stl
- cq-digits.3mf
- cq-digits.brep

We validate these features:
- Names across hierarchy levels: dIgItS -> dIgIt_{digit} -> tExT_{digit} and bOx_{digit}
- Colors on different levels: distinctive RGB triples instead of plain black/white so they
  stay visible in exports: 0.010101,0.010102,0.010103 and 0.990901,0.990902,0.990903

This script builds a feature matrix showing which formats contain which pieces of
information. It searches exported files for names and colors via simple substring search.

For .3mf we first unzip the archive and scan the contained XML.

"""

from __future__ import annotations

from datetime import datetime
import os
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Iterable


# Paths and constants
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
README = ROOT / "readme.md"
SECTION_TITLE = "### CadQuery export feature matrix (latest run)"
BASE_NAME = "cq-digits"
EXPECTED = {
    "step": OUT / f"{BASE_NAME}.step",
    "stl": OUT / f"{BASE_NAME}.stl",
}

NAME_GROUPS = {
    "root": ["dIgItS"],
    "child": ["dIgIt_"],
    "text": ["tExT_"],
    "box": ["bOx_"],
}
ALL_NAMES = tuple(name for names in NAME_GROUPS.values() for name in names)

COLORS = [
    "0.010101",
    "0.010102",
    "0.010103",
    "0.990901",
    "0.990902",
    "0.990903",
]


def run_digits() -> None:
    """Run cq-digits.py to generate export files."""

    env = os.environ.copy()
    env.setdefault("OCP_RENDER", "0")

    print("Running cq-digits.py to generate missing files...")
    subprocess.run([sys.executable, "cq-digits.py"], cwd=ROOT, env=env, check=True)


def ensure_exports() -> None:
    """Ensure all expected export files exist."""

    OUT.mkdir(exist_ok=True)
    missing = [p for p in EXPECTED.values() if not p.exists()]
    if not missing:
        return

    run_digits()

    still_missing = [p for p in EXPECTED.values() if not p.exists()]
    if still_missing:
        missing_list = ", ".join(str(p) for p in still_missing)
        raise FileNotFoundError(f"After cq-digits.py these files are still missing: {missing_list}")


def _read_text(path: Path) -> str:
    """Read file content as text (best effort)."""

    data = path.read_bytes()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1", errors="ignore")


def _search_strings(haystack: str, needles: Iterable[str]) -> list[str]:
    """Return all needle substrings found in haystack."""

    return [needle for needle in needles if needle in haystack]


def analyze_plain_file(path: Path) -> tuple[list[str], list[str]]:
    """Search names and colors in a plain text or binary file."""

    content = _read_text(path)
    found_names = _search_strings(content, ALL_NAMES)
    found_colors = _search_strings(content, COLORS)
    return found_names, found_colors


def analyze_3mf(path: Path) -> tuple[list[str], list[str]]:
    """Unzip the .3mf and scan contained XML files."""

    found_names: list[str] = []
    found_colors: list[str] = []

    with zipfile.ZipFile(path) as zf:
        for name in zf.namelist():
            if not name.lower().endswith((".model", ".xml", ".rels")):
                continue
            text = zf.read(name).decode("utf-8", errors="ignore")
            found_names.extend(_search_strings(text, ALL_NAMES))
            found_colors.extend(_search_strings(text, COLORS))

    # Drop duplicates
    return sorted(set(found_names)), sorted(set(found_colors))


def categorize_names(names: Iterable[str]) -> dict[str, bool]:
    """Flag hierarchy levels based on detected names."""

    detected = set(names)
    return {
        key: any(name in detected for name in needles)
        for key, needles in NAME_GROUPS.items()
    }


def build_matrix() -> dict[str, dict[str, list[str] | bool]]:
    """Build the feature matrix for all formats."""

    matrix: dict[str, dict[str, list[str] | bool]] = {}

    for fmt, path in EXPECTED.items():
        if not path.exists():
            matrix[fmt] = {
                "present": False,
                "names": [],
                "colors": [],
                "root": False,
                "child": False,
                "text": False,
                "box": False,
            }
            continue

        if fmt == "3mf":
            names, colors = analyze_3mf(path)
        else:
            names, colors = analyze_plain_file(path)

        flags = categorize_names(names)
        matrix[fmt] = {
            "present": True,
            "names": sorted(set(names)),
            "colors": sorted(set(colors)),
            **flags,
        }

    return matrix


def print_matrix(matrix: dict[str, dict[str, list[str] | bool]]) -> None:
    """Print the matrix as a compact table."""

    print(format_matrix(matrix))


def format_matrix(matrix: dict[str, dict[str, list[str] | bool]]) -> str:
    """Return the matrix as a formatted string table."""

    header = (
        f"| {'Format':<7} | {'File':<7} | {'root':<5} | {'child':<7} | "
        f"{'text':<5} | {'box':<4} | colors |"
    )
    align = "|:-------|:-------|:-----|:--------|:-----|:----|:-------|"
    lines = [header, align]
    for fmt, info in matrix.items():
        present = "ok" if info["present"] else "missing"
        root = "yes" if info["root"] else "-"
        child = "yes" if info["child"] else "-"
        text = "yes" if info["text"] else "-"
        box = "yes" if info["box"] else "-"
        colors = "yes" if info["colors"] else "-"
        lines.append(
            f"| {fmt:<7} | {present:<7} | {root:<5} | {child:<7} | "
            f"{text:<5} | {box:<4} | {colors} |"
        )
    return "\n".join(lines)


def render_readme_section(matrix: dict[str, dict[str, list[str] | bool]], timestamp: str, run_cmd: str) -> str:
    """Render the README section for the latest matrix."""

    parts = [
        SECTION_TITLE,
        "",
        f"Run: {run_cmd}  ",
        f"Date: {timestamp}",
        "",
        "Generated the digits exports and inspected them for hierarchy names and colors.",
        "",
        format_matrix(matrix),
        "",
    ]
    return "\n".join(parts)


def update_readme(matrix: dict[str, dict[str, list[str] | bool]], timestamp: str, run_cmd: str) -> None:
    """Update README with the latest matrix section if changed."""

    if not README.exists():
        return

    text = README.read_text()
    section = render_readme_section(matrix, timestamp, run_cmd)

    if SECTION_TITLE in text:
        before, _, rest = text.partition(SECTION_TITLE)

        next_idx = len(rest)
        for marker in ("\n## ", "\n### "):
            idx = rest.find(marker)
            if idx != -1 and idx < next_idx:
                next_idx = idx
        rest_tail = rest[next_idx:] if next_idx < len(rest) else ""
        new_text = before + section + rest_tail
    else:
        if not text.endswith("\n\n"):
            text = text.rstrip() + "\n\n"
        new_text = text + section

    if new_text != text:
        README.write_text(new_text)


def main() -> None:
    ensure_exports()
    matrix = build_matrix()
    print_matrix(matrix)
    timestamp = datetime.now().isoformat(timespec="seconds")
    run_cmd = f"{sys.executable} {Path(__file__).name}"
    update_readme(matrix, timestamp, run_cmd)


if __name__ == "__main__":
    main()
