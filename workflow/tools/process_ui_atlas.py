#!/usr/bin/env python3
"""Split the generated 4x4 UI atlas into validated transparent pixel assets."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "ui" / "source" / "reef-ui-atlas.png"
GROWTH_SOURCE = ROOT / "assets" / "ui" / "source" / "growth-progress-icon-source.png"
OUTPUT = ROOT / "assets" / "ui" / "processed"
REPORT = ROOT / "reports" / "ui"
NAMES = [
    "hud_panel", "growth_frame", "lives_panel", "round_button",
    "dialog_panel", "toast_panel", "tip_panel", "action_button",
    "icon_star", "icon_heart", "icon_pause", "icon_music",
    "icon_play", "icon_boost", "icon_pearl", "icon_warning",
]


def is_key(pixel: tuple[int, int, int, int]) -> bool:
    r, g, b, _ = pixel
    # Generated key colors vary from hot pink to dark magenta on a few edge
    # pixels. Keep blue/navy outlines by requiring red to dominate green too.
    return (
        r > 48 and b > 78 and g < 112
        and r > g * 1.28 and b > g * 1.52
        and abs(r - b) < 142
    )


def checker(size: tuple[int, int], step: int = 12) -> Image.Image:
    out = Image.new("RGB", size, "#173d58")
    draw = ImageDraw.Draw(out)
    for y in range(0, size[1], step):
        for x in range(0, size[0], step):
            if (x // step + y // step) % 2:
                draw.rectangle((x, y, x + step - 1, y + step - 1), fill="#245874")
    return out


def keep_components_centered_in(cell: Image.Image, bounds: tuple[int, int, int, int]) -> Image.Image:
    """Drop neighbouring-cell fragments while preserving multi-part icons."""
    alpha = cell.getchannel("A")
    mask = alpha.point(lambda value: 255 if value > 8 else 0)
    seen: set[tuple[int, int]] = set()
    keep: set[tuple[int, int]] = set()
    left, top, right, bottom = bounds
    for y in range(cell.height):
        for x in range(cell.width):
            if (x, y) in seen or not mask.getpixel((x, y)):
                continue
            stack = [(x, y)]
            seen.add((x, y))
            component: list[tuple[int, int]] = []
            while stack:
                px, py = stack.pop()
                component.append((px, py))
                for nx, ny in ((px - 1, py), (px + 1, py), (px, py - 1), (px, py + 1)):
                    if 0 <= nx < cell.width and 0 <= ny < cell.height and (nx, ny) not in seen and mask.getpixel((nx, ny)):
                        seen.add((nx, ny))
                        stack.append((nx, ny))
            min_x = min(point[0] for point in component)
            max_x = max(point[0] for point in component)
            min_y = min(point[1] for point in component)
            max_y = max(point[1] for point in component)
            center_x, center_y = (min_x + max_x) / 2, (min_y + max_y) / 2
            if len(component) >= 100 and left <= center_x < right and top <= center_y < bottom:
                keep.update(component)
    cleaned = Image.new("RGBA", cell.size, (0, 0, 0, 0))
    source = cell.load()
    target = cleaned.load()
    for x, y in keep:
        target[x, y] = source[x, y]
    return cleaned


def main() -> None:
    atlas = Image.open(SOURCE).convert("RGBA")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    REPORT.mkdir(parents=True, exist_ok=True)
    records = []
    contact = Image.new("RGB", (4 * 300, 5 * 300), "#102f48")
    contact_draw = ImageDraw.Draw(contact)

    for index, name in enumerate(NAMES):
        col, row = index % 4, index // 4
        left, right = round(col * atlas.width / 4), round((col + 1) * atlas.width / 4)
        top, bottom = round(row * atlas.height / 4), round((row + 1) * atlas.height / 4)
        expand = 38
        crop_left, crop_top = max(0, left - expand), max(0, top - expand)
        crop_right, crop_bottom = min(atlas.width, right + expand), min(atlas.height, bottom + expand)
        cell = atlas.crop((crop_left, crop_top, crop_right, crop_bottom))
        pixels = list(cell.getdata())
        keyed = [(r, g, b, 0 if is_key((r, g, b, a)) else a) for r, g, b, a in pixels]
        cell.putdata(keyed)
        cell = keep_components_centered_in(
            cell,
            (left - crop_left, top - crop_top, right - crop_left, bottom - crop_top),
        )
        alpha = cell.getchannel("A")
        box = alpha.getbbox()
        if not box:
            raise RuntimeError(f"{name}: empty after chroma removal")
        pad = 8
        box = (
            max(0, box[0] - pad), max(0, box[1] - pad),
            min(cell.width, box[2] + pad), min(cell.height, box[3] + pad),
        )
        item = cell.crop(box)
        output_path = OUTPUT / f"{name}.png"
        item.save(output_path, optimize=True)

        visible = [(r, g, b, a) for r, g, b, a in item.getdata() if a > 8]
        magenta = sum(1 for r, g, b, _ in visible if r > 160 and b > 160 and g < 100)
        alpha_box = item.getchannel("A").getbbox()
        touches = bool(alpha_box and (alpha_box[0] == 0 or alpha_box[1] == 0 or alpha_box[2] == item.width or alpha_box[3] == item.height))
        issues = []
        if magenta:
            issues.append("magenta-residue")
        if touches:
            issues.append("cropped-edge")
        records.append({
            "name": name,
            "size": list(item.size),
            "visible_pixels": len(visible),
            "magenta_pixels": magenta,
            "touches_edge": touches,
            "status": "pass" if not issues else "fail",
            "issues": issues,
        })

        tile = checker((260, 232))
        scale = min(224 / item.width, 194 / item.height, 1)
        preview = item.resize((max(1, round(item.width * scale)), max(1, round(item.height * scale))), Image.Resampling.NEAREST)
        tile.paste(preview, ((260 - preview.width) // 2, (220 - preview.height) // 2), preview)
        x, y = col * 300 + 20, row * 300 + 20
        contact.paste(tile, (x, y))
        contact_draw.text((x, y + 246), name, fill="#d9fbff")

    growth = Image.open(GROWTH_SOURCE).convert("RGBA")
    growth.putdata([
        (r, g, b, 0 if is_key((r, g, b, a)) else a)
        for r, g, b, a in growth.getdata()
    ])
    growth_box = growth.getchannel("A").getbbox()
    if not growth_box:
        raise RuntimeError("icon_growth: empty after chroma removal")
    pad = 12
    growth_box = (
        max(0, growth_box[0] - pad), max(0, growth_box[1] - pad),
        min(growth.width, growth_box[2] + pad), min(growth.height, growth_box[3] + pad),
    )
    growth = growth.crop(growth_box)
    growth.save(OUTPUT / "icon_growth.png", optimize=True)
    visible = [(r, g, b, a) for r, g, b, a in growth.getdata() if a > 8]
    magenta = sum(1 for r, g, b, _ in visible if r > 160 and b > 160 and g < 100)
    alpha_box = growth.getchannel("A").getbbox()
    touches = bool(alpha_box and (
        alpha_box[0] == 0 or alpha_box[1] == 0
        or alpha_box[2] == growth.width or alpha_box[3] == growth.height
    ))
    issues = []
    if magenta:
        issues.append("magenta-residue")
    if touches:
        issues.append("cropped-edge")
    records.append({
        "name": "icon_growth",
        "size": list(growth.size),
        "visible_pixels": len(visible),
        "magenta_pixels": magenta,
        "touches_edge": touches,
        "status": "pass" if not issues else "fail",
        "issues": issues,
    })
    tile = checker((260, 232))
    scale = min(224 / growth.width, 194 / growth.height, 1)
    preview = growth.resize(
        (max(1, round(growth.width * scale)), max(1, round(growth.height * scale))),
        Image.Resampling.NEAREST,
    )
    tile.paste(preview, ((260 - preview.width) // 2, (220 - preview.height) // 2), preview)
    contact.paste(tile, (20, 4 * 300 + 20))
    contact_draw.text((20, 4 * 300 + 266), "icon_growth", fill="#d9fbff")

    (REPORT / "ui-validation.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    contact.save(REPORT / "ui-contact-sheet.png", optimize=True)
    failed = [r for r in records if r["status"] != "pass"]
    print(f"Processed {len(records)} UI assets; {len(records) - len(failed)} passed, {len(failed)} failed")
    if failed:
        for record in failed:
            print(record["name"], record["issues"])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
