"""Builds assets/vibedrop.ico (and a 256 px PNG preview) from the VibeDrop mark.

    python assets/make_icon.py

Pure Python, no Pillow. The mark is the one in vibedrop.svg: a night-blue
rounded square with five sky-blue bars. The corners outside the rounded square
are fully transparent, so Windows shows the rounded tile on the desktop instead
of a square with dark corners.

Every size Windows asks for is drawn on its own (not scaled down from 256 px):
at 16-48 px the bars are snapped to whole pixels so they stay crisp.
"""

from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent

BG = (0x0A, 0x0D, 0x14)
BAR = (0x5A, 0xB9, 0xFC)
CORNER = 56 / 256  # corner radius of the tile, as a share of its side

# bars from vibedrop.svg, in a 256 px box: (x, top), width 18, bottom 180
BARS_X = (59, 89, 119, 149, 179)
BARS_TOP = (126, 94, 58, 106, 134)
BAR_W, BAR_BOTTOM, BAR_R = 18, 180, 9

SIZES = (256, 128, 96, 64, 48, 40, 32, 24, 20, 16)


def rounded_box_distance(px, py, x0, y0, x1, y1, r):
    """Signed distance from (px, py) to a rounded rectangle (negative inside)."""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hx, hy = (x1 - x0) / 2 - r, (y1 - y0) / 2 - r
    qx, qy = abs(px - cx) - hx, abs(py - cy) - hy
    outside = math.hypot(max(qx, 0.0), max(qy, 0.0))
    inside = min(max(qx, qy), 0.0)
    return outside + inside - r


def coverage(distance):
    return min(1.0, max(0.0, 0.5 - distance))


def bars_for(size):
    """Bar rectangles (x0, y0, x1, y1, radius) in pixels for this icon size."""
    k = size / 256
    if size >= 64:
        return [(x * k, top * k, (x + BAR_W) * k, BAR_BOTTOM * k, BAR_R * k)
                for x, top in zip(BARS_X, BARS_TOP)]
    # small sizes: whole-pixel bars, evenly spaced and centred
    width = max(1, round(BAR_W * k))
    pitch = max(width + 1, round(30 * k))
    total = 4 * pitch + width
    left = round((size - total) / 2)
    bottom = round(BAR_BOTTOM * k)
    radius = width / 2 if width >= 3 else 0
    return [(left + i * pitch, round(top * k), left + i * pitch + width, bottom, radius)
            for i, top in enumerate(BARS_TOP)]


def render(size):
    """RGBA rows, top to bottom, straight (non-premultiplied) alpha."""
    corner = CORNER * size
    bars = bars_for(size)
    rows = []
    for y in range(size):
        row = bytearray()
        for x in range(size):
            px, py = x + 0.5, y + 0.5
            tile = coverage(rounded_box_distance(px, py, 0, 0, size, size, corner))
            bar = 0.0
            for x0, y0, x1, y1, r in bars:
                if x0 - 1 <= px <= x1 + 1 and y0 - 1 <= py <= y1 + 1:
                    bar = max(bar, coverage(rounded_box_distance(px, py, x0, y0, x1, y1, r)))
            # bars sit inside the tile, so the tile's alpha is the pixel's alpha
            colour = [round(BG[c] + (BAR[c] - BG[c]) * bar) for c in range(3)]
            row += bytes((*colour, round(255 * tile)))
        rows.append(bytes(row))
    return rows


def png_bytes(size, rows):
    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    raw = b"".join(b"\x00" + row for row in rows)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))


def bmp_bytes(size, rows):
    """32-bit BGRA DIB with its AND mask, the format every Windows shell reads."""
    header = struct.pack("<IiiHHIIiiII", 40, size, size * 2, 1, 32, 0, 0, 0, 0, 0, 0)
    pixels = bytearray()
    for row in reversed(rows):  # DIBs are stored bottom-up
        for i in range(0, len(row), 4):
            r, g, b, a = row[i:i + 4]
            pixels += bytes((b, g, r, a))
    mask_stride = ((size + 31) // 32) * 4
    mask = bytearray()
    for row in reversed(rows):
        bits = bytearray(mask_stride)
        for x in range(size):
            if row[x * 4 + 3] == 0:  # fully transparent: masked out
                bits[x // 8] |= 0x80 >> (x % 8)
        mask += bits
    return header + bytes(pixels) + bytes(mask)


def main():
    images = []
    for size in SIZES:
        rows = render(size)
        data = png_bytes(size, rows) if size >= 256 else bmp_bytes(size, rows)
        images.append((size, data))
        if size == 256:
            (HERE / "vibedrop.png").write_bytes(png_bytes(size, rows))

    offset = 6 + 16 * len(images)
    directory, blobs = b"", b""
    for size, data in images:
        directory += struct.pack("<BBBBHHII", size % 256, size % 256, 0, 0, 1, 32, len(data), offset)
        blobs += data
        offset += len(data)
    out = HERE / "vibedrop.ico"
    out.write_bytes(struct.pack("<HHH", 0, 1, len(images)) + directory + blobs)
    print(f"{out} ({out.stat().st_size // 1024} KB, sizes {', '.join(map(str, SIZES))})")


if __name__ == "__main__":
    main()
