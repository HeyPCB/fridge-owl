"""Writes boards/merch_fridge_owl/board.json: Hoot, the fridge reminder owl (heypcb.ai merch 08).

    "$KICAD_PYTHON" boards/merch_fridge_owl/make_brief.py

A yellow owl magnet for the fridge door. Its left wing is "meds", its right wing "water". After you
press a wing, that eye stays quiet; when the reminder comes due (24 h for meds, 2 h for water) the eye
starts blinking at you until you press again. A quiet owl means you already did it. ATtiny412 on a
CR2032; two magnets glued to the flat back. Edit this file, not board.json. Frame 50 x 62 mm.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import merch_kit as K  # noqa: E402

SLUG = "fridge-owl"
W, H = 50.0, 62.0
CX = 25.0
BODY_C, BODY_RX, BODY_RY = (CX, 33.0), 21.0, 24.0
EYE_Y, EYE_DX = 22.5, 8.4

BLOCKS = [
    {"block": "merch_cr2032", "as": "bat", "title": "CR2032 in the belly"},
    {"block": "merch_mcu_attiny412", "as": "mcu", "title": "ATtiny412: two timers, asleep in between",
     "nets": {"VDD": "VBAT"},
     "pinNets": {"U?.4": "EYE_L", "U?.7": "EYE_R", "U?.2": "MEDS", "U?.5": "WATER"},
     "no_connect": ["U?.3"]},
    {"block": "gpio_led", "as": "eye_l", "title": "Left eye (orange): meds due", "nets": {"SIG": "EYE_L"},
     "values": {"D?": "Orange", "R?": "220"}},
    {"block": "gpio_led", "as": "eye_r", "title": "Right eye (orange): water due", "nets": {"SIG": "EYE_R"},
     "values": {"D?": "Orange", "R?": "220"}},
    {"block": "merch_button", "as": "meds", "title": "Left wing: I took my meds", "nets": {"SIG": "MEDS"}},
    {"block": "merch_button", "as": "water", "title": "Right wing: I drank water", "nets": {"SIG": "WATER"}},
]

# ---------------------------------------------------------------------------------------- outline
body = K.Shape.ellipse(BODY_C[0], BODY_C[1], BODY_RX, BODY_RY)
tuft_l = K.Shape.poly([(7.5, 18.0), (9.0, 2.4), (19.0, 11.0)])
tuft_r = K.Shape.poly([(W - 7.5, 18.0), (W - 9.0, 2.4), (W - 19.0, 11.0)])
outline = (body | tuft_l | tuft_r).rounded(1.4)

# ---------------------------------------------------------------------------------------- parts
parts = K.design_footprints(BLOCKS, os.path.join(os.path.dirname(HERE), "..", "blocks"))
L = K.Layout(parts)
L.lock("eye_l:D?", CX - EYE_DX, EYE_Y, 180, "left eye")
L.lock("eye_r:D?", CX + EYE_DX, EYE_Y, 0, "right eye")
L.lock("eye_l:R?", CX - 2.2, 17.2, 0, "eye resistor, under the MCU")
L.lock("eye_r:R?", CX + 2.2, 17.2, 0, "eye resistor, under the MCU")
L.lock("mcu:U?", CX, 12.8, 0, "MCU on the forehead, between the tufts")
L.lock("mcu:C?", CX - 6.2, 13.0, 0, "bypass, beside VDD (pin 1)")
L.lock("bat:C?", CX + 6.2, 13.0, 0, "reservoir, mirrored on the other side")
L.lock("meds:SW?", 9.6, 40.0, 90, "left wing: meds")
L.lock("water:SW?", W - 9.6, 40.0, 90, "right wing: water")
L.lock("bat:BT?", CX, 41.6, 0, "the cell in the belly")
for i in range(3):
    L.lock("mcu:TP%d?" % (i + 1), CX - 2.54 + 2.54 * i, 53.6, 0, "UPDI pads (VCC, UPDI, GND)")

# ---------------------------------------------------------------------------------------- art
art = []
for sx in (-1, 1):
    ex = CX + sx * EYE_DX
    ring = K.Shape.circle(ex, EYE_Y, 4.4) - K.Shape.circle(ex, EYE_Y, 3.2)
    gap = K.Shape.rect(ex - 1.2, EYE_Y, ex + 1.2, EYE_Y + 5.0)          # the traces' way in, at the bottom
    art += K.gold(ring - gap, "eye_ring")
    art += K.silk_ring(K.Shape.circle(ex, EYE_Y, 5.6), "eye_disc", 0.25)
art += K.gold(K.Shape.poly([(CX - 1.8, 26.4), (CX + 1.8, 26.4), (CX, 30.0)]).rounded(0.3), "beak")
# wings: a long shallow arc down each side, threading the 1.5 mm between the wing button's pads and the
# cell holder's (peak x 12.85: 0.3 mm clear of the switch silk, 0.4 mm of the holder pad). The button
# sits in the wing, its word and icon above it.
for sx, word in ((-1, "meds"), (1, "water")):
    wx = CX + sx * 16.0                                     # the word and icon column
    a0, a1 = (-27, 28) if sx < 0 else (152, 207)
    art += K.silk_line(K.arc_points(CX + sx * 26.75, 40.0, 14.6, a0, a1, 24), "wing", 0.25)
    art += K.text(word, wx, 32.0, size=0.9, name="word_" + word)
pill = K.Shape.capsule(CX - 17.0, 34.6, CX - 15.0, 34.6, 0.6)
art += K.silk_ring(pill, "pill", 0.18)
art += K.silk_line([(CX - 16.0, 34.0), (CX - 16.0, 35.2)], "pill_mid", 0.18)
drop = K.Shape.circle(CX + 16.0, 35.0, 0.65) | K.Shape.poly([(CX + 15.42, 34.72), (CX + 16.58, 34.72), (CX + 16.0, 33.6)])
art += K.silk_ring(drop, "drop", 0.18)
art += K.text("heypcb.ai", CX, 55.4, size=0.8, bold=True, name="brand_front")   # on the chin, under the UPDI pads
# chest feathers under the eyes
for k in range(3):
    x = CX - 3.0 + 3.0 * k
    art += K.silk_line([(x - 1.0, 30.6), (x, 31.6), (x + 1.0, 30.6)], "feather", 0.2)
# back: magnets behind the eyes, the QR, how it works, the brand
for mx in (CX - EYE_DX, CX + EYE_DX):
    art += K.silk_ring(K.Shape.circle(mx, EYE_Y, 4.4), "magnet", 0.2, side="B")
    art += K.text("magnet", mx, EYE_Y, size=0.8, side="B", name="mag%d" % int(mx))
art += K.qr(K.world_url(SLUG), CX, 39.0, size=10.0, side="B")
for i, line in enumerate(["wing = done", "blinking eye = due", "meds 24 h, water 2 h", "hold 3 s: meds 12 h"]):
    art += K.text(line, CX, 47.4 + 1.8 * i, size=0.9, side="B", name="howto%d" % i)
art += K.text("heypcb.ai", CX, 14.6, size=1.1, side="B", bold=True, name="brand_back")

keep = {}
for i, it in enumerate(a for a in art if "F.Cu" in a.get("layers", [])):
    keep["gold%d" % i] = K.Shape.poly(it["points"]).offset(0.3)
if os.environ.get("MERCH_PREVIEW"):
    K.preview(os.environ["MERCH_PREVIEW"], outline, L, art, keep)
K.check_art(outline, art)
L.check(outline, edge=0.5, keep=keep)

brief = {
    "name": "fridge_owl",
    "title": "Hoot - fridge reminder owl: meds and water timers, two wing buttons, CR2032 magnet",
    "revision": "A",
    "brief": "An owl-shaped fridge magnet on one CR2032. An ATtiny412, asleep in power-down between 1 s RTC ticks, "
             "keeps two timers: press the left wing when you take your meds and the right wing when you drink "
             "water; when a reminder is due (24 h, or 12 h by choice, for meds; 2 h for water) that eye's orange "
             "LED blinks every 2 s until you press again, dozing to one flash every 10 s after an hour "
             "unanswered. 2 layers, single-sided SMT, yellow mask, black silk, ENIG.",
    "blocks": BLOCKS,
    "pwrFlags": ["GND", "VBAT"],
    "netClasses": [],
    "board": {
        "width": W, "height": H, "corner_radius": 0.0, "layers": 2, "origin": [100.0, 100.0],
        "shape": {"type": "polygon", "points": K.outline_points(outline), "fillet": 0},
        "rules": {"clearance": 0.2, "track": 0.2, "via": [0.6, 0.3], "edge_clearance": 0.5,
                  "hole_to_hole": 0.5, "min_through_hole": 0.3, "min_track": 0.15},
        "finish": {"mask": "Yellow", "silk": "Black", "copper": "ENIG",
                   "why": "a cheerful kitchen owl drawn in black ink, gold eye rings and beak"},
        "unpoured": ["F.Cu"],
        "notes": "2 layers; the face is unpoured, GND plane on the back. The back is flat for two magnets.",
    },
    "placement": L.locks,
    "route": {"passes": 30, "fanout": True, "solve_s": 240},
    "stitch_pitch": 6.0,
    "silk": {"designators": "hide",
             "title": [{"text": "Hoot", "y": 26.0, "size": 2.0, "bold": True},
                       {"text": "fridge reminder owl  rev {revision}", "y": 28.8, "size": 0.9}]},
    "art": art,
    "captions": {"done_3d": "Hoot: gold-ringed LED eyes, two wing buttons, a CR2032 belly, magnets on the back."},
}
K.write_brief(os.path.join(HERE, "board.json"), brief)
print("wrote board.json: %d outline points, %d art items, %d locks, QR -> %s"
      % (len(brief["board"]["shape"]["points"]), len(art), len(L.locks), K.world_url(SLUG)))
