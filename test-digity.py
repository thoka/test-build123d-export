"""

Wir testen die Exportmöglichkeiten von build123d über das Testscript digits.py 

Es erzeugt folgende Dateien im Ordner out/:
- digits.step
- digits.stl
- digits.3mf
- digits.bin
- digits.brep
- digits.gltf

Wir wollen folgende Features testen:
- Namen auf unterschiedlichen Ebenen: dIgItS -> dIgIt_{digit} -> tExT_{digit} und bOx_{digit}
- Farben auf unterschiedlichen Ebenen: Weiß für bOx_{digit} und Schwarz für tExT_{digit}.
  Um die Farben zu testen, nutzen wir statt Weiß und Schwarz besser identifizierbare Farben, 
  bei denen die Komponenten auch im Export gut zu erkennen sind: 
  0.010101,0.010102,0.010103 und 0.990901,0.990902,0.990903 statt Weiß und Schwarz.

Dieses Programm erzeugt eine Feature-Matrix, welche Formate welche Informationen enthalten.
Dazu werden in den unterschiedlichen Exportformaten die Namen und Farben über einfache Textsuche gesucht.

Für .3mf müssen wir die Datei vorher entpacken.

"""

from __future__ import annotations

import os
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Iterable


# Pfade und Konstanten
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
BASE_NAME = "digits"
EXPECTED = {
  "step": OUT / f"{BASE_NAME}.step",
  "stl": OUT / f"{BASE_NAME}.stl",
  "3mf": OUT / f"{BASE_NAME}.3mf",
  "bin": OUT / f"{BASE_NAME}.bin",
  "brep": OUT / f"{BASE_NAME}.brep",
  "gltf": OUT / f"{BASE_NAME}.gltf",
}

NAMES = ["dIgItS", "dIgIt_", "tExT_", "bOx_"]
COLORS = [
  "0.010101",
  "0.010102",
  "0.010103",
  "0.990901",
  "0.990902",
  "0.990903",
]


def run_digits() -> None:
  """Führt digits.py aus, um die Exportdateien zu erzeugen."""

  env = os.environ.copy()
  # Verhindert ein Aufpoppen des Viewers, falls ocp_vscode installiert ist.
  env.setdefault("OCP_RENDER", "0")

  print("Starte digits.py, um fehlende Dateien zu erzeugen...")
  subprocess.run([sys.executable, "digits.py"], cwd=ROOT, env=env, check=True)


def ensure_exports() -> None:
  """Sorgt dafür, dass alle erwarteten Exportdateien vorliegen."""

  OUT.mkdir(exist_ok=True)
  missing = [p for p in EXPECTED.values() if not p.exists()]
  if not missing:
    return

  run_digits()

  still_missing = [p for p in EXPECTED.values() if not p.exists()]
  if still_missing:
    missing_list = ", ".join(str(p) for p in still_missing)
    raise FileNotFoundError(f"Nach digits.py fehlen weiterhin: {missing_list}")


def _read_text(path: Path) -> str:
  """Liest den Dateiinhalt als Text (best effort)."""

  data = path.read_bytes()
  try:
    return data.decode("utf-8")
  except UnicodeDecodeError:
    return data.decode("latin-1", errors="ignore")


def _search_strings(haystack: str, needles: Iterable[str]) -> list[str]:
  """Findet alle Vorkommen der gesuchten Teilstrings."""

  return [needle for needle in needles if needle in haystack]


def analyze_plain_file(path: Path) -> tuple[list[str], list[str]]:
  """Sucht Namen und Farben in einer normalen Text- oder Binärdatei."""

  content = _read_text(path)
  found_names = _search_strings(content, NAMES)
  found_colors = _search_strings(content, COLORS)
  return found_names, found_colors


def analyze_3mf(path: Path) -> tuple[list[str], list[str]]:
  """Entpackt die .3mf und durchsucht alle enthaltenen XML-Dateien."""

  found_names: list[str] = []
  found_colors: list[str] = []

  with zipfile.ZipFile(path) as zf:
    for name in zf.namelist():
      if not name.lower().endswith((".model", ".xml", ".rels")):
        continue
      text = zf.read(name).decode("utf-8", errors="ignore")
      found_names.extend(_search_strings(text, NAMES))
      found_colors.extend(_search_strings(text, COLORS))

  # Doppelte Einträge vermeiden
  return sorted(set(found_names)), sorted(set(found_colors))


def build_matrix() -> dict[str, dict[str, list[str] | bool]]:
  """Erzeugt die Feature-Matrix für alle Formate."""

  matrix: dict[str, dict[str, list[str] | bool]] = {}

  for fmt, path in EXPECTED.items():
    if not path.exists():
      matrix[fmt] = {"present": False, "names": [], "colors": []}
      continue

    if fmt == "3mf":
      names, colors = analyze_3mf(path)
    else:
      names, colors = analyze_plain_file(path)

    matrix[fmt] = {
      "present": True,
      "names": sorted(set(names)),
      "colors": sorted(set(colors)),
    }

  return matrix


def print_matrix(matrix: dict[str, dict[str, list[str] | bool]]) -> None:
  """Gibt die Matrix als kleine Tabelle aus."""

  header = f"{'Format':<6} | {'Datei':<7} | Namen | Farben"
  print(header)
  print("-" * len(header))
  for fmt, info in matrix.items():
    present = "ok" if info["present"] else "fehlt"
    names = ",".join(info["names"]) if info["names"] else "-"
    colors = ",".join(info["colors"]) if info["colors"] else "-"
    print(f"{fmt:<6} | {present:<7} | {names} | {colors}")


def main() -> None:
  ensure_exports()
  matrix = build_matrix()
  print_matrix(matrix)


if __name__ == "__main__":
  main()

