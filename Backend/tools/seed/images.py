"""Generated imagery for the seed dataset.

WHY GENERATE RATHER THAN SHIP BINARIES
    A seed database whose image columns point at files that do not exist is
    worse than one with no images at all: every room card, menu tile and staff
    avatar renders a broken icon, and the first thing anyone concludes is that
    uploads are broken. The previous dataset was in exactly that state -- 25
    rooms and 20 reservations carried image paths, four files existed, and the
    room paths (`/assets/rooms/placeholder-1.jpg`) pointed into the frontend
    bundle rather than at the service upload mount they are served from.

    Generating them here keeps the repository free of binary blobs, makes every
    image reproducible, and guarantees that each path written to the database
    has a real file behind it, in the right directory, under the same naming
    convention the upload endpoints use.

WHAT THESE ARE NOT
    Photographs. They are clean, legible, obviously-synthetic placeholders that
    identify what they depict -- room 204, Deluxe Room; Paneer Tikka; A.K. The
    identity documents are deliberately and visibly marked as specimens: a seed
    file must never be mistakable for a real identity document.
"""

from __future__ import annotations

import os
import uuid

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
# The property's own colours, so seeded imagery does not look foreign inside
# the app. Primary is the Cherry maroon used across the UI.
PRIMARY = (133, 1, 38)
INK = (17, 24, 39)
MUTED = (107, 114, 128)
PAPER = (250, 250, 249)

# One hue per room type, so a room grid reads as a grid of types at a glance.
ROOM_TYPE_COLOURS = {
    "Standard Room": ((94, 120, 160), (58, 79, 112)),
    "Deluxe Room": ((150, 106, 74), (104, 70, 47)),
    "Super Deluxe": ((122, 108, 156), (80, 68, 110)),
    "Executive Room": ((70, 128, 124), (42, 88, 85)),
    "Family Suite": ((176, 122, 96), (126, 82, 62)),
    "VIP Suite": ((146, 84, 104), (99, 50, 66)),
    "Presidential Suite": ((120, 96, 60), (82, 64, 36)),
    "Dormitory": ((100, 116, 130), (66, 79, 91)),
}

# Warm food tones for menu tiles; picked per item name so the same dish always
# renders the same colour.
FOOD_COLOURS = [
    ((198, 124, 78), (150, 88, 52)),
    ((176, 148, 84), (128, 105, 54)),
    ((160, 108, 96), (114, 72, 64)),
    ((134, 146, 96), (94, 104, 64)),
    ((186, 132, 108), (136, 92, 74)),
    ((150, 120, 150), (104, 82, 106)),
]

AVATAR_COLOURS = [
    (133, 1, 38), (52, 84, 132), (46, 106, 92), (128, 84, 40),
    (96, 72, 132), (150, 84, 60), (60, 96, 116), (112, 96, 44),
]


def _font(size: int, bold: bool = False):
    """A real TrueType face where the platform has one, else the bitmap default."""
    candidates = (
        ["arialbd.ttf", "seguisb.ttf", "DejaVuSans-Bold.ttf"] if bold
        else ["arial.ttf", "segoeui.ttf", "DejaVuSans.ttf"]
    )
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _centre(draw, box, text, font, fill):
    """Draw `text` centred inside `box` = (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    draw.text(
        (x0 + (x1 - x0 - (right - left)) / 2 - left,
         y0 + (y1 - y0 - (bottom - top)) / 2 - top),
        text, font=font, fill=fill,
    )


def _gradient(size, top, bottom):
    """A vertical gradient, built small and scaled up so it costs nothing."""
    w, h = size
    strip = Image.new("RGB", (1, h))
    px = strip.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return strip.resize((w, h), Image.BILINEAR)


# ---------------------------------------------------------------------------
# Room photograph
# ---------------------------------------------------------------------------

def room_image(room_no: str, room_type: str, variant: int, size=(1024, 683)) -> Image.Image:
    """A room 'photo': a stylised interior, captioned with room and type.

    Four variants per room, matching the four Room_Image columns, so a gallery
    shows four distinguishable pictures rather than the same file repeated.
    """
    w, h = size
    top, bottom = ROOM_TYPE_COLOURS.get(room_type, ((110, 110, 120), (70, 70, 80)))
    # Later variants are progressively lighter, as if shot at different times.
    lift = variant * 16
    top = tuple(min(255, c + lift) for c in top)
    bottom = tuple(min(255, c + lift) for c in bottom)

    img = _gradient(size, top, bottom)
    d = ImageDraw.Draw(img, "RGBA")

    floor_y = int(h * 0.66)
    floor = tuple(int(c * 0.62) for c in bottom)
    d.rectangle([0, floor_y, w, h], fill=floor)
    # Skirting, so wall and floor read as separate planes.
    d.rectangle([0, floor_y - 8, w, floor_y], fill=tuple(int(c * 0.82) for c in bottom))

    if variant in (0, 2):                      # bed elevation
        bw, bh = int(w * 0.50), int(h * 0.20)
        bx, by = int(w * 0.24), floor_y - int(bh * 0.30)

        # Rug under the bed.
        d.ellipse([bx - int(bw * 0.16), by + int(bh * 0.72),
                   bx + bw + int(bw * 0.16), by + int(bh * 1.42)],
                  fill=tuple(min(255, int(c * 0.78)) for c in floor))

        # Headboard.
        hb_h = int(h * 0.22)
        d.rounded_rectangle([bx + int(bw * 0.06), by - hb_h,
                             bx + int(bw * 0.94), by + 6], 12,
                            fill=tuple(int(c * 0.80) for c in bottom))
        for i in range(4):                     # tufting
            lx = bx + int(bw * (0.16 + i * 0.22))
            d.line([lx, by - hb_h + 14, lx, by - 6],
                   fill=tuple(int(c * 0.68) for c in bottom), width=3)

        # Mattress, blanket, runner.
        d.rounded_rectangle([bx, by, bx + bw, by + bh], 12, fill=(242, 240, 236))
        d.rounded_rectangle([bx, by + int(bh * 0.42), bx + bw, by + bh], 12,
                            fill=(226, 222, 214))
        d.rectangle([bx, by + int(bh * 0.60), bx + bw, by + int(bh * 0.78)],
                    fill=tuple(int(c * 0.90) for c in top))
        for i in range(2):                     # pillows
            px0 = bx + int(bw * (0.09 + i * 0.44))
            d.rounded_rectangle([px0, by - 6, px0 + int(bw * 0.36), by + int(bh * 0.34)],
                                10, fill=(253, 253, 251))
            d.rounded_rectangle([px0, by - 6, px0 + int(bw * 0.36), by + int(bh * 0.34)],
                                10, outline=(232, 230, 226), width=2)
        # Bed base in shadow.
        d.rectangle([bx + 6, by + bh, bx + bw - 6, by + bh + int(h * 0.045)],
                    fill=tuple(int(c * 0.44) for c in bottom))

        # Nightstands and lamps, one each side.
        for side in (0, 1):
            nx = bx - int(bw * 0.20) if side == 0 else bx + bw + int(bw * 0.04)
            ny = floor_y - int(h * 0.10)
            d.rectangle([nx, ny, nx + int(bw * 0.16), floor_y],
                        fill=tuple(int(c * 0.70) for c in bottom))
            lx = nx + int(bw * 0.08)
            d.line([lx, ny - int(h * 0.05), lx, ny], fill=(210, 205, 195), width=4)
            d.polygon([(lx - int(bw * 0.06), ny - int(h * 0.05)),
                       (lx + int(bw * 0.06), ny - int(h * 0.05)),
                       (lx + int(bw * 0.04), ny - int(h * 0.10)),
                       (lx - int(bw * 0.04), ny - int(h * 0.10))],
                      fill=(248, 236, 208))

        # Framed art above the headboard.
        aw = int(bw * 0.30)
        ax = bx + int(bw * 0.35)
        ay = by - hb_h - int(h * 0.16)
        d.rectangle([ax, ay, ax + aw, ay + int(h * 0.13)], fill=(236, 232, 224),
                    outline=(70, 62, 54), width=4)
    else:                                      # window elevation
        ww, wh = int(w * 0.40), int(h * 0.34)
        wx, wy = int(w * 0.30), int(h * 0.16)
        d.rectangle([wx - 10, wy - 10, wx + ww + 10, wy + wh + 10], fill=(245, 245, 243))
        d.rectangle([wx, wy, wx + ww, wy + wh], fill=(206, 224, 238))
        # Sky to ground, seen through the glass.
        d.rectangle([wx, wy + int(wh * 0.62), wx + ww, wy + wh], fill=(150, 178, 150))
        d.ellipse([wx + int(ww * 0.62), wy + int(wh * 0.12),
                   wx + int(ww * 0.86), wy + int(wh * 0.36)], fill=(252, 244, 214))
        d.line([wx + ww // 2, wy, wx + ww // 2, wy + wh], fill=(250, 250, 248), width=6)
        d.line([wx, wy + wh // 2, wx + ww, wy + wh // 2], fill=(250, 250, 248), width=6)
        # Curtains.
        for side in (0, 1):
            cx0 = wx - 10 if side == 0 else wx + ww - int(ww * 0.14) + 10
            d.rectangle([cx0, wy - 10, cx0 + int(ww * 0.14), wy + wh + 10],
                        fill=tuple(int(c * 0.86) for c in top))
        # An armchair and a side table on the floor.
        chx, chy = int(w * 0.16), floor_y - int(h * 0.14)
        d.rounded_rectangle([chx, chy, chx + int(w * 0.16), floor_y], 12,
                            fill=tuple(int(c * 0.74) for c in bottom))
        d.rounded_rectangle([chx, chy - int(h * 0.06), chx + int(w * 0.16), chy + 12], 12,
                            fill=tuple(int(c * 0.84) for c in bottom))
        tx = chx + int(w * 0.20)
        d.ellipse([tx, chy + int(h * 0.02), tx + int(w * 0.10), chy + int(h * 0.06)],
                  fill=tuple(int(c * 0.66) for c in bottom))

    # Lamp glow, for a little depth.
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse(
        [int(w * 0.62), int(h * 0.10), int(w * 0.92), int(h * 0.44)],
        fill=(255, 236, 190, 70))
    img = Image.alpha_composite(img.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(38)))
    img = img.convert("RGB")
    d = ImageDraw.Draw(img, "RGBA")

    # Caption bar.
    d.rectangle([0, h - 92, w, h], fill=(0, 0, 0, 150))
    d.text((28, h - 76), f"Room {room_no}", font=_font(40, bold=True), fill=(255, 255, 255))
    d.text((28, h - 32), room_type, font=_font(22), fill=(226, 226, 226))
    tag = f"View {variant + 1} of 4"
    tb = d.textbbox((0, 0), tag, font=_font(18))
    d.text((w - 28 - (tb[2] - tb[0]), h - 30), tag, font=_font(18), fill=(200, 200, 200))
    return img


# ---------------------------------------------------------------------------
# Menu item
# ---------------------------------------------------------------------------

def menu_image(name: str, category: str, veg: bool = True, size=(800, 600)) -> Image.Image:
    """A plated-dish tile for a restaurant or bar menu item."""
    w, h = size
    top, bottom = FOOD_COLOURS[sum(map(ord, name)) % len(FOOD_COLOURS)]
    img = _gradient(size, tuple(min(255, c + 40) for c in top), bottom)
    d = ImageDraw.Draw(img, "RGBA")

    cx, cy, r = w // 2, int(h * 0.44), int(min(w, h) * 0.30)
    d.ellipse([cx - r - 14, cy - r - 14, cx + r + 14, cy + r + 14], fill=(255, 255, 255, 40))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(248, 247, 244))
    d.ellipse([cx - int(r * 0.74), cy - int(r * 0.74), cx + int(r * 0.74), cy + int(r * 0.74)],
              fill=(238, 235, 229))

    # Food on the plate, arranged deterministically from the name.
    seed = sum(map(ord, name))
    inner = int(r * 0.60)
    for i in range(5):
        a = (seed + i * 67) % 360
        import math
        dist = inner * (0.20 + ((seed >> i) % 5) / 10.0)
        px = cx + int(dist * math.cos(math.radians(a)))
        py = cy + int(dist * math.sin(math.radians(a)))
        blob = int(inner * (0.30 + ((seed >> (i + 2)) % 4) / 12.0))
        d.ellipse([px - blob, py - blob, px + blob, py + blob],
                  fill=tuple(max(0, c - 18 * i % 60) for c in top))

    # Veg / non-veg mark, as Indian menus require.
    mark = 26
    mx, my = 24, 24
    colour = (22, 128, 62) if veg else (150, 24, 24)
    d.rectangle([mx, my, mx + mark, my + mark], outline=colour, width=3)
    d.ellipse([mx + 7, my + 7, mx + mark - 7, my + mark - 7], fill=colour)

    d.rectangle([0, h - 104, w, h], fill=(0, 0, 0, 150))
    label = name if len(name) <= 26 else name[:25] + "…"
    d.text((26, h - 88), label, font=_font(34, bold=True), fill=(255, 255, 255))
    d.text((26, h - 42), category, font=_font(20), fill=(224, 224, 224))
    return img


# ---------------------------------------------------------------------------
# Staff avatar
# ---------------------------------------------------------------------------

def avatar_image(first: str, last: str, size=(512, 512)) -> Image.Image:
    """Initials on a solid ground -- the same convention the UI falls back to."""
    w, h = size
    initials = (first[:1] + last[:1]).upper() or "?"
    colour = AVATAR_COLOURS[(sum(map(ord, first + last))) % len(AVATAR_COLOURS)]
    img = Image.new("RGB", size, colour)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([-w * 0.25, h * 0.45, w * 1.25, h * 1.9], fill=(255, 255, 255, 26))
    _centre(d, (0, 0, w, int(h * 0.92)), initials, _font(int(h * 0.42), bold=True),
            (255, 255, 255))
    return img


# ---------------------------------------------------------------------------
# Identity document
# ---------------------------------------------------------------------------

def identity_document(guest_name: str, doc_type: str, ref: str,
                      size=(1000, 640)) -> Image.Image:
    """A SPECIMEN identity document for a reservation's proof upload.

    Marked as a specimen in three places, and carries no number that could be
    mistaken for a real one. A seeded file must never be usable as, or mistaken
    for, a genuine identity document -- so this looks like a form, says what it
    is, and stays obviously synthetic.
    """
    w, h = size
    img = Image.new("RGB", size, PAPER)
    d = ImageDraw.Draw(img, "RGBA")

    d.rectangle([0, 0, w, 96], fill=PRIMARY)
    d.text((32, 26), doc_type.upper(), font=_font(34, bold=True), fill=(255, 255, 255))
    d.text((32, 66), "SPECIMEN — SEED DATA, NOT A REAL DOCUMENT",
           font=_font(17), fill=(255, 214, 224))

    d.rounded_rectangle([32, 132, 236, 372], 10, fill=(232, 232, 230),
                        outline=(200, 200, 198), width=2)
    _centre(d, (32, 132, 236, 372), "PHOTO", _font(26, bold=True), MUTED)

    fields = [
        ("Name", guest_name),
        ("Document", doc_type),
        ("Reference", ref),
        ("Issued", "—  specimen  —"),
        ("Status", "Sample record for demonstration"),
    ]
    y = 140
    for label, value in fields:
        d.text((268, y), label.upper(), font=_font(15, bold=True), fill=MUTED)
        d.text((268, y + 22), str(value), font=_font(25), fill=INK)
        y += 62

    d.line([32, h - 96, w - 32, h - 96], fill=(214, 214, 212), width=2)
    d.text((32, h - 76),
           "Generated by the HotelERP seed dataset. Contains no personal data.",
           font=_font(17), fill=MUTED)

    # Diagonal watermark, so it reads as a specimen even in a thumbnail.
    mark = Image.new("RGBA", size, (0, 0, 0, 0))
    md = ImageDraw.Draw(mark)
    md.text((int(w * 0.10), int(h * 0.40)), "SPECIMEN",
            font=_font(140, bold=True), fill=(133, 1, 38, 34))
    img = Image.alpha_composite(img.convert("RGBA"), mark).convert("RGB")
    return img


def incident_photo(room_no: str, summary: str, size=(900, 675)) -> Image.Image:
    """An attachment for a housekeeping room-incident log entry."""
    w, h = size
    img = _gradient(size, (120, 124, 130), (74, 78, 84))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, int(h * 0.66), w, h], fill=(92, 88, 84))
    d.polygon([(int(w * 0.30), int(h * 0.66)), (int(w * 0.52), int(h * 0.40)),
               (int(w * 0.72), int(h * 0.66))], fill=(150, 146, 140))
    d.rectangle([0, 0, w, 74], fill=(0, 0, 0, 150))
    d.text((24, 18), f"Room {room_no} — incident", font=_font(30, bold=True),
           fill=(255, 255, 255))
    d.rectangle([0, h - 62, w, h], fill=(0, 0, 0, 150))
    d.text((24, h - 46), (summary[:60] + "…") if len(summary) > 60 else summary,
           font=_font(20), fill=(230, 230, 230))
    return img


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------

def save(img: Image.Image, directory: str, filename: str, quality: int = 82) -> str:
    """Write `img` into `directory` as `filename`; return the filename."""
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    if filename.lower().endswith((".jpg", ".jpeg")):
        img.save(path, "JPEG", quality=quality, optimize=True)
    else:
        img.save(path, "PNG", optimize=True)
    return filename


def hex_name(ext: str = "jpg") -> str:
    """`{uuid4().hex}.ext` — what MasterData, Restaurant and Bar uploads produce."""
    return f"{uuid.uuid4().hex}.{ext}"


def user_name(ext: str = "png") -> str:
    """`user_{uuid4().hex}.ext` — what the UserServices upload produces."""
    return f"user_{uuid.uuid4().hex}.{ext}"


def dashed_name(ext: str = "jpg") -> str:
    """`{uuid4()}.ext` — what the reservation identity-proof upload produces."""
    return f"{uuid.uuid4()}.{ext}"
