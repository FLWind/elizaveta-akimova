#!/usr/bin/env python3
"""Regenerate committed PNG/ICO icons from static/favicon.svg.

Fedora: sudo dnf install inkscape python3-pillow
Not needed for a normal Hugo build.
"""
from pathlib import Path
import subprocess
import tempfile

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "static"
BACKGROUND = "#171923"

with tempfile.TemporaryDirectory() as temporary:
    raster = Path(temporary) / "master.png"
    subprocess.run([
        "inkscape", str(STATIC / "favicon.svg"),
        "--export-width=2048", "--export-height=2048",
        f"--export-filename={raster}",
    ], check=True)
    with Image.open(raster) as source:
        master = source.convert("RGBA")

    for size in (16, 32, 48, 96):
        master.resize((size, size), Image.Resampling.LANCZOS).save(
            STATIC / f"favicon-{size}x{size}.png", optimize=True)
    master.resize((256, 256), Image.Resampling.LANCZOS).save(
        STATIC / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

    # Opaque backgrounds let operating systems apply their own corner masks.
    for name, size, scale in (
        ("apple-touch-icon.png", 180, 1),
        ("web-app-manifest-192x192.png", 192, 1),
        ("web-app-manifest-512x512.png", 512, 1),
        ("web-app-manifest-maskable-512x512.png", 512, 0.8),
    ):
        canvas = Image.new("RGB", (size, size), BACKGROUND)
        mark_size = round(size * scale)
        mark = master.resize((mark_size, mark_size), Image.Resampling.LANCZOS)
        offset = (size - mark_size) // 2
        canvas.paste(mark, (offset, offset), mark)
        canvas.save(STATIC / name, optimize=True)

print("Generated favicon PNG/ICO, Apple touch icon and web app icons.")
