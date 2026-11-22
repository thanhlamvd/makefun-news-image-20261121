#!/usr/bin/env python3
"""Draw the 21 November 2026 front page as a 1024x1024 PNG.

Pure Python 3 standard library: an RGB framebuffer, a hand-drawn
5x7 bitmap font and a small PNG writer built on zlib. No network,
no clock, no randomness, so every run writes identical bytes.

    python3 generate_image.py [output.png]

With no argument the image goes to entry.png next to this file.
This is a build-time tool only; the entry itself is main.py, which
copies the committed entry.png into the output directory.
"""

import binascii
import os
import struct
import sys
import zlib

PAGE_W = 1024
PAGE_H = 1024

# 5x7 bitmap font. Every glyph is seven rows of five cells; '#'
# is ink and '.' is paper. All front-page text is set in capitals,
# so only capitals, digits and a few marks are needed.
FONT = {
    "A": (" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "B": ("#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "),
    "C": (" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"),
    "D": ("#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "),
    "E": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    "F": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    "G": (" ####", "#    ", "#    ", "#  ##", "#   #", "#   #", " ### "),
    "H": ("#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "I": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"),
    "J": ("  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "),
    "K": ("#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"),
    "L": ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    "M": ("#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"),
    "N": ("#   #", "##  #", "# # #", "#  ##", "#   #", "#   #", "#   #"),
    "O": (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "P": ("#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "),
    "Q": (" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"),
    "R": ("#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"),
    "S": (" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "),
    "T": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "U": ("#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "V": ("#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "W": ("#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"),
    "X": ("#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"),
    "Y": ("#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "Z": ("#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"),
    "0": (" ### ", "#   #", "#  ##", "# # #", "##  #", "#   #", " ### "),
    "1": ("  #  ", " ##  ", "# #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "2": (" ### ", "#   #", "    #", "  ## ", " #   ", "#    ", "#####"),
    "3": ("#### ", "    #", "    #", " ### ", "    #", "    #", "#### "),
    "4": ("   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "),
    "5": ("#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "),
    "6": (" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "),
    "7": ("#####", "    #", "   # ", "  #  ", "  #  ", " #   ", " #   "),
    "8": (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    "9": (" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "),
    " ": ("     ", "     ", "     ", "     ", "     ", "     ", "     "),
    ",": ("     ", "     ", "     ", "     ", "  ## ", "  ## ", " #   "),
    ".": ("     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "),
    ":": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "),
    ";": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", " #   "),
    "'": ("  #  ", "  #  ", " #   ", "     ", "     ", "     ", "     "),
    "-": ("     ", "     ", "     ", " ### ", "     ", "     ", "     "),
    "/": ("    #", "   # ", "   # ", "  #  ", " #   ", " #   ", "#    "),
    "&": (" ##  ", "#  # ", "#  # ", " #   ", "# # #", "#  # ", " ## #"),
    "(": ("   # ", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   # "),
    ")": (" #   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", "   # "),
    "%": ("##  #", "## # ", "   # ", "  #  ", " #   ", "# # #", "#  ##"),
    "$": ("  #  ", " ####", "# #  ", " ### ", "  # #", "#### ", "  #  "),
    "?": (" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "),
    "!": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "),
    "+": ("     ", "  #  ", "  #  ", "#####", "  #  ", "  #  ", "     "),
}


def new_canvas(width, height, colour):
    return bytearray(bytes(colour) * (width * height))


def rect(buf, x, y, w, h, colour):
    """Fill an axis-aligned rectangle, clipped to the page."""
    r, g, b = colour
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(PAGE_W, x + w)
    y1 = min(PAGE_H, y + h)
    for yy in range(y0, y1):
        base = (yy * PAGE_W + x0) * 3
        for xx in range(x0, x1):
            o = base + (xx - x0) * 3
            buf[o] = r
            buf[o + 1] = g
            buf[o + 2] = b


def outline(buf, x, y, w, h, colour, thick=2):
    rect(buf, x, y, w, thick, colour)
    rect(buf, x, y + h - thick, w, thick, colour)
    rect(buf, x, y, thick, h, colour)
    rect(buf, x + w - thick, y, thick, h, colour)


def blit_glyph(buf, x, y, ch, colour, scale):
    shape = FONT.get(ch, FONT["?"])
    for row in range(7):
        for col in range(5):
            if shape[row][col] == "#":
                rect(buf, x + col * scale, y + row * scale,
                     scale, scale, colour)


def measure(text, scale):
    return len(text) * 6 * scale


def draw_text(buf, x, y, text, colour, scale):
    cx = x
    for ch in text:
        blit_glyph(buf, cx, y, ch, colour, scale)
        cx += 6 * scale


def draw_centred(buf, y, text, colour, scale):
    draw_text(buf, (PAGE_W - measure(text, scale)) // 2, y,
              text, colour, scale)


def shrink_to_fit(text, max_w, start):
    """Largest scale at or below `start` that fits `text` in `max_w`."""
    scale = start
    while scale > 1 and measure(text, scale) > max_w:
        scale -= 1
    return scale


def wrap(text, limit):
    lines = []
    current = ""
    for word in text.split(" "):
        trial = word if not current else current + " " + word
        if len(trial) <= limit:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_block(buf, x, y, text, colour, scale, limit, line_h):
    """Draw wrapped text; return the y just past the last line."""
    lines = wrap(text, limit)
    for i, line in enumerate(lines):
        draw_text(buf, x, y + i * line_h, line, colour, scale)
    return y + len(lines) * line_h


def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    return out + struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)


def write_png(path, width, height, buf):
    raw = b"".join(
        b"\x00" + bytes(buf[y * width * 3:(y + 1) * width * 3])
        for y in range(height)
    )
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


PAPER = (250, 247, 240)
CARD = (255, 255, 255)
INK = (22, 22, 30)
NAVY = (15, 23, 42)
GOLD = (198, 160, 38)
GREY = (98, 114, 138)
LINE = (201, 211, 224)
WHITE = (255, 255, 255)

# Six stories, each verified against reporting dated 21 November 2026.
LEAD = {
    "kicker": "MEXICO",
    "accent": (37, 99, 235),
    "headline": "EL CHAPO ISIDRO CAPTURED IN SINALOA RAID",
    "body": "MEXICAN SPECIAL FORCES SEIZE FAUSTO ISIDRO MEZA FLORES, "
            "AN FBI TOP TEN FUGITIVE, IN GUASAVE. FOUR SOLDIERS AND "
            "SEVEN GUNMEN KILLED IN THE RAID, RUN WITH U.S. "
            "INTELLIGENCE.",
    "source": "REUTERS - AP - WSJ",
}

STORIES = [
    {
        "kicker": "WAR IN UKRAINE",
        "accent": (217, 119, 6),
        "headline": "STRIKE HITS ZELENSKYY'S HOMETOWN",
        "body": "A RUSSIAN MISSILE ATTACK ON KRYVYI RIH KILLS TWO, "
                "A BOY OF SEVEN AND A WOMAN OF 20, AND WOUNDS 60, "
                "INCLUDING SIX CHILDREN. RESCUERS ARE HIT BY "
                "FOLLOW-UP ROCKETS.",
        "source": "AP - AL JAZEERA",
    },
    {
        "kicker": "BALTIC SEA",
        "accent": (5, 150, 105),
        "headline": "DRONES SET SANCTIONED RUSSIAN SHIP ABLAZE",
        "body": "THE SPARTA II, BOUND FOR KALININGRAD, IS HIT BY "
                "TWO DRONES IN THE GULF OF FINLAND AND DRIFTS INTO "
                "FINNISH WATERS. ITS 16 CREW ARE EVACUATED. "
                "FINLAND SAYS UKRAINE IS LIKELY BEHIND IT.",
        "source": "REUTERS - AL JAZEERA - CNN",
    },
    {
        "kicker": "MIDDLE EAST",
        "accent": (220, 38, 38),
        "headline": "TWO TANKERS HIT NEAR STRAIT OF HORMUZ",
        "body": "UKMTO SAYS TWO TANKERS ARE STRUCK BY UNIDENTIFIED "
                "PROJECTILES OFF OMAN. IRAN SAYS ANOTHER TANKER "
                "CAUGHT FIRE AFTER HITTING A NAVAL MINE. NO "
                "CASUALTIES REPORTED.",
        "source": "REUTERS - AL JAZEERA",
    },
    {
        "kicker": "CLIMATE",
        "accent": (13, 148, 136),
        "headline": "COP31 TALKS RUN PAST DEADLINE",
        "body": "NEGOTIATORS IN ANTALYA WORK THROUGH SATURDAY "
                "AFTER MISSING THE FRIDAY DEADLINE. THE DRAFT "
                "STILL OMITS FOSSIL FUELS AND A $120BN ADAPTATION "
                "TARGET. A THIRD DRAFT IS DUE.",
        "source": "AFP - AL JAZEERA - REUTERS",
    },
    {
        "kicker": "SCIENCE",
        "accent": (124, 58, 237),
        "headline": "MOSQUITOES CUT DENGUE BY 69 PERCENT",
        "body": "A FOUR-YEAR TRIAL IN BELO HORIZONTE, BRAZIL, "
                "FINDS WOLBACHIA MOSQUITOES CUT DENGUE AND "
                "CHIKUNGUNYA INFECTIONS BY ABOUT 69 PERCENT IN "
                "MORE THAN 5,700 CHILDREN.",
        "source": "AP - STRAITS TIMES",
    },
]

# The day in numbers: one verified figure per panel entry.
NUMBERS = [
    ("11", "KILLED IN THE SINALOA RAID"),
    ("2 + 60", "KILLED AND WOUNDED IN KRYVYI RIH"),
    ("16", "CREW EVACUATED FROM THE SPARTA II"),
    ("69%", "FEWER DENGUE INFECTIONS IN BRAZIL"),
]


def draw_card(buf, x, y, card_w, card_h, story, index):
    rect(buf, x, y, card_w, card_h, CARD)
    outline(buf, x, y, card_w, card_h, LINE, 2)
    rect(buf, x, y, card_w, 9, story["accent"])
    draw_text(buf, x + 16, y + 26, story["kicker"],
              story["accent"], 1)
    draw_text(buf, x + 16 + measure(story["kicker"], 1) + 12,
              y + 26, str(index), GREY, 1)
    after = draw_block(buf, x + 16, y + 54, story["headline"],
                       INK, 2, (card_w - 32) // 12, 30)
    rect(buf, x + 16, after + 10, card_w - 32, 2, LINE)
    draw_block(buf, x + 16, after + 26, story["body"],
               INK, 1, (card_w - 32) // 6, 15)
    draw_text(buf, x + 16, y + card_h - 28, story["source"],
              GREY, 1)


def draw_lead(buf, x, y, lead_w, lead_h):
    rect(buf, x, y, lead_w, lead_h, CARD)
    outline(buf, x, y, lead_w, lead_h, LINE, 2)
    rect(buf, x, y, 9, lead_h, LEAD["accent"])
    draw_text(buf, x + 28, y + 22, LEAD["kicker"],
              LEAD["accent"], 1)
    draw_text(buf, x + 28 + measure(LEAD["kicker"], 1) + 12,
              y + 22, "1", GREY, 1)
    head_scale = shrink_to_fit(LEAD["headline"], lead_w - 56, 3)
    draw_text(buf, x + 28, y + 50, LEAD["headline"], INK, head_scale)
    after = draw_block(buf, x + 28, y + 92, LEAD["body"],
                       INK, 2, (lead_w - 56) // 12, 26)
    draw_text(buf, x + 28, y + lead_h - 26, LEAD["source"],
              GREY, 1)
    return after


def draw_numbers(buf, x, y, panel_w, panel_h):
    rect(buf, x, y, panel_w, panel_h, NAVY)
    draw_text(buf, x + 16, y + 22, "THE DAY IN NUMBERS", GOLD, 1)
    rect(buf, x + 16, y + 44, panel_w - 32, 2, GOLD)
    cy = y + 66
    for big, label in NUMBERS:
        draw_text(buf, x + 16, cy, big, WHITE, 2)
        draw_text(buf, x + 16, cy + 26, label, (203, 213, 225), 1)
        cy += 56
    return cy


def compose():
    buf = new_canvas(PAGE_W, PAGE_H, PAPER)
    # Masthead: navy band, title, date, gold rule.
    rect(buf, 0, 0, PAGE_W, 138, NAVY)
    draw_centred(buf, 22, "THE WORLD IN ONE DAY", WHITE, 4)
    date = "SATURDAY, 21 NOVEMBER 2026"
    date_scale = shrink_to_fit(date, PAGE_W - 80, 3)
    draw_centred(buf, 88, date, GOLD, date_scale)
    rect(buf, 0, 138, PAGE_W, 4, GOLD)

    margin = 24
    gap = 16
    # Lead story, full width.
    lead_w = PAGE_W - 2 * margin
    draw_lead(buf, margin, 154, lead_w, 196)

    # Three cards in a row, then two cards plus the numbers panel.
    cols = 3
    card_w = (PAGE_W - 2 * margin - (cols - 1) * gap) // cols
    card_h = 290
    row1_y = 366
    for i in range(3):
        x = margin + i * (card_w + gap)
        draw_card(buf, x, row1_y, card_w, card_h, STORIES[i], i + 2)
    row2_y = 672
    for i in range(3, 5):
        x = margin + (i - 3) * (card_w + gap)
        draw_card(buf, x, row2_y, card_w, card_h, STORIES[i], i + 2)
    nx = margin + 2 * (card_w + gap)
    draw_numbers(buf, nx, row2_y, card_w, card_h)

    draw_centred(buf, 980,
                 "SOURCES: REUTERS - AP - WSJ - AL JAZEERA - AFP - "
                 "CNN - STRAITS TIMES",
                 GREY, 1)
    return buf


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "entry.png")
    buf = compose()
    write_png(out, PAGE_W, PAGE_H, buf)
    print("wrote %s (%dx%d)" % (out, PAGE_W, PAGE_H))


if __name__ == "__main__":
    main()
