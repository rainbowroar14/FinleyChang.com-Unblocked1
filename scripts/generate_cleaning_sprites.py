"""Generate 256x256 pixel-art cleaning sprites (plate, sponge, stains, bubbles)."""
from __future__ import annotations

import math
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = Path(__file__).resolve().parent
import sys

if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
OUT = ROOT / "assets" / "cleaning"
SIZE = 256
SCALE = 4  # draw at 64, scale to 256


def scale_up(img: Image.Image) -> Image.Image:
    w, h = img.size
    return img.resize((w * SCALE, h * SCALE), Image.Resampling.NEAREST)


def crop_to_content(img: Image.Image, pad: int = 2) -> Image.Image:
    """Trim transparent margins, then fit the art into a square canvas."""
    bbox = img.getbbox()
    if not bbox:
        return img
    x0, y0, x1, y1 = bbox
    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(img.width, x1 + pad)
    y1 = min(img.height, y1 + pad)
    cropped = img.crop((x0, y0, x1, y1))
    side = max(cropped.width, cropped.height)
    out = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    ox = (side - cropped.width) // 2
    oy = (side - cropped.height) // 2
    out.paste(cropped, (ox, oy))
    return out.resize((SIZE, SIZE), Image.Resampling.NEAREST)


def save_rgba(img: Image.Image, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    img.save(path, optimize=True)
    print("wrote", path)


def draw_plate(size: int = 64) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    r_outer = 28
    r_inner = 20

    # soft shadow under plate
    for i in range(3):
        d.ellipse(
            (cx - r_outer + 2, cy - r_outer + 4 + i, cx + r_outer + 2, cy + r_outer + 4 + i),
            fill=(0, 0, 0, 30 - i * 8),
        )

    # outer rim base
    d.ellipse(
        (cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer),
        fill=(168, 178, 198, 255),
        outline=(0, 0, 0, 255),
        width=1,
    )

    # rim shading (top darker, bottom lighter)
    for angle in range(0, 360, 2):
        rad = math.radians(angle)
        x = cx + math.cos(rad) * (r_outer - 2)
        y = cy + math.sin(rad) * (r_outer - 2)
        if math.sin(rad) < -0.15:
            c = (130, 138, 158, 90)
        elif math.sin(rad) > 0.2:
            c = (210, 218, 232, 110)
        else:
            c = (175, 185, 205, 50)
        d.point((int(x), int(y)), fill=c)

    # solid inner bowl (fully opaque — no transparent center)
    d.ellipse(
        (cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner),
        fill=(148, 158, 178, 255),
        outline=(0, 0, 0, 255),
        width=1,
    )

    # inner rim shadow (top arc) — opaque pixels only
    for x in range(cx - r_inner, cx + r_inner):
        for y in range(cy - r_inner, cy + r_inner):
            dx, dy = x - cx, y - cy
            dist = math.hypot(dx, dy)
            if r_inner - 4 < dist < r_inner - 1 and dy < -2:
                img.putpixel((x, y), (100, 108, 124, 255))
            elif r_inner - 4 < dist < r_inner - 1 and dy > 3:
                img.putpixel((x, y), (218, 226, 240, 255))

    # center highlight (opaque)
    d.ellipse((cx - 10, cy - 8, cx + 12, cy + 10), fill=(198, 208, 224, 255))

    # subtle ceramic speckles (opaque)
    rng = random.Random(42)
    for _ in range(28):
        px = cx + rng.randint(-18, 18)
        py = cy + rng.randint(-18, 18)
        if math.hypot(px - cx, py - cy) < r_inner - 6:
            img.putpixel(
                (px, py),
                (rng.randint(155, 195), rng.randint(165, 205), rng.randint(180, 220), 255),
            )

    return crop_to_content(scale_up(img))


def draw_sponge(size: int = 64) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # rounded rect body
    body = (14, 18, 50, 46)
    d.rounded_rectangle(body, radius=8, fill=(248, 210, 55, 255), outline=(0, 0, 0, 255), width=1)
    # side depth
    d.polygon(
        [(50, 22), (56, 26), (56, 42), (50, 46), (50, 22)],
        fill=(210, 140, 35, 255),
        outline=(0, 0, 0, 255),
    )
    d.polygon(
        [(50, 22), (56, 26), (56, 30), (50, 28)],
        fill=(255, 235, 120, 255),
    )

    rng = random.Random(7)
    pore_colors = [(200, 130, 25, 255), (180, 110, 20, 255), (230, 170, 40, 255), (255, 240, 150, 255)]
    for _ in range(90):
        px = rng.randint(16, 48)
        py = rng.randint(20, 44)
        if py > 38 and px > 44:
            continue
        img.putpixel((px, py), pore_colors[rng.randint(0, len(pore_colors) - 1)])

    # scrub surface highlight strips
    for y in range(22, 40, 3):
        for x in range(18, 46):
            if rng.random() < 0.12:
                img.putpixel((x, y), (255, 245, 170, 120))

    # outline touch-ups
    d.rounded_rectangle(body, radius=8, outline=(0, 0, 0, 255), width=1)
    return scale_up(img)


def draw_bowl(size: int = 64) -> Image.Image:
    """Top-down ceramic bowl — terracotta rim, dark interior."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = 32, 33

    # drop shadow
    d.ellipse((cx - 24, cy + 14, cx + 25, cy + 22), fill=(0, 0, 0, 55))

    # outer bowl body
    d.ellipse((cx - 25, cy - 22, cx + 26, cy + 20), fill=(154, 107, 69, 255), outline=(0, 0, 0, 255), width=1)

    # inner cavity (darker)
    d.ellipse((cx - 19, cy - 14, cx + 20, cy + 16), fill=(107, 68, 40, 255))
    d.ellipse((cx - 14, cy - 6, cx + 15, cy + 14), fill=(61, 37, 24, 255))

    # rim highlight (top arc)
    for x in range(cx - 22, cx + 23):
        t = (x - (cx - 22)) / 44.0
        y = cy - 20 + int(4 * (1 - (t - 0.5) ** 2 * 4))
        if 0 <= y < size:
            img.putpixel((x, y), (212, 165, 116, 255))
    d.arc((cx - 22, cy - 22, cx + 23, cy - 8), 200, 340, fill=(0, 0, 0, 255), width=1)

    # ceramic speckle / wear
    rng = random.Random(41)
    for _ in range(45):
        x, y = rng.randint(cx - 20, cx + 20), rng.randint(cy - 12, cy + 10)
        if img.getpixel((x, y))[3] > 0:
            img.putpixel((x, y), (rng.randint(130, 175), rng.randint(95, 125), rng.randint(55, 80), 255))

    # inner shadow edge
    for ang in range(200, 340):
        rad = math.radians(ang)
        x = int(cx + math.cos(rad) * 18)
        y = int(cy + 4 + math.sin(rad) * 12)
        if 0 <= x < size and 0 <= y < size:
            p = img.getpixel((x, y))
            if p[3] > 0:
                img.putpixel((x, y), (max(0, p[0] - 25), max(0, p[1] - 20), max(0, p[2] - 15), 255))

    d.ellipse((cx - 25, cy - 22, cx + 26, cy + 20), outline=(0, 0, 0, 255), width=1)
    return scale_up(img)


def draw_mug(size: int = 64) -> Image.Image:
    """Coffee mug — cream body, red band, dark coffee, side handle."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = 30, 32

    # shadow
    d.rounded_rectangle((cx - 18, cy + 22, cx + 20, cy + 26), radius=2, fill=(0, 0, 0, 50))

    # mug body
    body = (cx - 18, cy - 20, cx + 18, cy + 22)
    d.rounded_rectangle(body, radius=5, fill=(236, 232, 224, 255), outline=(0, 0, 0, 255), width=1)

    # red band
    d.rectangle((cx - 16, cy - 2, cx + 16, cy + 8), fill=(214, 40, 40, 255))

    # coffee surface (ellipse at top)
    d.ellipse((cx - 12, cy - 22, cx + 12, cy - 12), fill=(61, 37, 24, 255))
    d.ellipse((cx - 9, cy - 21, cx + 9, cy - 14), fill=(45, 28, 18, 255))
    # coffee highlight
    d.ellipse((cx - 5, cy - 20, cx + 2, cy - 17), fill=(90, 55, 35, 120))

    # left shading on mug
    for y in range(cy - 18, cy + 20):
        for x in range(cx - 17, cx - 12):
            p = img.getpixel((x, y))
            if p[3] > 200:
                img.putpixel((x, y), (210, 206, 198, 255))

    # right highlight
    for y in range(cy - 16, cy + 18):
        img.putpixel((cx + 15, y), (255, 252, 245, 255))

    # handle (right side) — two arcs
    d.arc((cx + 14, cy - 10, cx + 30, cy + 10), 270, 90, fill=(200, 196, 188, 255), width=4)
    d.arc((cx + 16, cy - 8, cx + 28, cy + 8), 270, 90, fill=(0, 0, 0, 0), width=2)
    # handle opening (inner cut)
    d.arc((cx + 18, cy - 6, cx + 26, cy + 6), 270, 90, fill=(0, 0, 0, 0), width=3)

    # redraw body outline over handle overlap
    d.rounded_rectangle(body, radius=5, outline=(0, 0, 0, 255), width=1)
    # handle outline
    d.arc((cx + 14, cy - 10, cx + 30, cy + 10), 270, 90, fill=(0, 0, 0, 255), width=1)

    # band outline touch
    d.line((cx - 16, cy - 2, cx + 16, cy - 2), fill=(0, 0, 0, 255), width=1)
    d.line((cx - 16, cy + 8, cx + 16, cy + 8), fill=(0, 0, 0, 255), width=1)

    return scale_up(img)


def organic_blob(
    d: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    fill: tuple[int, int, int, int],
    seed: int,
) -> None:
    rng = random.Random(seed)
    pts = []
    for i in range(24):
        ang = 2 * math.pi * i / 24
        wobble = 0.75 + rng.random() * 0.45
        x = cx + math.cos(ang) * rx * wobble
        y = cy + math.sin(ang) * ry * wobble
        pts.append((x, y))
    d.polygon(pts, fill=fill)


def draw_stain_sauce(size: int = 64) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    organic_blob(d, 32, 34, 18, 14, (120, 35, 28, 210), 1)
    organic_blob(d, 28, 30, 10, 8, (160, 50, 35, 180), 2)
    organic_blob(d, 38, 36, 8, 6, (90, 25, 20, 200), 3)
    # drip
    for y in range(40, 52):
        a = int(180 - (y - 40) * 12)
        d.ellipse((30, y, 36, y + 3), fill=(100, 30, 25, max(0, a)))
    # crust edge pixels
    rng = random.Random(11)
    for _ in range(120):
        x, y = rng.randint(14, 50), rng.randint(18, 48)
        if img.getpixel((x, y))[3] > 0:
            img.putpixel((x, y), (70, 20, 15, min(255, img.getpixel((x, y))[3] + 40)))
    for _ in range(80):
        x, y = rng.randint(16, 48), rng.randint(20, 46)
        if img.getpixel((x, y))[3] == 0 and rng.random() < 0.15:
            img.putpixel((x, y), (140, 45, 30, rng.randint(40, 90)))
    return scale_up(img)


def draw_stain_grease(size: int = 64) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    organic_blob(d, 34, 32, 20, 12, (55, 48, 35, 170), 4)
    organic_blob(d, 26, 36, 12, 9, (75, 65, 45, 150), 5)
    # shiny grease highlights
    d.ellipse((24, 26, 32, 30), fill=(130, 120, 90, 90))
    d.ellipse((36, 30, 44, 34), fill=(150, 140, 100, 70))
    rng = random.Random(22)
    for _ in range(100):
        x, y = rng.randint(16, 50), rng.randint(22, 42)
        p = img.getpixel((x, y))
        if p[3] > 50:
            img.putpixel((x, y), (min(255, p[0] + 15), min(255, p[1] + 12), p[2], p[3]))
    return scale_up(img)


def draw_dirt_specs(size: int = 64) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rng = random.Random(33)
    colors = [
        (80, 55, 35, 220),
        (95, 70, 45, 200),
        (60, 42, 28, 230),
        (110, 85, 55, 180),
        (45, 32, 22, 240),
    ]
    for _ in range(200):
        x, y = rng.randint(8, 56), rng.randint(10, 54)
        r = rng.randint(1, 3)
        c = colors[rng.randint(0, len(colors) - 1)]
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    # greenish mold speck
    for _ in range(40):
        x, y = rng.randint(12, 52), rng.randint(14, 50)
        d.point((x, y), fill=(55, 75, 40, rng.randint(100, 180)))
    return scale_up(img)


def draw_stain_crumb(size: int = 64) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rng = random.Random(44)
    for _ in range(60):
        x, y = rng.randint(18, 46), rng.randint(20, 44)
        w, h = rng.randint(2, 5), rng.randint(2, 4)
        col = (rng.randint(130, 180), rng.randint(90, 120), rng.randint(40, 70), rng.randint(160, 230))
        d.rectangle((x, y, x + w, y + h), fill=col, outline=(80, 50, 25, 200))
    organic_blob(d, 32, 33, 14, 10, (100, 70, 40, 120), 6)
    return scale_up(img)


def draw_bubble(size: int = 64) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    clusters = [(20, 24, 9), (34, 30, 11), (26, 38, 7), (40, 22, 6), (16, 36, 5)]
    for cx, cy, r in clusters:
        d.ellipse(
            (cx - r, cy - r, cx + r, cy + r),
            fill=(170, 220, 255, 140),
            outline=(80, 150, 210, 200),
            width=1,
        )
        # highlight
        hr = max(2, r // 3)
        d.ellipse(
            (cx - r // 2, cy - r // 2, cx - r // 2 + hr, cy - r // 2 + hr),
            fill=(245, 252, 255, 220),
        )
        # secondary tiny bubble
        if r > 6:
            d.ellipse(
                (cx + r - 2, cy + 1, cx + r + 3, cy + 5),
                fill=(200, 235, 255, 100),
                outline=(120, 180, 230, 150),
                width=1,
            )
    return scale_up(img)


def draw_steak(bite_level: int = 0, size: int = 128) -> Image.Image:
    from steak_sprite import draw_steak as _draw_steak

    return crop_to_content(_draw_steak(bite_level, size), pad=4)


def draw_bubble_small(size: int = 64) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((24, 24, 40, 40), fill=(185, 230, 255, 160), outline=(90, 160, 220, 200), width=1)
    d.ellipse((28, 26, 32, 30), fill=(250, 255, 255, 230))
    return scale_up(img)


def write_embedded_js() -> None:
    import base64
    import json

    names = [
        "plate",
        "bowl",
        "mug",
        "sponge",
        "stain_sauce",
        "stain_grease",
        "dirt_specs",
        "stain_crumb",
        "bubble",
        "bubble_small",
        "steak_full",
        "steak_bite1",
        "steak_bite2",
    ]
    out = {}
    for name in names:
        path = OUT / f"{name}.png"
        out[name] = base64.b64encode(path.read_bytes()).decode("ascii")
    js_path = OUT / "cleaning-sprites-data.js"
    js_path.write_text("window.CLEANING_SPRITE_DATA = " + json.dumps(out) + ";\n", encoding="utf-8")
    print("wrote", js_path)


def main() -> None:
    random.seed(0)
    save_rgba(draw_plate(), "plate.png")
    save_rgba(draw_bowl(), "bowl.png")
    save_rgba(draw_mug(), "mug.png")
    save_rgba(draw_sponge(), "sponge.png")
    save_rgba(draw_stain_sauce(), "stain_sauce.png")
    save_rgba(draw_stain_grease(), "stain_grease.png")
    save_rgba(draw_dirt_specs(), "dirt_specs.png")
    save_rgba(draw_stain_crumb(), "stain_crumb.png")
    save_rgba(draw_bubble(), "bubble.png")
    save_rgba(draw_bubble_small(), "bubble_small.png")
    save_rgba(draw_steak(0), "steak_full.png")
    save_rgba(draw_steak(1), "steak_bite1.png")
    save_rgba(draw_steak(2), "steak_bite2.png")
    write_embedded_js()
    print("done —", OUT)
    print("Run: python scripts/inline_cleaning_data.py  (after regenerating, if index needs refresh)")


if __name__ == "__main__":
    main()
