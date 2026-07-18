#!/usr/bin/env python3
"""Turn generated 3x2 chroma sheets into registered 6-frame transparent spritesheets."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "animation" / "source"
FRAMES = ROOT / "assets" / "animation" / "frames"
SHEETS = ROOT / "assets" / "animation" / "sheets"
REPORTS = ROOT / "reports" / "animation"
HELPER = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "skills" / ".system" / "imagegen" / "scripts" / "remove_chroma_key.py"

FRAME_SIZE = 256
SPECS = {
    "momo_swim": "momo-swim-source.png",
    "lanternfish_swim": "lanternfish-swim-source.png",
    "butterflyfish_swim": "butterflyfish-swim-source.png",
    "sardine_swim": "sardine-swim-source.png",
    "shrimp_swim": "shrimp-swim-source.png",
    "puffer_pulse": "puffer-pulse-source.png",
    "jellyfish_pulse": "jellyfish-pulse-source.png",
    "shark_boss": "shark-boss-source.png",
}

HEAD_ANCHORED_SHEETS = {
    "momo_swim", "lanternfish_swim", "butterflyfish_swim",
    "sardine_swim", "shrimp_swim", "shark_boss",
}


def key_image(source: Path, output: Path) -> None:
    subprocess.run(
        [
            "python3", str(HELPER), "--input", str(source), "--out", str(output),
            "--auto-key", "border", "--tolerance", "62", "--despill", "--force",
        ],
        check=True,
    )


def validate_frame(name: str, index: int, frame: Image.Image) -> dict:
    alpha = frame.getchannel("A")
    bbox = alpha.point(lambda value: 255 if value > 8 else 0).getbbox()
    pixels = list(frame.getdata())
    visible = [(r, g, b, a) for r, g, b, a in pixels if a > 8]
    magenta = sum(1 for r, g, b, _ in visible if r > 190 and b > 190 and g < 70)
    corners = [alpha.getpixel((0, 0)), alpha.getpixel((255, 0)), alpha.getpixel((0, 255)), alpha.getpixel((255, 255))]
    edge = []
    for p in range(FRAME_SIZE):
        edge += [alpha.getpixel((p, 0)), alpha.getpixel((p, 255)), alpha.getpixel((0, p)), alpha.getpixel((255, p))]
    issues = []
    if bbox is None:
        issues.append("empty-frame")
        coverage = 0
    else:
        coverage = ((bbox[2] - bbox[0]) * (bbox[3] - bbox[1])) / (FRAME_SIZE * FRAME_SIZE)
        if coverage < .12:
            issues.append("subject-too-small")
        if coverage > .82:
            issues.append("subject-too-large")
    if any(c != 0 for c in corners):
        issues.append("corner-not-transparent")
    if max(edge, default=0) > 8:
        issues.append("frame-edge-clipped")
    if magenta / max(len(visible), 1) > .002:
        issues.append("magenta-residue")
    return {
        "sheet": name,
        "frame": index,
        "bbox": bbox,
        "coverage": round(coverage, 4),
        "magenta_pixels": magenta,
        "issues": issues,
    }


def remove_alpha_specks(frame: Image.Image, min_pixels: int = 14) -> Image.Image:
    """Remove tiny detached keying artifacts without touching connected appendages."""
    alpha = frame.getchannel("A")
    visible = alpha.point(lambda value: 255 if value > 8 else 0)
    seen: set[tuple[int, int]] = set()
    remove: list[tuple[int, int]] = []
    for y in range(frame.height):
        for x in range(frame.width):
            if (x, y) in seen or visible.getpixel((x, y)) == 0:
                continue
            stack = [(x, y)]
            seen.add((x, y))
            component = []
            while stack:
                px, py = stack.pop()
                component.append((px, py))
                for nx, ny in ((px - 1, py), (px + 1, py), (px, py - 1), (px, py + 1)):
                    if 0 <= nx < frame.width and 0 <= ny < frame.height and (nx, ny) not in seen and visible.getpixel((nx, ny)):
                        seen.add((nx, ny))
                        stack.append((nx, ny))
            if len(component) < min_pixels:
                remove.extend(component)
    if not remove:
        return frame
    cleaned = frame.copy()
    pixels = cleaned.load()
    for x, y in remove:
        pixels[x, y] = (0, 0, 0, 0)
    return cleaned


def bell_anchor(frame: Image.Image) -> tuple[float, int]:
    """Return the jelly bell's horizontal centroid and top edge."""
    alpha = frame.getchannel("A")
    bbox = alpha.getbbox()
    if not bbox:
        return FRAME_SIZE / 2, 0
    cutoff = min(FRAME_SIZE, bbox[1] + 78)
    total = 0
    weighted_x = 0
    pixels = alpha.load()
    for y in range(bbox[1], cutoff):
        for x in range(FRAME_SIZE):
            value = pixels[x, y]
            total += value
            weighted_x += x * value
    return (weighted_x / total if total else (bbox[0] + bbox[2]) / 2), bbox[1]


def align_frame(name: str, frame: Image.Image) -> Image.Image:
    """Register body anchors so animation affects appendages, not world position."""
    bbox = frame.getchannel("A").getbbox()
    if not bbox:
        return frame
    if name in HEAD_ANCHORED_SHEETS:
        # These creatures face right. Lock the head/antenna side while the tail changes.
        dx = round(240 - bbox[2])
        dy = round(128 - (bbox[1] + bbox[3]) / 2)
    elif name == "puffer_pulse":
        # Inflation must expand around one fixed body center.
        dx = round(128 - (bbox[0] + bbox[2]) / 2)
        dy = round(128 - (bbox[1] + bbox[3]) / 2)
    elif name == "jellyfish_pulse":
        # Tentacle bounds are volatile, so anchor the bell instead.
        bell_x, bell_top = bell_anchor(frame)
        dx = round(128 - bell_x)
        dy = round(24 - bell_top)
    else:
        dx = dy = 0
    aligned = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    aligned.alpha_composite(frame, (dx, dy))
    return aligned


def anchor_error(name: str, frame: Image.Image) -> dict:
    bbox = frame.getchannel("A").getbbox()
    if not bbox:
        return {"x": 999, "y": 999}
    if name in HEAD_ANCHORED_SHEETS:
        return {"x": abs(bbox[2] - 240), "y": abs((bbox[1] + bbox[3]) / 2 - 128)}
    if name == "puffer_pulse":
        return {"x": abs((bbox[0] + bbox[2]) / 2 - 128), "y": abs((bbox[1] + bbox[3]) / 2 - 128)}
    bell_x, bell_top = bell_anchor(frame)
    return {"x": abs(bell_x - 128), "y": abs(bell_top - 24)}


def contact_sheet(rows: list[tuple[str, list[Image.Image]]]) -> None:
    label_w = 156
    preview = 128
    board = Image.new("RGB", (label_w + preview * 6, preview * len(rows)), (7, 33, 53))
    draw = ImageDraw.Draw(board)
    for row_index, (name, frames) in enumerate(rows):
        y0 = row_index * preview
        draw.rectangle((0, y0, label_w, y0 + preview), fill=(9, 47, 69))
        draw.text((12, y0 + 54), name, fill=(245, 216, 120))
        for frame_index, frame in enumerate(frames):
            x0 = label_w + frame_index * preview
            for yy in range(y0, y0 + preview, 16):
                for xx in range(x0, x0 + preview, 16):
                    fill = (17, 51, 73) if ((xx - x0) // 16 + (yy - y0) // 16) % 2 else (24, 64, 84)
                    draw.rectangle((xx, yy, xx + 15, yy + 15), fill=fill)
            thumb = frame.resize((preview, preview), Image.Resampling.NEAREST)
            board.paste(thumb, (x0, y0), thumb)
    board.save(REPORTS / "animation-contact-sheet.png", optimize=True)


def main() -> None:
    FRAMES.mkdir(parents=True, exist_ok=True)
    SHEETS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    results = []
    contacts = []
    built_frames = {}

    for name, filename in SPECS.items():
        source = SOURCE / filename
        keyed = SOURCE / f"{name}-alpha.png"
        key_image(source, keyed)
        image = Image.open(keyed).convert("RGBA")
        cell_w, cell_h = image.width // 3, image.height // 2
        frames = []
        for index in range(6):
            col, row = index % 3, index // 3
            cell = image.crop((col * cell_w, row * cell_h, (col + 1) * cell_w, (row + 1) * cell_h))
            if name in {"jellyfish_pulse", "shrimp_swim"}:
                # The widest tentacle pose reaches the source-cell edge; keep a shared
                # inset transform for volatile tentacles/antennae so they never clip.
                registered = cell.resize((232, 232), Image.Resampling.NEAREST)
                frame = Image.new("RGBA", (FRAME_SIZE, FRAME_SIZE), (0, 0, 0, 0))
                frame.alpha_composite(registered, (12, 12))
            else:
                frame = cell.resize((FRAME_SIZE, FRAME_SIZE), Image.Resampling.NEAREST)
            frame = remove_alpha_specks(frame)
            frame = align_frame(name, frame)
            frame_path = FRAMES / f"{name}_{index}.png"
            frame.save(frame_path, optimize=True)
            frames.append(frame)
            result = validate_frame(name, index, frame)
            result["anchor_error"] = anchor_error(name, frame)
            results.append(result)
        sheet = Image.new("RGBA", (FRAME_SIZE * 6, FRAME_SIZE), (0, 0, 0, 0))
        for index, frame in enumerate(frames):
            sheet.alpha_composite(frame, (index * FRAME_SIZE, 0))
        sheet.save(SHEETS / f"{name}.png", optimize=True)
        built_frames[name] = frames
        contacts.append((name, frames))

    contact_sheet(contacts)
    report = {
        "frame_size": FRAME_SIZE,
        "sheets": len(contacts),
        "frames": len(results),
        "passed": sum(1 for item in results if not item["issues"]),
        "failed": sum(1 for item in results if item["issues"]),
        "max_anchor_error": round(max(max(item["anchor_error"].values()) for item in results), 3),
        "results": results,
    }
    (REPORTS / "animation-validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("frame_size", "sheets", "frames", "passed", "failed")}, indent=2))


if __name__ == "__main__":
    main()
