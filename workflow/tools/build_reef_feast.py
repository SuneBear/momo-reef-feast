#!/usr/bin/env python3
"""Build the standalone side-scrolling reef feast game."""

from __future__ import annotations

import base64
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "src" / "momo-reef-feast.template.html"
OUTPUT = ROOT / "momo-reef-feast.html"
WEB_DIR = ROOT / "momo-reef-feast"
REFERENCE = Path("/Users/sunebear/Code/Zworks/Wsune/creative-refs-2025/momoyu-app/V1/assets/s.anyway.red/momoyu")

ANIMATIONS = ROOT / "assets" / "animation" / "sheets"
ANIMATION_EXCLUDES = {"minnow_coral", "minnow_cyan", "minnow_green"}
BACKGROUNDS = ROOT / "assets" / "background"
DEPTH = ROOT / "assets" / "depth"
AUDIO = ROOT / "assets" / "audio"
UI = ROOT / "assets" / "ui" / "processed"
WORKFLOW_SCRIPTS = [
    ROOT / "tools" / "process_animation_sheets.py",
    ROOT / "tools" / "process_ui_atlas.py",
    ROOT / "tools" / "slice_ui_frames.py",
    ROOT / "tools" / "build_reef_feast.py",
]
WORKFLOW_REPORTS = [
    (ROOT / "reports" / "animation" / "animation-validation.json", "animation-validation.json"),
    (ROOT / "reports" / "animation" / "animation-contact-sheet.png", "animation-contact-sheet.png"),
    (ROOT / "reports" / "background-pixel-assets.png", "scene-contact-sheet.png"),
    (ROOT / "reports" / "depth-assets.png", "depth-contact-sheet.png"),
    (ROOT / "reports" / "ui" / "ui-validation.json", "ui-validation.json"),
    (ROOT / "reports" / "ui" / "ui-contact-sheet.png", "ui-contact-sheet.png"),
    (ROOT / "reports" / "ui" / "slice-manifest.json", "slice-manifest.json"),
]
WORKFLOW_SOURCES = sorted((ROOT / "assets" / "animation" / "source").glob("*-source.png")) + [
    ROOT / "assets" / "ui" / "source" / "reef-ui-atlas.png",
    ROOT / "assets" / "ui" / "source" / "icon-watch-generated.png",
    ROOT / "assets" / "ui" / "source" / "growth-progress-icon-source.png",
]


def data_url(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def video_data_url(path: Path) -> str:
    return "data:video/mp4;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def audio_data_url(path: Path) -> str:
    mime = {".ogg": "audio/ogg", ".mp3": "audio/mpeg", ".wav": "audio/wav"}[path.suffix.lower()]
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def render_html(manifest: dict[str, str], video_url: str, audio_urls: dict[str, str]) -> str:
    output = TEMPLATE.read_text(encoding="utf-8")
    replacements = {
        "__ASSET_MANIFEST__": json.dumps(manifest, ensure_ascii=False, separators=(",", ":")),
        "__WATER_VIDEO__": video_url,
        "__BGM_AMBIENT__": audio_urls["ambient"],
        "__BGM_CHASE__": audio_urls["chase"],
        "__SFX_EAT_SMALL__": audio_urls["eat_small"],
        "__SFX_EAT_HEAVY__": audio_urls["eat_heavy"],
        "__SFX_BUBBLE_POP__": audio_urls["bubble_pop"],
        "__SFX_PLAYER_HIT__": audio_urls["player_hit"],
    }
    for marker, value in replacements.items():
        if output.count(marker) != 1:
            raise RuntimeError(f"Template must contain exactly one {marker} marker")
        output = output.replace(marker, value)
    return output


def main() -> None:
    image_paths = [path for path in sorted(ANIMATIONS.glob("*.png")) if path.stem not in ANIMATION_EXCLUDES]
    image_paths += sorted(BACKGROUNDS.glob("*.png"))
    image_paths += sorted(DEPTH.glob("depth_*.png"))
    # Runtime UI uses flexible CSS shapes plus the generated pixel icons.
    # Decorative frame and slice sources remain workflow artifacts only.
    image_paths += sorted(UI.glob("icon_*.png"))
    image_paths += [UI / "dialog_panel.png", UI / "toast_panel.png"]
    video_path = REFERENCE / "loop10.mp4"
    audio_paths = {
        "ambient": AUDIO / "underwater-ambient-pad.ogg",
        "chase": AUDIO / "frenzied-swimming.ogg",
        "eat_small": AUDIO / "sfx" / "eat-cute-small.wav",
        "eat_heavy": AUDIO / "sfx" / "eat-cute-heavy.wav",
        "bubble_pop": AUDIO / "sfx" / "bubble-pop.ogg",
        "player_hit": AUDIO / "sfx" / "player-hit.mp3",
    }

    embedded_manifest = {path.stem: data_url(path) for path in image_paths}
    standalone = render_html(
        embedded_manifest,
        video_data_url(video_path),
        {name: audio_data_url(path) for name, path in audio_paths.items()},
    )
    OUTPUT.write_text(standalone, encoding="utf-8")

    image_dir = WEB_DIR / "assets" / "images"
    audio_dir = WEB_DIR / "assets" / "audio"
    media_dir = WEB_DIR / "assets" / "media"
    workflow_tools = WEB_DIR / "workflow" / "tools"
    workflow_reports = WEB_DIR / "workflow" / "reports"
    workflow_sources = WEB_DIR / "workflow" / "sources"
    for directory in (image_dir, audio_dir, media_dir, workflow_tools, workflow_reports, workflow_sources):
        if directory.exists():
            shutil.rmtree(directory)
    for metadata_file in WEB_DIR.rglob(".DS_Store"):
        metadata_file.unlink()
    for directory in (image_dir, audio_dir, media_dir, workflow_tools, workflow_reports, workflow_sources):
        directory.mkdir(parents=True, exist_ok=True)
    web_manifest = {}
    for path in image_paths:
        target = image_dir / f"{path.stem}.png"
        shutil.copy2(path, target)
        web_manifest[path.stem] = f"assets/images/{target.name}"
    for name, path in audio_paths.items():
        shutil.copy2(path, audio_dir / path.name)
    shutil.copy2(AUDIO / "CREDITS.md", audio_dir / "CREDITS.md")
    shutil.copy2(video_path, media_dir / "water-light.mp4")
    for path in WORKFLOW_SCRIPTS:
        shutil.copy2(path, workflow_tools / path.name)
    for path, target_name in WORKFLOW_REPORTS:
        shutil.copy2(path, workflow_reports / target_name)
    for path in WORKFLOW_SOURCES:
        shutil.copy2(path, workflow_sources / path.name)
    web_html = render_html(
        web_manifest,
        "assets/media/water-light.mp4",
        {
            "ambient": "assets/audio/underwater-ambient-pad.ogg",
            "chase": "assets/audio/frenzied-swimming.ogg",
            "eat_small": "assets/audio/eat-cute-small.wav",
            "eat_heavy": "assets/audio/eat-cute-heavy.wav",
            "bubble_pop": "assets/audio/bubble-pop.ogg",
            "player_hit": "assets/audio/player-hit.mp3",
        },
    )
    (WEB_DIR / "index.html").write_text(web_html, encoding="utf-8")
    print(
        f"Wrote {OUTPUT} and {WEB_DIR / 'index.html'} with {len(embedded_manifest)} images, "
        f"{len(audio_paths)} audio tracks and 1 water-light video "
        f"({OUTPUT.stat().st_size:,} bytes)"
    )


if __name__ == "__main__":
    main()
