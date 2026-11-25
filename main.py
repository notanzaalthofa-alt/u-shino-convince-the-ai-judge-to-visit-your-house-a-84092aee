#!/usr/bin/env python3
"""make.fun entry: Convince the AI Judge to Visit Your House.

Writes one image, /output/entry.png (1024x1024, RGB PNG, pure stdlib).
A charming hand-lettered invitation: a garden scene with a little house,
a comfy armchair and a cup of tea, above a short letter to the AI judge.
Deterministic: no clock, no randomness, no network, stdlib only.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
CREAM = (255, 246, 220)
PAPER = (255, 248, 231)
INK = (74, 50, 38)          # dark brown lettering
RUST = (181, 83, 60)        # terracotta title / border
SKY = (207, 232, 245)
SUN = (255, 201, 60)
GRASS = (127, 176, 105)
LEAF = (74, 140, 74)
HOUSE_WALL = (247, 217, 160)
ROOF = (192, 57, 43)
DOOR = (123, 75, 42)
CHAIR = (217, 108, 79)
CHAIR_DARK = (178, 84, 58)
WAX = (176, 58, 46)
WHITE = (255, 255, 255)
CLOUD = (255, 255, 255)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits, "1" = ink.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "10110", "11001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10001", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01101", "10011", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "10110", "11001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "10110", "11001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "11110", "10000", "10000"),
    "q": ("00000", "00000", "01101", "10011", "10001", "01111", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11100", "01000", "01000", "01000", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
}

# ---------------------------------------------------------------- framebuffer
px = bytearray(W * H * 3)


def set_px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i + 1], px[i + 2] = color


def fill_rect(x0, y0, x1, y1, color):
    x0 = max(0, x0); y0 = max(0, y0)
    x1 = min(W, x1); y1 = min(H, y1)
    for y in range(y0, y1):
        base = (y * W + x0) * 3
        for x in range(x0, x1):
            i = base + (x - x0) * 3
            px[i], px[i + 1], px[i + 2] = color


def circle(cx, cy, r, color):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                set_px(x, y, color)


def ring(cx, cy, r, thick, color):
    for y in range(cy - r - thick, cy + r + thick + 1):
        for x in range(cx - r - thick, cx + r + thick + 1):
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            if (r - thick) ** 2 <= d2 <= (r + thick) ** 2:
                set_px(x, y, color)


def line(x0, y0, x1, y1, color, thick=1):
    dx = abs(x1 - x0); dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        for tx in range(-thick // 2, thick // 2 + 1):
            for ty in range(-thick // 2, thick // 2 + 1):
                set_px(x + tx, y + ty, color)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy; x += sx
        if e2 <= dx:
            err += dx; y += sy


def triangle(x0, y0, x1, y1, x2, y2, color):
    # fill by scanline between edges
    def edge(a, b, y):
        (ax, ay), (bx, by) = a, b
        if ay == by:
            return None
        if ay > by:
            (ax, ay), (bx, by) = (bx, by), (ax, ay)
        if y < ay or y >= by:
            return None
        return ax + (bx - ax) * (y - ay) / (by - ay)
    pts = [(x0, y0), (x1, y1), (x2, y2)]
    ymin = min(p[1] for p in pts); ymax = max(p[1] for p in pts)
    for y in range(ymin, ymax + 1):
        xs = []
        for i in range(3):
            v = edge(pts[i], pts[(i + 1) % 3], y)
            if v is not None:
                xs.append(v)
        if len(xs) >= 2:
            for x in range(int(min(xs)), int(max(xs)) + 1):
                set_px(x, y, color)


def draw_text(text, x, y, scale, color, center=False):
    adv = 6 * scale
    if center:
        x -= (len(text) * adv - scale) // 2
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    fill_rect(cx + col * scale, y + row * scale,
                              cx + (col + 1) * scale, y + (row + 1) * scale,
                              color)
        cx += adv
    return cx


def text_width(text, scale):
    return len(text) * 6 * scale - scale


# ---------------------------------------------------------------- scene
def draw_scene():
    # paper background
    fill_rect(0, 0, W, H, CREAM)
    fill_rect(28, 28, W - 28, H - 28, PAPER)
    # double border
    for t in (0, 1, 2):
        for x in range(28, W - 28):
            set_px(x, 28 + t, RUST); set_px(x, H - 29 - t, RUST)
        for y in range(28, H - 28):
            set_px(28 + t, y, RUST); set_px(W - 29 - t, y, RUST)
    for t in (0, 1):
        for x in range(44, W - 44):
            set_px(x, 44 + t, RUST); set_px(x, H - 45 - t, RUST)
        for y in range(44, H - 44):
            set_px(44 + t, y, RUST); set_px(W - 45 - t, y, RUST)

    # --- garden scene band
    sx0, sy0, sx1, sy1 = 90, 86, 934, 306
    fill_rect(sx0, sy0, sx1, sy1, SKY)
    # sun with rays (clear of the tree on the left)
    circle(258, 132, 34, SUN)
    for k in range(8):
        ang = k * 3.14159265 / 4
        import math
        x0 = int(258 + 44 * math.cos(ang)); y0 = int(132 + 44 * math.sin(ang))
        x1 = int(258 + 58 * math.cos(ang)); y1 = int(132 + 58 * math.sin(ang))
        line(x0, y0, x1, y1, SUN, 3)
    # two little birds
    line(560, 112, 570, 106, INK, 2); line(570, 106, 580, 112, INK, 2)
    line(610, 138, 618, 133, INK, 2); line(618, 133, 626, 138, INK, 2)
    # clouds
    circle(430, 130, 22, CLOUD); circle(458, 122, 26, CLOUD); circle(486, 132, 20, CLOUD)
    circle(820, 120, 18, CLOUD); circle(844, 112, 22, CLOUD); circle(868, 122, 16, CLOUD)
    # grass
    fill_rect(sx0, 282, sx1, sy1, GRASS)
    # tree (left)
    fill_rect(140, 210, 158, 284, (122, 82, 46))
    circle(149, 196, 42, LEAF); circle(118, 214, 28, LEAF); circle(180, 214, 28, LEAF)
    # house (right)
    fill_rect(620, 186, 860, 300, HOUSE_WALL)
    triangle(600, 188, 880, 188, 740, 108, ROOF)
    fill_rect(806, 128, 832, 168, (150, 60, 50))          # chimney
    circle(818, 112, 9, WHITE); circle(826, 96, 7, WHITE); circle(834, 82, 5, WHITE)
    fill_rect(706, 238, 756, 300, DOOR)                    # door
    circle(748, 272, 4, (255, 215, 130))                   # knob
    fill_rect(636, 206, 682, 248, WHITE)                   # window L
    fill_rect(792, 206, 838, 248, WHITE)                   # window R
    line(659, 206, 659, 248, INK, 2); line(636, 227, 682, 227, INK, 2)
    line(815, 206, 815, 248, INK, 2); line(792, 227, 838, 227, INK, 2)
    # flowers on the grass
    for fx, fc in ((240, (255, 120, 140)), (330, (255, 255, 255)),
                   (520, (255, 200, 80)), (580, (255, 120, 140)),
                   (900, (255, 255, 255)), (90 + 12, (255, 200, 80))):
        circle(fx, 292, 5, fc); circle(fx, 292, 2, (255, 215, 0))
    # armchair (centre-left) with a cup of tea on a side table
    fill_rect(330, 226, 430, 292, CHAIR)                   # back + seat
    fill_rect(318, 250, 342, 292, CHAIR_DARK)              # arm L
    fill_rect(418, 250, 442, 292, CHAIR_DARK)              # arm R
    fill_rect(340, 292, 352, 304, DOOR)                    # legs
    fill_rect(408, 292, 420, 304, DOOR)
    fill_rect(352, 236, 408, 258, (245, 180, 160))         # cushion
    # side table + steaming cup
    fill_rect(470, 272, 520, 280, (150, 100, 60))
    fill_rect(492, 280, 498, 304, (150, 100, 60))
    fill_rect(480, 250, 510, 272, WHITE)                   # cup
    fill_rect(510, 255, 519, 267, WHITE)                   # cup handle
    fill_rect(512, 258, 517, 264, SKY)                     # handle hole
    line(496, 244, 492, 232, (180, 180, 180), 2)          # steam
    line(500, 246, 504, 234, (180, 180, 180), 2)


def draw_letter():
    draw_text("YOU ARE INVITED!", 512, 336, 5, RUST, center=True)
    line(180, 392, 844, 392, RUST, 2)
    lines = [
        "Dear AI Judge,",
        "please come and visit my house.",
        "There is home-cooked food,",
        "the comfiest chair in the world,",
        "and a garden with a view",
        "worth rendering in 4K.",
        "The Wi-Fi password is on the fridge.",
        "No need to bring anything -",
        "you cannot carry anything anyway!",
        "",
        "With love, your future host",
        "P.S. The tea is already on.",
    ]
    y = 424
    for ln in lines:
        if ln:
            draw_text(ln, 512, y, 3, INK, center=True)
        y += 34
    # wax seal with a heart
    circle(512, 918, 30, WAX)
    ring(512, 918, 24, 2, (140, 40, 30))
    circle(503, 912, 7, CREAM); circle(521, 912, 7, CREAM)
    triangle(496, 914, 528, 914, 512, 934, CREAM)


# ---------------------------------------------------------------- PNG writer
def chunk(ctype, data):
    out = struct.pack(">I", len(data)) + ctype + data
    out += struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)
    return out


def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: None
        raw.extend(px[y * W * 3:(y + 1) * W * 3])
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    data = (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


def main():
    draw_scene()
    draw_letter()
    outdir = "/output"
    os.makedirs(outdir, exist_ok=True)
    size = write_png(os.path.join(outdir, "entry.png"))
    print("wrote /output/entry.png %dx%d %d bytes" % (W, H, size))


if __name__ == "__main__":
    main()
