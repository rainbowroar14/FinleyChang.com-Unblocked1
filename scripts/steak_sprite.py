"""Grilled steak sprite — imported by generate_cleaning_sprites.py"""
from __future__ import annotations

import random

from PIL import Image


def _steak_meat_mask(size: int, cx: int, cy: int) -> set[tuple[int, int]]:
    mask: set[tuple[int, int]] = set()
    for y in range(cy - 44, cy + 40):
        for x in range(cx - 54, cx + 54):
            dx, dy = (x - cx) / 52.0, (y - cy) / 38.0
            if dx * dx + dy * dy <= 1.02:
                mask.add((x, y))
    for y in range(cy - 46, cy - 36):
        for x in range(cx - 38, cx + 38):
            if (x - cx) ** 2 / 1500 + (y - (cy - 40)) ** 2 / 100 < 1:
                mask.add((x, y))
    return mask


def draw_steak(bite_level: int = 0, size: int = 128) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cx, cy = size // 2, size // 2 + 6
    rng = random.Random(90 + bite_level)

    meat = _steak_meat_mask(size, cx, cy)

    for x, y in meat:
        sx, sy = x + 5, y + 6
        if 0 <= sx < size and 0 <= sy < size and img.getpixel((sx, sy))[3] == 0:
            img.putpixel((sx, sy), (0, 0, 0, 48))

    for x, y in meat:
        rel_x = (x - cx) / 52.0
        rel_y = (y - cy) / 38.0
        shade = 0.55 + rel_y * 0.35 - rel_x * 0.1
        if shade < 0.65:
            c = (52, 28, 18, 255)
        elif shade < 0.85:
            c = (78, 42, 28, 255)
        else:
            c = (98, 55, 36, 255)
        img.putpixel((x, y), c)

    for _ in range(120 - bite_level * 25):
        x = cx + rng.randint(-50, 50)
        y = cy + rng.randint(-38, 36)
        if (x, y) in meat:
            img.putpixel(
                (x, y),
                rng.choice([(220, 175, 110, 255), (195, 140, 85, 255), (240, 200, 140, 255)]),
            )

    def grill_line(x0: int, y0: int, x1: int, y1: int, width: int = 2) -> None:
        steps = int(max(abs(x1 - x0), abs(y1 - y0)) * 2)
        for i in range(steps + 1):
            t = i / max(1, steps)
            px = int(x0 + (x1 - x0) * t)
            py = int(y0 + (y1 - y0) * t)
            for w in range(-width, width + 1):
                qx, qy = px + w, py + w
                if (qx, qy) in meat:
                    img.putpixel((qx, qy), (28, 14, 10, 255))

    if bite_level < 2:
        for off in range(-44, 48, 14):
            grill_line(cx - 44 + off, cy - 34, cx + 44 + off, cy + 10)
        for off in range(-36, 40, 14):
            grill_line(cx - 36 + off, cy - 40, cx + 36 + off, cy + 14)

    for x, y in meat:
        if x < cx - 8 and y < cy - 6 and rng.random() < 0.08:
            img.putpixel((x, y), (232, 145, 58, 255))
        elif x < cx and y < cy and rng.random() < 0.04:
            img.putpixel((x, y), (200, 110, 45, 255))

    for x, y in meat:
        on_edge = any((x + dx, y + dy) not in meat for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if on_edge and y < cy + 6:
            r, g, b, a = img.getpixel((x, y))
            img.putpixel((x, y), (min(255, r + 22), min(255, g + 16), min(255, b + 10), a))

    if bite_level >= 1:
        bite1 = {
            (x, y)
            for x in range(cx + 2, cx + 54)
            for y in range(cy - 26, cy + 30)
            if (x - (cx + 26)) ** 2 / 380 + (y - cy) ** 2 / 420 < 1
        }
        interior = (168, 72, 58, 255)
        interior_dark = (120, 45, 38, 255)
        for x, y in bite1:
            if (x, y) in meat:
                meat.discard((x, y))
                img.putpixel((x, y), (0, 0, 0, 0))
        for x in range(cx + 2, cx + 30):
            for y in range(cy - 18, cy + 16):
                if (x, y) not in meat and ((x + 1, y) in meat or (x, y + 1) in meat):
                    img.putpixel((x, y), interior if rng.random() > 0.3 else interior_dark)

    if bite_level >= 2:
        bite2 = {
            (x, y)
            for x in range(cx - 52, cx + 12)
            for y in range(cy - 40, cy + 10)
            if (x - (cx - 22)) ** 2 / 520 + (y - (cy - 12)) ** 2 / 380 < 1
        }
        for x, y in bite2:
            if (x, y) in meat:
                meat.discard((x, y))
                img.putpixel((x, y), (0, 0, 0, 0))
        for x in range(cx - 40, cx - 8):
            for y in range(cy - 28, cy + 4):
                if (x, y) not in meat and ((x + 1, y) in meat or (x, y + 1) in meat):
                    img.putpixel(
                        (x, y),
                        (155, 65, 50, 255) if rng.random() > 0.35 else (110, 40, 32, 255),
                    )

    for x, y in meat:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) not in meat and 0 <= nx < size and 0 <= ny < size:
                img.putpixel((nx, ny), (0, 0, 0, 255))

    return img.resize((256, 256), Image.Resampling.NEAREST)
