#!/usr/bin/env python3
"""Create traditional three-slice and nine-slice pieces from processed UI frames."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "ui" / "processed"
OUTPUT = ROOT / "assets" / "ui" / "slices"
REPORT = ROOT / "reports" / "ui" / "slice-manifest.json"

HORIZONTAL = {
    # cap width, x coordinate of an undecorated repeatable border strip
    "growth_frame": (76, 112),
    "lives_panel": (60, 45),
    "toast_panel": (65, 114),
    "tip_panel": (55, 96),
    "action_button": (60, 92),
}


def save_piece(image: Image.Image, name: str) -> dict:
    path = OUTPUT / f"{name}.png"
    image.save(path, optimize=True)
    return {"name": name, "size": list(image.size), "file": str(path.relative_to(ROOT))}


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    records = []
    for name, (cap, tile_x) in HORIZONTAL.items():
        image = Image.open(SOURCE / f"{name}.png").convert("RGBA")
        if image.width <= cap * 2:
            raise RuntimeError(f"{name}: width {image.width} is too small for {cap}px caps")
        records.extend([
            save_piece(image.crop((0, 0, cap, image.height)), f"{name}_left"),
            save_piece(image.crop((tile_x, 0, tile_x + 8, image.height)), f"{name}_mid"),
            save_piece(image.crop((image.width - cap, 0, image.width, image.height)), f"{name}_right"),
        ])

    dialog = Image.open(SOURCE / "dialog_panel.png").convert("RGBA")
    margin = 74
    xs = (0, margin, dialog.width - margin, dialog.width)
    ys = (0, margin, dialog.height - margin, dialog.height)
    labels = (("tl", "t", "tr"), ("l", "c", "r"), ("bl", "b", "br"))
    for row in range(3):
        for col in range(3):
            records.append(save_piece(
                dialog.crop((xs[col], ys[row], xs[col + 1], ys[row + 1])),
                f"dialog_panel_{labels[row][col]}",
            ))

    REPORT.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(records)} traditional UI slice pieces")


if __name__ == "__main__":
    main()
