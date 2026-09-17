"""Build the unpacked Chrome extension with Python's standard library only."""
from pathlib import Path
import binascii
import shutil
import struct
import zlib

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"
EXTENSION = ROOT / "extension"
ICONS = EXTENSION / "icons"


def _chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)


def make_icon(path: Path, size: int) -> None:
    """Draw a transparent PNG with the TwinTimes green seal and cream T."""
    rows = []
    center = (size - 1) / 2
    radius = size * .45
    green = (23, 63, 53, 255)
    cream = (242, 236, 223, 255)
    transparent = (0, 0, 0, 0)
    for y in range(size):
        row = bytearray([0])
        for x in range(size):
            inside = (x - center) ** 2 + (y - center) ** 2 <= radius ** 2
            top = size * .27 <= y <= size * .39 and size * .27 <= x <= size * .73
            stem = size * .45 <= x <= size * .55 and size * .30 <= y <= size * .73
            row.extend(cream if inside and (top or stem) else green if inside else transparent)
        rows.append(bytes(row))
    raw = b"".join(rows)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(raw, 9))
    png += _chunk(b"IEND", b"")
    path.write_bytes(png)


def main() -> None:
    EXTENSION.mkdir(exist_ok=True)
    ICONS.mkdir(exist_ok=True)
    for filename in ("index.html", "newsmarks.html", "app.css", "app.js"):
        shutil.copy2(STATIC / filename, EXTENSION / filename)
    for size in (16, 32, 48, 128):
        make_icon(ICONS / f"icon{size}.png", size)
    print(f"Built Chrome extension in {EXTENSION}")


if __name__ == "__main__":
    main()
