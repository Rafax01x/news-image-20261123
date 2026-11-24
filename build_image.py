#!/usr/bin/env python3
"""Build entry.png for make.fun news-image-20261123.

One image summing up the world's news of Monday 23 November 2026:
a dotted world map drawn from Natural Earth land polygons, with a pin
at every story's real location, a lead story on top and six stories
in a grid below. 1024x1024, deterministic, no network at render time
(the GeoJSON is read from disk; the map is rasterised by this script).

Stories (all verified 23-24 Nov 2026 from named sources):
  lead  COP31 collapses, Antalya, Turkey (Reuters, CNN, Le Monde)
  1     Ukraine sinks Russian corvette off Libya, Benghazi (CNN, WSJ)
  2     Russian strike kills 11 in Dymer, Ukraine (Reuters)
  3     Factory fire kills 24 in Cikande, Indonesia (Reuters)
  4     Nvidia brings back Jensen Huang, Santa Clara (Reuters, Le Monde)
  5     US sanctions Iran's shadow banks, Washington (US Treasury)
  6     India gives Nepal $1.62bn to rebuild, New Delhi (BusinessWorld)
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
GEOJSON = os.path.join(HERE, "ne_50m_land.geojson")
OUT = os.path.join(HERE, "entry.png")

W = H = 1024
BG = (12, 20, 36)          # deep navy
INK = (236, 241, 240)      # near-white
MUTED = (168, 182, 204)    # grey-blue deck text
RED = (229, 72, 77)        # kickers, pins
GOLD = (217, 164, 65)      # lead pin, date/source lines
DOT = (116, 139, 173)      # map dots
RULE = (34, 48, 74)        # hairlines
PIN_RING = (255, 255, 255)

FONT_SERIF_BLACK = "/usr/share/fonts/truetype/noto/NotoSerifDisplay-Black.ttf"
FONT_SERIF_BOLD = "/usr/share/fonts/truetype/noto/NotoSerifDisplay-Bold.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def tracked(draw, xy, text, fnt, fill, tracking=2):
    """Draw text with extra letter-spacing (editorial kicker look)."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x


def text_w(draw, text, fnt, tracking=0):
    w = draw.textlength(text, font=fnt)
    if tracking:
        w += tracking * max(len(text) - 1, 0)
    return w


# ---------------------------------------------------------------- stories
# lon/lat are the real locations; label_dx/dy shift the map label so
# labels never collide; anchor "l" puts the label right of the pin,
# "r" puts it left of the pin.
STORIES = [
    dict(key="benghazi", city="BENGHAZI", lon=20.07, lat=32.12,
         pin=RED, label_dx=-12, label_dy=2, anchor="r",
         headline=["Ukraine sinks Russian", "warship off Libya"],
         deck=["Seven naval drones sink the Merkury at anchor in Benghazi;",
               "the cargo ship Angara is hit too."],
         date="23 NOVEMBER 2026", source="CNN"),
    dict(key="dymer", city="DYMER", lon=30.30, lat=50.78,
         pin=RED, label_dx=12, label_dy=-8, anchor="l",
         headline=["Russian strike kills 11", "in Dymer, north of Kyiv"],
         deck=["A five-storey block collapses; a boy of seven is pulled alive",
               "from the rubble after 14 hours."],
         date="23 NOVEMBER 2026", source="REUTERS"),
    dict(key="cikande", city="CIKANDE", lon=106.33, lat=-6.20,
         pin=RED, label_dx=-12, label_dy=-8, anchor="r",
         headline=["Factory fire kills 24", "in Indonesia"],
         deck=["A candy factory burns in Banten; about 30 workers are still",
               "missing as rescuers search on."],
         date="23 NOVEMBER 2026", source="REUTERS"),
    dict(key="santa-clara", city="SANTA CLARA", lon=-121.95, lat=37.35,
         pin=RED, label_dx=-12, label_dy=-8, anchor="r",
         headline=["Nvidia brings back", "Jensen Huang"],
         deck=["The board reinstates its co-founder as chief executive after",
               "pressure from Trump; shares jump 30%."],
         date="23 NOVEMBER 2026", source="REUTERS"),
    dict(key="washington", city="WASHINGTON", lon=-77.04, lat=38.90,
         pin=RED, label_dx=12, label_dy=-8, anchor="l",
         headline=["US hits Iran's shadow", "banking network"],
         deck=["The Treasury sanctions dozens of exchange houses and front",
               "firms, the regime's \u201clast financial lifeline\u201d."],
         date="23 NOVEMBER 2026", source="U.S. TREASURY"),
    dict(key="new-delhi", city="NEW DELHI", lon=77.21, lat=28.61,
         pin=RED, label_dx=12, label_dy=-8, anchor="l",
         headline=["India gives Nepal $1.62bn", "to rebuild after floods"],
         deck=["A 240-billion-rupee package will rebuild after August's",
               "floods, as Nepal's prime minister visits Delhi."],
         date="23 NOVEMBER 2026", source="BUSINESSWORLD"),
]

LEAD = dict(
    city="ANTALYA, TURKEY", lon=30.71, lat=36.90, pin=GOLD,
    label_dx=12, label_dy=-8, anchor="l", label="ANTALYA",
    headline=["COP31 ends with no deal", "as the climate talks collapse"],
    deck=["The EU and about 130 countries reject a draft silent on fossil fuels, ending the",
         "longest climate summit on record \u2014 the first big breakdown since Copenhagen in 2009."],
    date="23 NOVEMBER 2026", source="REUTERS",
)

# Map box and projection: equirectangular, uniform scale, lat 80..-55
# (Antarctica is cut, as on the v3 map).
MAP = dict(x0=48, x1=976, y0=325, y1=595, lat_top=80.0, lat_bot=-55.0)


def project(lon, lat):
    mw = MAP["x1"] - MAP["x0"]
    mh = MAP["y1"] - MAP["y0"]
    scale = min(mw / 360.0, mh / (MAP["lat_top"] - MAP["lat_bot"]))
    w = 360.0 * scale
    h = (MAP["lat_top"] - MAP["lat_bot"]) * scale
    ox = MAP["x0"] + (mw - w) / 2.0
    oy = MAP["y0"] + (mh - h) / 2.0
    x = ox + (lon + 180.0) * scale
    y = oy + (MAP["lat_top"] - lat) * scale
    return x, y, scale


def load_land_mask():
    """Rasterise Natural Earth land polygons into a boolean mask
    over the map box (1 = land)."""
    mw = MAP["x1"] - MAP["x0"]
    mh = MAP["y1"] - MAP["y0"]
    mask = Image.new("L", (mw, mh), 0)
    md = ImageDraw.Draw(mask)
    with open(GEOJSON, encoding="utf-8") as f:
        data = json.load(f)
    for feat in data["features"]:
        geom = feat["geometry"]
        polys = []
        if geom["type"] == "Polygon":
            polys = [geom["coordinates"]]
        elif geom["type"] == "MultiPolygon":
            polys = geom["coordinates"]
        for poly in polys:
            for ring in poly:
                pts = []
                for lon, lat in ring:
                    x, y, _ = project(lon, lat)
                    pts.append((x - MAP["x0"], y - MAP["y0"]))
                if len(pts) >= 3:
                    md.polygon(pts, fill=255)
    return mask


def draw_map(draw, mask):
    """Dot-matrix world map: a dot wherever the mask says land."""
    spacing = 5
    r = 1.7
    mw = MAP["x1"] - MAP["x0"]
    mh = MAP["y1"] - MAP["y0"]
    px = mask.load()
    y = spacing // 2
    while y < mh:
        x = spacing // 2
        while x < mw:
            if px[x, y]:
                draw.ellipse([MAP["x0"] + x - r, MAP["y0"] + y - r,
                              MAP["x0"] + x + r, MAP["y0"] + y + r],
                             fill=DOT)
            x += spacing
        y += spacing


def draw_pin(draw, x, y, colour, big=False):
    r = 11 if big else 9
    draw.ellipse([x - r - 2.5, y - r - 2.5, x + r + 2.5, y + r + 2.5],
                 outline=PIN_RING, width=2)
    draw.ellipse([x - r, y - r, x + r, y + r], fill=colour)
    draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=PIN_RING)


def draw_label(draw, x, y, text, dx, dy, anchor):
    fnt = font(FONT_SANS_BOLD, 15)
    lx = x + dx if anchor == "l" else x + dx - text_w(draw, text, fnt)
    ly = y + dy
    draw.text((lx, ly), text, font=fnt, fill=INK,
              stroke_width=3, stroke_fill=BG)


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # ---- header
    tracked(draw, (48, 32), "MONDAY \u00b7 THE WORLD IN ONE PAGE \u00b7 7 STORIES",
            font(FONT_SANS_BOLD, 19), RED, tracking=2)
    draw.text((48, 54), "23 NOVEMBER 2026", font=font(FONT_SERIF_BLACK, 56),
              fill=INK)
    draw.line([(48, 124), (976, 124)], fill=RED, width=2)

    # ---- lead story
    tracked(draw, (48, 136), "THE BIG STORY \u00b7 " + LEAD["city"],
            font(FONT_SANS_BOLD, 18), RED, tracking=2)
    y = 156
    for line in LEAD["headline"]:
        draw.text((48, y), line, font=font(FONT_SERIF_BLACK, 46), fill=INK)
        y += 50
    y += 4
    for line in LEAD["deck"]:
        draw.text((48, y), line, font=font(FONT_SANS, 15), fill=MUTED)
        y += 19
    y += 4
    tracked(draw, (48, y), LEAD["date"] + " \u00b7 " + LEAD["source"],
            font(FONT_SANS_BOLD, 13), GOLD, tracking=1)

    # ---- map
    mask = load_land_mask()
    draw_map(draw, mask)
    lx, ly, _ = project(LEAD["lon"], LEAD["lat"])
    draw_pin(draw, lx, ly, LEAD["pin"], big=True)
    draw_label(draw, lx, ly, LEAD["label"], LEAD["label_dx"],
               LEAD["label_dy"], LEAD["anchor"])
    for s in STORIES:
        px, py, _ = project(s["lon"], s["lat"])
        draw_pin(draw, px, py, s["pin"])
        draw_label(draw, px, py, s["city"], s["label_dx"], s["label_dy"],
                   s["anchor"])
    # legend, bottom-right of the map box
    leg_y = MAP["y1"] - 18
    f_leg = font(FONT_SANS_BOLD, 13)
    draw.ellipse([MAP["x1"] - 218, leg_y + 2, MAP["x1"] - 208, leg_y + 12],
                 fill=GOLD)
    draw.text((MAP["x1"] - 202, leg_y), "LEAD STORY", font=f_leg, fill=MUTED)
    draw.ellipse([MAP["x1"] - 108, leg_y + 2, MAP["x1"] - 98, leg_y + 12],
                 fill=RED)
    draw.text((MAP["x1"] - 92, leg_y), "STORY", font=f_leg, fill=MUTED)

    # ---- divider + story grid (2 cols x 3 rows)
    draw.line([(48, 608), (976, 608)], fill=RULE, width=1)
    col_w = 448
    col_x = [48, 528]
    row_y = [620, 745, 870]
    for i, s in enumerate(STORIES):
        cx = col_x[i % 2]
        cy = row_y[i // 2]
        tracked(draw, (cx, cy), s["city"], font(FONT_SANS_BOLD, 15), RED,
                tracking=1)
        hy = cy + 20
        for line in s["headline"]:
            draw.text((cx, hy), line, font=font(FONT_SERIF_BOLD, 21),
                      fill=INK)
            hy += 24
        dy = hy + 2
        for line in s["deck"]:
            draw.text((cx, dy), line, font=font(FONT_SANS, 13.5), fill=MUTED)
            dy += 16.5
        tracked(draw, (cx, dy + 3),
                s["date"] + " \u00b7 " + s["source"],
                font(FONT_SANS_BOLD, 11.5), GOLD, tracking=1)
        if i % 2 == 0:
            draw.line([(504, cy + 2), (504, cy + 106)], fill=RULE, width=1)

    # ---- footer
    draw.line([(48, 992), (976, 992)], fill=RULE, width=1)
    foot = "Sources: Reuters \u00b7 CNN \u00b7 Le Monde \u00b7 The Wall Street Journal \u00b7 U.S. Treasury \u00b7 BusinessWorld"
    fw = text_w(draw, foot, font(FONT_SANS, 14))
    draw.text(((W - fw) / 2, 1000), foot, font=font(FONT_SANS, 14),
              fill=MUTED)

    img.save(OUT, format="PNG", optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
