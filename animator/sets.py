"""Backgrounds, sets, props and effect marks for the box-head style (style_bible.md 4-5).
Everything is flat colour with the same thin ink line as the characters (style.pen)."""
import math
import random

import cairo

from engine import PI, W, H, hexc
from style import INK, TEAR, WHITE, fill_ink, pen, _ink, _fill

# ---------------------------------------------------------------- palette (sampled from the references)
MOOD = {
    "neutral": ["#6296ce", "#4666aa", "#c2d2fe", "#aed6ea"],
    "warm": ["#fece92", "#fed68e", "#fefaca", "#7ed6d6", "#e2929e", "#5aeeca", "#e2b672"],
    "tension": ["#fe722e", "#62527a", "#de6a1e"],
    "shock": ["#eaca22", "#e28212"],
    "sad": ["#565e66", "#5a5e76", "#52567a", "#8a76b2", "#028666", "#ca8ace"],
    "base": ["#ce7a6a", "#d28682"],
    "skin": ["#f6d6c6"],
}
METAL, WOOD, GLASS = hexc("#848484"), hexc("#6a4a2e"), hexc("#aee4f0")


def settle(ctx, T, px=5.0):
    """Held-pose settle for a prop insert: shift the drawing a few screen px every quarter second
    (the references redraw every 3-4 frames and hold in between). Call before drawing the prop;
    wrap in ctx.save()/restore()."""
    k = 1 if int(T * 4) % 2 else -1
    dpx = math.hypot(*ctx.user_to_device_distance(1.0, 0.0)) or 1.0
    ctx.translate(0.6 * k * px / dpx, -k * px / dpx)


def bg(ctx, col):
    """Flat background colour filling everything the camera can see."""
    _fill(ctx, hexc(col) if isinstance(col, str) else col)
    ctx.rectangle(-4000, -4000, W + 8000, H + 8000)
    ctx.fill()


def lw_at(ctx, size=96):
    return pen(ctx, size)


def poly(ctx, pts, col, lw, close=True):
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    col = hexc(col) if isinstance(col, str) else col
    if close:
        ctx.close_path()
        fill_ink(ctx, col, lw)
    else:          # open polyline: stroked in its own colour
        _ink(ctx, lw, col)


def bar(ctx, p0, p1, col, w):
    """Thick coloured bar with an ink outline (metal rods, handles)."""
    lw = lw_at(ctx, w * 8)
    for c, ww in ((INK, w + 2 * lw), (hexc(col) if isinstance(col, str) else col, w)):
        ctx.move_to(*p0)
        ctx.line_to(*p1)
        _ink(ctx, ww, c)


def rect(ctx, x, y, w, h, col, lw, r=0.0):
    if r:
        ctx.new_sub_path()
        ctx.arc(x + w - r, y + r, r, -PI / 2, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, PI / 2)
        ctx.arc(x + r, y + h - r, r, PI / 2, PI)
        ctx.arc(x + r, y + r, r, PI, 1.5 * PI)
        ctx.close_path()
    else:
        ctx.rectangle(x, y, w, h)
    fill_ink(ctx, hexc(col) if isinstance(col, str) else col, lw)


def oval(ctx, x, y, rx, ry, col, lw, rot=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(rx, ry)
    ctx.new_sub_path()
    ctx.arc(0, 0, 1, 0, 2 * PI)
    ctx.restore()
    fill_ink(ctx, hexc(col) if isinstance(col, str) else col, lw)


def scrawl(ctx, s, x, y, size, col=INK, rot=0.0):
    """Hand-written word (calendar months, labels): thin sans, slightly tilted."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    e = ctx.text_extents(s)
    ctx.move_to(-e.width / 2 - e.x_bearing, e.height / 2)
    _fill(ctx, col)
    ctx.show_text(s)
    ctx.restore()


# ---------------------------------------------------------------- sets
def room_box(ctx, back="#c2d2fe", side="#aebef0", floor="#606696", rug="#6296ce", door=True, shelf=True,
             box=(170, 330, 550, 700)):
    """One-point perspective box room (garage / bedroom from the doorway, monitor ref 4.6 s)."""
    lw = lw_at(ctx, 140)
    bg(ctx, side)
    x0, y0, x1, y1 = box
    poly(ctx, [(-400, -400), (x0, y0), (x1, y0), (W + 400, -400)], hexc(side), lw)            # ceiling
    poly(ctx, [(-400, H + 600), (x0, y1), (x1, y1), (W + 400, H + 600)], hexc(floor), lw)      # floor
    poly(ctx, [(-400, -400), (x0, y0), (x0, y1), (-400, H + 600)], hexc(side), lw)              # left wall
    poly(ctx, [(W + 400, -400), (x1, y0), (x1, y1), (W + 400, H + 600)], hexc(side), lw)        # right wall
    rect(ctx, x0, y0, x1 - x0, y1 - y0, back, lw)
    if door:
        poly(ctx, [(x1 + 25, y1 + 40), (x1 + 25, y0 + 120), (x1 + 75, y0 + 70), (x1 + 75, y1 + 100)], "#3a3c48", lw)
    if shelf:
        poly(ctx, [(x0 + 90, y0 + 120), (x1 - 90, y0 + 120)], INK, lw * 1.6, close=False)
        for k in range(3):
            rect(ctx, x0 + 110 + k * 26, y0 + 98, 22, 20, "#ffffff", lw)
    if rug:
        oval(ctx, W / 2, y1 + 380, 520, 190, rug, lw)


def wall_floor(ctx, wall="#fefaca", floor="#c6c09c", y=900, tilt=-60):
    """A pale wall over a darker floor band (socket / corner shots)."""
    lw = lw_at(ctx, 140)
    bg(ctx, wall)
    poly(ctx, [(-400, y - tilt), (W + 400, y + tilt), (W + 400, H + 600), (-400, H + 600)], floor, lw)


def desk(ctx, x, y, w=300, col="#303030"):
    lw = lw_at(ctx, w * 0.4)
    rect(ctx, x - w / 2, y, w, 22, col, lw)
    for k in (-1, 1):
        rect(ctx, x + k * (w / 2 - 20) - 8, y + 22, 16, 210, col, lw)


def chair(ctx, x, y, s=1.0, col="#d8b07a", side=True):
    """Simple wooden chair, seat top at y (side view like monitor ref 28.5 s)."""
    lw = lw_at(ctx, 96 * s)
    u = 96 * s
    rect(ctx, x - 0.55 * u, y, 1.1 * u, 0.14 * u, col, lw)
    for k in (-1, 1):
        rect(ctx, x + k * 0.45 * u - 0.05 * u, y + 0.14 * u, 0.1 * u, 1.0 * u, col, lw)
    rect(ctx, x + (0.42 if side else -0.52) * u, y - 1.2 * u, 0.1 * u, 1.2 * u, col, lw)


def monitor(ctx, x, y, w=420, glint=0.0, cracked=0.0, on=False, rot=0.0):
    """Flat monitor on a stand, centre of the screen at (x, y). glint 0..1 draws the sparkle."""
    lw = lw_at(ctx, w * 0.3)
    h = w * 0.58
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    rect(ctx, -0.07 * w, h / 2, 0.14 * w, 0.12 * w, "#202020", lw)
    oval(ctx, 0, h / 2 + 0.13 * w, 0.22 * w, 0.03 * w, "#202020", lw)
    rect(ctx, -w / 2, -h / 2, w, h, "#303030", lw, r=0.02 * w)
    rect(ctx, -w / 2 + 0.03 * w, -h / 2 + 0.03 * w, w - 0.06 * w, h - 0.06 * w,
         "#2f6fb5" if on else "#000000", lw * 0.6)
    if cracked > 0:
        rnd = random.Random(7)
        for k in range(9):
            a = rnd.uniform(0, 2 * PI)
            ln = rnd.uniform(0.25, 0.5) * w * cracked
            px, py = -0.05 * w, -0.03 * w
            pts = [(px, py)]
            for j in range(3):
                px += math.cos(a + rnd.uniform(-0.4, 0.4)) * ln / 3
                py += math.sin(a + rnd.uniform(-0.4, 0.4)) * ln / 3
                pts.append((max(-w / 2 + 12, min(w / 2 - 12, px)), max(-h / 2 + 12, min(h / 2 - 12, py))))
            poly(ctx, pts, WHITE, lw * 0.9, close=False)
            ctx.set_source_rgb(1, 1, 1)
    ctx.restore()
    if glint > 0:
        sparkle(ctx, x + w / 2 - 0.02 * w, y - h / 2 + 0.03 * w, 0.09 * w * glint, "#fff6c8")


def socket(ctx, x, y, s=1.0, plugged=1.0):
    """Wall socket; plugged 1 = plug in, 0 = pulled out (the cable swings)."""
    lw = lw_at(ctx, 96 * s)
    u = 96 * s
    rect(ctx, x - 0.6 * u, y - 0.42 * u, 1.2 * u, 0.84 * u, "#c8c8c8", lw, r=0.05 * u)
    for k in (-1, 1):
        rect(ctx, x + k * 0.27 * u - 0.15 * u, y - 0.25 * u, 0.3 * u, 0.5 * u, "#e6e6e6", lw)
        for j in (-1, 1):
            rect(ctx, x + k * 0.27 * u + j * 0.06 * u - 0.015 * u, y - 0.08 * u, 0.03 * u, 0.1 * u, INK, lw * 0.5)
    px = x - 0.27 * u - (1 - plugged) * 0.6 * u
    py = y + (1 - plugged) * 0.1 * u
    ctx.move_to(px, py + 0.1 * u)
    ctx.curve_to(px - 0.4 * u, py + 1.4 * u, px - 1.4 * u, py + 1.6 * u, px - 3.5 * u, py + 2.4 * u)
    _ink(ctx, 0.07 * u, hexc("#262626"))
    rect(ctx, px - 0.14 * u, py - 0.14 * u, 0.28 * u, 0.3 * u, "#262626", lw, r=0.04 * u)
    return px, py


def bunk(ctx, x, y, s=1.0, mattress="#f4f0ea", frame="#848484", blanket=None, two=True, dark=False):
    """Hospital / bunk bed frame; y = floor. Returns the top surfaces (lower, upper) as y values."""
    lw = lw_at(ctx, 120 * s)
    u = 100 * s
    w = 4.2 * u
    lower, upper = y - 1.4 * u, y - 4.1 * u
    for k in (-1, 1):
        rect(ctx, x + k * (w / 2) - 0.09 * u, (upper - 0.2 * u) if two else (lower - 0.2 * u), 0.18 * u,
             y - ((upper - 0.2 * u) if two else (lower - 0.2 * u)), frame, lw)
        oval(ctx, x + k * (w / 2), y, 0.12 * u, 0.12 * u, "#202020", lw)
    for top in ((lower, upper) if two else (lower,)):
        rect(ctx, x - w / 2 - 0.1 * u, top, w + 0.2 * u, 0.42 * u, frame, lw)
        rect(ctx, x - w / 2 + 0.05 * u, top - 0.32 * u, w - 0.1 * u, 0.34 * u, mattress, lw, r=0.12 * u)
        if blanket:
            rect(ctx, x - w / 2 + 1.1 * u, top - 0.38 * u, w - 1.2 * u, 0.4 * u, blanket, lw, r=0.12 * u)
    return lower - 0.32 * u, upper - 0.32 * u


def pillow(ctx, x, y, s=1.0, col="#c8f0fc", rot=-0.35):
    oval(ctx, x, y, 1.0 * 96 * s, 0.5 * 96 * s, col, lw_at(ctx, 96 * s), rot)


def blanket(ctx, x, y, s=1.0, col="#7aa6aa", fold="#54787e", rot=-0.35):
    """Big body-under-blanket shape for the in-bed close-up (window ref 0.0 s): a rounded hump
    from (x, y) toward the bottom-left corner, plus a darker turned-down fold."""
    lw = lw_at(ctx, 96 * s)
    u = 96 * s
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.move_to(-0.3 * u, -0.1 * u)
    ctx.curve_to(-1.4 * u, -0.6 * u, -3.4 * u, -0.5 * u, -4.4 * u, 0.4 * u)
    ctx.line_to(-4.4 * u, 6 * u)
    ctx.line_to(2.5 * u, 6 * u)
    ctx.curve_to(1.6 * u, 3.0 * u, 1.0 * u, 1.0 * u, -0.3 * u, -0.1 * u)
    ctx.close_path()
    fill_ink(ctx, hexc(col), lw)
    ctx.move_to(-0.1 * u, 0.0)
    ctx.curve_to(-0.9 * u, 0.4 * u, -1.6 * u, 0.3 * u, -2.1 * u, 0.1 * u)
    ctx.curve_to(-1.6 * u, 0.9 * u, -0.6 * u, 1.0 * u, 0.6 * u, 0.6 * u)
    ctx.close_path()
    fill_ink(ctx, hexc(fold), lw)
    ctx.restore()


def in_bed(ctx, ch, x, y, s=1.0, expr="sleep", t=0.0, rot=0.5, pillow_col="#c8f0fc", cover=None,
           collar=None, talk=False, look=0.0):
    """Close-up of a character lying in bed (window refs 0.0 s and 26.6 s): head bottom centre at
    (x, y) tilted by rot, pillow behind the head, the body under a blanket running off the frame,
    a darker collar under the chin."""
    U = ch.unit(s)
    hh = ch.b["head_h"] * U
    lw = pen(ctx, U)
    cover = hexc(cover) if cover else ch.body
    collar = hexc(collar) if collar else (ch.stripes or tuple(v * 0.72 for v in ch.body))
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    oval(ctx, 0.25 * U, -0.6 * hh, 0.8 * U, 0.62 * U, pillow_col, lw, rot=0.05)
    ctx.move_to(-0.75 * U, 0.15 * U)                       # body under the blanket
    ctx.curve_to(-0.8 * U, 1.2 * U, -1.6 * U, 2.6 * U, -2.6 * U, 6 * U)
    ctx.line_to(3.4 * U, 6 * U)
    ctx.curve_to(1.6 * U, 2.6 * U, 1.0 * U, 0.6 * U, 0.75 * U, 0.15 * U)
    ctx.close_path()
    fill_ink(ctx, cover, lw)
    ctx.move_to(-0.62 * U, -0.05 * U)                      # collar
    ctx.curve_to(-0.7 * U, 0.35 * U, -0.3 * U, 0.6 * U, 0.1 * U, 0.55 * U)
    ctx.curve_to(0.5 * U, 0.5 * U, 0.75 * U, 0.3 * U, 0.6 * U, -0.05 * U)
    ctx.close_path()
    fill_ink(ctx, collar, lw)
    ctx.restore()
    ch.draw_head(ctx, x, y, s, expr, t, talk=talk, look=look, rot=rot)


def bricks(ctx, x, y, w, h, base="#9c9c9c", warm="#c08060", mortar=INK, seed=3):
    lw = lw_at(ctx, w * 0.5)
    rect(ctx, x, y, w, h, base, lw)
    ctx.save()
    ctx.rectangle(x, y, w, h)
    ctx.clip()
    rnd = random.Random(seed)
    bh, bw = h / 9, w / 3.2
    for r in range(10):
        off = (r % 2) * bw / 2
        for c in range(-1, 5):
            col = warm if rnd.random() < 0.35 else base
            rect(ctx, x + c * bw + off, y + r * bh, bw, bh, col, lw * 0.7)
    ctx.restore()


def window(ctx, x, y, w, h, view="sky", frame="#6a4a2e", tilt=0.0, open_=0.0):
    """Window with a wooden frame: view 'sky' (blue glass), 'night', 'bricks' (the reveal)."""
    lw = lw_at(ctx, w * 0.35)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(tilt)
    f = 0.08 * w
    rect(ctx, -w / 2 - f, -h / 2 - f, w + 2 * f, h + 2 * f, frame, lw)
    if view == "bricks":
        bricks(ctx, -w / 2, -h / 2, w, h)
    else:
        rect(ctx, -w / 2, -h / 2, w, h, {"sky": "#aee4f0", "night": "#363a5e"}.get(view, view), lw)
    rect(ctx, -f * 0.4, -h / 2, f * 0.8, h, frame, lw)
    ctx.restore()


def sunset(ctx, T=0.0, sky="#de721e", sun="#fce45a"):
    """Flat sunset landscape: big sun, wavy layered green hills (window ref 8.5 s)."""
    lw = lw_at(ctx, 150)
    bg(ctx, sky)
    oval(ctx, W / 2, 470 - T * 8, 175, 175, sun, lw)
    layers = [("#1e6c3c", 600, 50), ("#e4de8a", 650, 40), ("#5aa878", 690, 55), ("#e4de8a", 760, 35),
              ("#78ba90", 790, 60), ("#5aa878", 960, 45), ("#78ba90", 1010, 55)]
    for i, (col, yb, amp) in enumerate(layers):
        ctx.move_to(-400, H + 600)
        for k in range(0, 1561, 40):
            xx = -400 + k
            ctx.line_to(xx, yb + math.sin(xx / 130 + i * 1.7) * amp * 0.6 + math.sin(xx / 61 + i) * amp * 0.25)
        ctx.line_to(W + 400, H + 600)
        ctx.close_path()
        fill_ink(ctx, hexc(col), lw)


def sky(ctx, T=0.0, col="#aed6ea", sun_x=640, sun_y=330, sun="#e2a812"):
    """Day sky with long cloud bands and a sun peeking in (time jump, window ref 17.6 s)."""
    lw = lw_at(ctx, 150)
    bg(ctx, col)
    oval(ctx, sun_x, sun_y, 230, 230, sun, lw * 0.01)
    for i, (yy, x0) in enumerate(((420, -60), (560, 260), (760, -120), (960, 300))):
        x0 += T * 30 * (1 if i % 2 else -1)
        ctx.move_to(x0, yy)
        ctx.curve_to(x0 + 120, yy - 40, x0 + 260, yy - 10, x0 + 420, yy - 25)
        ctx.curve_to(x0 + 300, yy + 30, x0 + 160, yy + 25, x0, yy)
        ctx.close_path()
        _fill(ctx, hexc("#e8f4fa"))
        ctx.fill()


def spotlight(ctx, x, y, w=420):
    """Pale ellipse on the floor under a lone character (monitor ref 28.5 s)."""
    oval(ctx, x, y, w / 2, w * 0.17, "#f4f4f4", lw_at(ctx, 120))


# ---------------------------------------------------------------- props
def hammer(ctx, x, y, s=1.0, rot=0.0):
    """Claw hammer held at (x, y) (the grip); s=1 is about 250 px long."""
    lw = lw_at(ctx, 96 * s)
    u = 96 * s
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    rect(ctx, -0.3 * u, -0.09 * u, 2.6 * u, 0.18 * u, "#5c2e26", lw, r=0.08 * u)
    poly(ctx, [(2.3 * u, -0.45 * u), (2.62 * u, -0.45 * u), (2.62 * u, 0.25 * u), (2.3 * u, 0.25 * u)], METAL, lw)
    ctx.move_to(2.3 * u, -0.4 * u)
    ctx.curve_to(2.1 * u, -0.5 * u, 2.0 * u, -0.3 * u, 2.05 * u, 0.1 * u)
    ctx.line_to(2.22 * u, -0.05 * u)
    ctx.close_path()
    fill_ink(ctx, METAL, lw)
    rect(ctx, 2.25 * u, 0.2 * u, 0.42 * u, 0.2 * u, METAL, lw, r=0.05 * u)
    ctx.restore()


def bat(ctx, x, y, s=1.0, rot=0.0, col="#c48a4e"):
    lw = lw_at(ctx, 96 * s)
    u = 96 * s
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.move_to(-0.3 * u, -0.06 * u)
    ctx.line_to(0.8 * u, -0.07 * u)
    ctx.curve_to(1.6 * u, -0.18 * u, 2.6 * u, -0.2 * u, 2.7 * u, 0.0)
    ctx.curve_to(2.6 * u, 0.2 * u, 1.6 * u, 0.18 * u, 0.8 * u, 0.07 * u)
    ctx.line_to(-0.3 * u, 0.06 * u)
    ctx.close_path()
    fill_ink(ctx, hexc(col), lw)
    ctx.restore()


def phone(ctx, x, y, s=1.0, rot=0.0, screen="#3a3a3a", glow=0.0):
    lw = lw_at(ctx, 96 * s)
    u = 96 * s
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    rect(ctx, -0.35 * u, -0.6 * u, 0.7 * u, 1.2 * u, "#8a8a8a", lw, r=0.1 * u)
    rect(ctx, -0.29 * u, -0.52 * u, 0.58 * u, 1.04 * u, "#9cc8f0" if glow else screen, lw * 0.7, r=0.06 * u)
    rect(ctx, 0.08 * u, -0.5 * u, 0.18 * u, 0.24 * u, "#222222", lw * 0.6, r=0.04 * u)
    ctx.restore()


def balloons(ctx, x, y, s=1.0, T=0.0):
    """Bunch of glossy balloons; strings meet at (x, y) (window ref 7.5 s)."""
    lw = lw_at(ctx, 96 * s)
    u = 96 * s
    cols = ["#e8302a", "#7e54ae", "#3aa8a0", "#9cb41e", "#d8ae12", "#727ea8", "#e8302a", "#7e54ae", "#3aa8a0",
            "#9cb41e", "#d8ae12", "#727ea8"]
    rnd = random.Random(5)
    pos = [(rnd.uniform(-1.2, 1.2) * u, rnd.uniform(-4.4, -2.6) * u) for _ in cols]
    for (bx, by) in pos:
        ctx.move_to(x, y)
        ctx.curve_to(x + bx * 0.2, y - 1.0 * u, bx * 0.9 + x, by + 1.2 * u, x + bx, by + 0.5 * u + y - y)
        _ink(ctx, lw * 0.7)
    for k, ((bx, by), c) in enumerate(sorted(zip(pos, cols), key=lambda p: p[0][1])):
        sway = math.sin(T * 2 + k) * 0.04 * u
        oval(ctx, x + bx + sway, by, 0.42 * u, 0.5 * u, c, lw)
        oval(ctx, x + bx + sway - 0.14 * u, by - 0.2 * u, 0.06 * u, 0.1 * u, "#ffffff", 0.001, rot=0.5)


def ball(ctx, x, y, r=40):
    lw = lw_at(ctx, r * 2)
    oval(ctx, x, y, r, r, "#ffffff", lw)
    for k in range(5):
        a = k * 2 * PI / 5
        oval(ctx, x + math.cos(a) * r * 0.62, y + math.sin(a) * r * 0.62, r * 0.22, r * 0.22, "#202020", lw * 0.5)
    oval(ctx, x, y, r * 0.25, r * 0.25, "#202020", lw * 0.5)


def calendar(ctx, x, y, s=1.0, month="MARCH", crossed=1.0, rot=0.0):
    """Calendar page with a red X drawn over it (crossed 0..1 = how much of the X is drawn)."""
    lw = lw_at(ctx, 96 * s)
    u = 96 * s
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    rect(ctx, -1.1 * u, -1.0 * u, 2.2 * u, 2.0 * u, "#ffffff", lw)
    scrawl(ctx, month, 0, -0.72 * u, 0.32 * u, INK, 0.0)
    for r in range(6):
        ctx.move_to(-1.0 * u, -0.4 * u + r * 0.27 * u)
        ctx.line_to(1.0 * u, -0.4 * u + r * 0.27 * u)
    for c in range(8):
        ctx.move_to(-1.0 * u + c * 2.0 * u / 7, -0.4 * u)
        ctx.line_to(-1.0 * u + c * 2.0 * u / 7, 0.95 * u)
    _ink(ctx, lw * 0.7)
    red = hexc("#b8322a")
    for k, (a, b) in enumerate((((-1.2, -1.0), (1.2, 1.0)), ((1.2, -1.0), (-1.2, 1.0)))):
        f = max(0.0, min(1.0, crossed * 2 - k))
        if f > 0:
            ctx.move_to(a[0] * u, a[1] * u)
            ctx.line_to((a[0] + (b[0] - a[0]) * f) * u, (a[1] + (b[1] - a[1]) * f) * u)
            _ink(ctx, lw * 1.5, red)
    ctx.restore()


def shards(ctx, x, y, s=1.0, seed=1, n=9, spread=1.0):
    """Black glass shards on the floor (monitor ref 20 s)."""
    lw = lw_at(ctx, 96 * s)
    u = 96 * s
    rnd = random.Random(seed)
    for _ in range(n):
        cx, cy = x + rnd.uniform(-2.6, 2.6) * u * spread, y + rnd.uniform(-1.2, 1.2) * u * spread
        r = rnd.uniform(0.12, 0.4) * u
        a0 = rnd.uniform(0, PI)
        pts = [(cx + math.cos(a0 + k * 2.1 + rnd.uniform(-0.3, 0.3)) * r,
                cy + math.sin(a0 + k * 2.1) * r * 0.35) for k in range(3)]
        poly(ctx, pts, "#141418", lw)


def hand(ctx, x, y, s=1.0, rot=0.0, col="#fdcdc7", pose="open", length=6.0):
    """An arm entering from off-screen ending in a hand at (x, y); rot = direction the arm comes
    FROM (0 = from the right). pose: open, fist, grab."""
    lw = lw_at(ctx, 96 * s)
    u = 96 * s
    col = hexc(col) if isinstance(col, str) else col
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.move_to(length * u, -0.32 * u)
    ctx.curve_to(2 * u, -0.34 * u, 0.6 * u, -0.3 * u, 0.25 * u, -0.28 * u)
    ctx.line_to(0.25 * u, 0.28 * u)
    ctx.curve_to(0.6 * u, 0.3 * u, 2 * u, 0.34 * u, length * u, 0.32 * u)
    ctx.close_path()
    fill_ink(ctx, col, lw)
    if pose == "fist":
        oval(ctx, 0, 0, 0.48 * u, 0.42 * u, col, lw)
        for k in range(3):
            ctx.move_to(-0.42 * u, -0.18 * u + k * 0.16 * u)
            ctx.line_to(-0.1 * u, -0.18 * u + k * 0.16 * u)
        _ink(ctx, lw * 0.8)
    else:
        ctx.move_to(0.3 * u, -0.3 * u)
        ctx.curve_to(-0.2 * u, -0.45 * u, -0.6 * u, -0.25 * u, -0.6 * u, 0.0)
        ctx.curve_to(-0.6 * u, 0.25 * u, -0.2 * u, 0.42 * u, 0.3 * u, 0.3 * u)
        ctx.close_path()
        fill_ink(ctx, col, lw)
        oval(ctx, -0.05 * u, -0.38 * u, 0.24 * u, 0.12 * u, col, lw, rot=-0.4)
    ctx.restore()


def eye(ctx, x, y, s=1.0, pupil="dot", look=(0.0, 0.0), skin="#f6d6c6"):
    """Extreme close-up of one eye filling the frame (window refs 2.5 s and 29.8 s).
    pupil: dot, wide, dashed (blind), none."""
    lw = lw_at(ctx, 200 * s)
    u = 100 * s
    ctx.move_to(x - 2.9 * u, y)
    ctx.curve_to(x - 1.6 * u, y - 2.3 * u, x + 1.6 * u, y - 2.3 * u, x + 2.9 * u, y)
    ctx.curve_to(x + 1.6 * u, y + 2.0 * u, x - 1.6 * u, y + 2.0 * u, x - 2.9 * u, y)
    ctx.close_path()
    fill_ink(ctx, WHITE, lw)
    ctx.move_to(x - 3.1 * u, y + 0.3 * u)
    ctx.curve_to(x - 2.0 * u, y + 2.4 * u, x + 1.6 * u, y + 2.5 * u, x + 3.0 * u, y + 0.4 * u)
    _ink(ctx, lw * 0.8, hexc("#c49a88"))
    px, py = x + look[0] * u, y + look[1] * u
    if pupil == "dashed":
        ctx.set_dash([0.22 * u, 0.15 * u])
        ctx.new_sub_path()
        ctx.arc(px, py, 0.42 * u, 0, 2 * PI)
        _ink(ctx, lw * 1.2)
        ctx.set_dash([])
    elif pupil != "none":
        r = 0.55 if pupil == "wide" else 0.42
        oval(ctx, px, py, r * u, r * u, "#000000", lw)
        oval(ctx, px + 0.15 * u, py - 0.15 * u, 0.1 * u, 0.1 * u, "#ffffff", 0.001)


# ---------------------------------------------------------------- more props (sample story)
def teddy(ctx, x, y, s=1.0, rot=0.0, col="#b07a46", worn=True):
    """Old teddy bear, centre of the belly at (x, y); s=1 is about 190 px tall."""
    lw = lw_at(ctx, 96 * s)
    u = 96 * s
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    for k in (-1, 1):
        oval(ctx, k * 0.42 * u, 0.62 * u, 0.24 * u, 0.2 * u, col, lw)        # feet
        oval(ctx, k * 0.6 * u, -0.05 * u, 0.2 * u, 0.32 * u, col, lw, rot=k * 0.5)   # arms
        oval(ctx, k * 0.38 * u, -1.32 * u, 0.2 * u, 0.2 * u, col, lw)       # ears
        oval(ctx, k * 0.38 * u, -1.32 * u, 0.09 * u, 0.09 * u, "#e8c49a", lw * 0.7)
    oval(ctx, 0, 0.15 * u, 0.55 * u, 0.62 * u, col, lw)
    oval(ctx, 0, 0.25 * u, 0.3 * u, 0.32 * u, "#e8c49a", lw * 0.8)
    oval(ctx, 0, -0.9 * u, 0.5 * u, 0.44 * u, col, lw)
    oval(ctx, 0, -0.78 * u, 0.2 * u, 0.15 * u, "#e8c49a", lw * 0.8)
    oval(ctx, 0, -0.84 * u, 0.06 * u, 0.045 * u, INK, 0.001)
    for k in (-1, 1):   # one button eye, one stitched cross (worn out)
        if k < 0 or not worn:
            oval(ctx, k * 0.2 * u, -1.0 * u, 0.05 * u, 0.05 * u, INK, 0.001)
        else:
            poly(ctx, [(0.15 * u, -1.05 * u), (0.25 * u, -0.95 * u)], INK, lw, close=False)
            poly(ctx, [(0.25 * u, -1.05 * u), (0.15 * u, -0.95 * u)], INK, lw, close=False)
    if worn:   # a patch
        rect(ctx, -0.42 * u, 0.0, 0.2 * u, 0.2 * u, "#7a9ec8", lw * 0.8)
    ctx.restore()


def trash_bin(ctx, x, y, s=1.0, col="#7c8a90", lid=0.0):
    """Kitchen bin, bottom centre at (x, y); lid 0..1 opens the flip lid."""
    lw = lw_at(ctx, 96 * s)
    u = 96 * s
    poly(ctx, [(x - 1.1 * u, y - 3.0 * u), (x + 1.1 * u, y - 3.0 * u), (x + 0.9 * u, y), (x - 0.9 * u, y)], col, lw)
    for k in (-1, 0, 1):
        poly(ctx, [(x + k * 0.5 * u, y - 2.7 * u), (x + k * 0.42 * u, y - 0.3 * u)], INK, lw * 0.8, close=False)
    ctx.save()
    ctx.translate(x - 1.15 * u, y - 3.0 * u)
    ctx.rotate(-1.9 * lid)
    rect(ctx, 0, -0.25 * u, 2.3 * u, 0.25 * u, "#5c686e", lw, r=0.06 * u)
    ctx.restore()


def chalkboard(ctx, x, y, w=420, h=230):
    lw = lw_at(ctx, w * 0.3)
    rect(ctx, x - w / 2 - 14, y - h / 2 - 14, w + 28, h + 28, "#8a5a36", lw)
    rect(ctx, x - w / 2, y - h / 2, w, h, "#2f5a44", lw)
    scrawl(ctx, "2 + 2 = 4", x - w * 0.12, y - h * 0.15, h * 0.17, hexc("#e8eee8"), -0.03)
    scrawl(ctx, "A B C", x + w * 0.15, y + h * 0.2, h * 0.15, hexc("#e8eee8"), 0.02)


def school_desk(ctx, x, y, s=1.0, col="#d8b07a"):
    """Small school desk, top surface at y."""
    lw = lw_at(ctx, 96 * s)
    u = 96 * s
    rect(ctx, x - 0.9 * u, y, 1.8 * u, 0.15 * u, col, lw)
    for k in (-1, 1):
        rect(ctx, x + k * 0.75 * u - 0.05 * u, y + 0.15 * u, 0.1 * u, 0.9 * u, "#6a6a6a", lw)


def cardboard_box(ctx, x, y, s=1.0, open_=0.0, col="#c9995e"):
    """Box, bottom centre at (x, y); open_ 0..1 swings the two top flaps outward."""
    lw = lw_at(ctx, 96 * s)
    u = 96 * s
    if open_ > 0.05:
        for k in (-1, 1):
            ctx.save()
            ctx.translate(x + k * 1.0 * u, y - 1.3 * u)
            ctx.rotate(-k * (PI - open_ * 2.3))
            rect(ctx, 0 if k < 0 else -1.0 * u, -0.06 * u, 1.0 * u, 0.12 * u, "#b4844c", lw)
            ctx.restore()
    rect(ctx, x - 1.0 * u, y - 1.3 * u, 2.0 * u, 1.3 * u, col, lw)
    if open_ <= 0.05:
        poly(ctx, [(x, y - 1.3 * u), (x, y - 0.95 * u)], INK, lw, close=False)


def note(ctx, x, y, s=1.0, unfold=1.0, rot=0.0, lines=("Mr. Button kept", "me company...")):
    """Folded paper note opening up; the writing appears when unfolded."""
    lw = lw_at(ctx, 96 * s)
    u = 96 * s
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    hh = 0.8 * u + 0.9 * u * unfold
    rect(ctx, -1.3 * u, -hh / 2, 2.6 * u, hh, "#fbf7ee", lw)
    if unfold > 0.6:
        for k, ln in enumerate(lines):
            scrawl(ctx, ln, 0, -0.35 * u + k * 0.5 * u, 0.3 * u, hexc("#2a3a8a"), -0.03)
    else:
        poly(ctx, [(-1.3 * u, 0), (1.3 * u, 0)], INK, lw * 0.7, close=False)
    ctx.restore()


def closet(ctx, x, y, w=420, h=640, open_=1.0):
    """Wardrobe, bottom centre at (x, y); open_ swings the right door; clothes on a rail."""
    lw = lw_at(ctx, w * 0.3)
    rect(ctx, x - w / 2, y - h, w, h, "#8a5a36", lw)
    rect(ctx, x - w / 2 + 16, y - h + 16, w - 32, h - 32, "#3a2a22", lw)
    poly(ctx, [(x - w / 2 + 20, y - h + 70), (x + w / 2 - 20, y - h + 70)], METAL, lw * 2, close=False)
    for k, c in enumerate(("#e2929e", "#7ed6d6", "#fece92", "#8a76b2")):
        cx = x - w / 2 + 70 + k * 90
        poly(ctx, [(cx - 34, y - h + 80), (cx + 34, y - h + 80), (cx + 44, y - h + 330), (cx - 44, y - h + 330)], c, lw)
    wd = (w / 2) * (1 - open_)
    if open_ < 1:
        rect(ctx, x + w / 2 - wd - 0.0, y - h, wd, h, "#a06c44", lw)
    else:
        poly(ctx, [(x + w / 2, y - h), (x + w / 2 + 110, y - h + 50), (x + w / 2 + 110, y - 30), (x + w / 2, y)], "#a06c44", lw)


def sofa(ctx, x, y, w=520, col="#6f8f5a"):
    """Sofa seen from the front, seat top at y."""
    lw = lw_at(ctx, w * 0.25)
    rect(ctx, x - w / 2, y - 210, w, 230, col, lw, r=40)
    rect(ctx, x - w / 2 + 50, y - 20, w - 100, 90, col, lw, r=20)
    for k in (-1, 1):
        rect(ctx, x + k * (w / 2) - 55, y - 80, 110, 190, col, lw, r=40)


def bed_side(ctx, x, y, w=520, blanket="#e2929e", pillow_col="#ffffff"):
    """Single bed seen from the side, mattress top at y (for sitting on its edge)."""
    lw = lw_at(ctx, w * 0.25)
    rect(ctx, x - w / 2 - 20, y - 140, 40, 290, "#a06c44", lw)
    rect(ctx, x - w / 2, y, w, 70, "#f4f0ea", lw, r=18)
    rect(ctx, x - w / 2 + 120, y - 6, w - 120, 50, blanket, lw, r=18)
    oval(ctx, x - w / 2 + 70, y - 12, 60, 28, pillow_col, lw)
    for k in (-1, 1):
        rect(ctx, x + k * (w / 2 - 20) - 10, y + 70, 20, 90, "#a06c44", lw)


def moon(ctx, x, y, r=70):
    oval(ctx, x, y, r, r, "#f6f0c8", lw_at(ctx, r * 3))
    oval(ctx, x + r * 0.45, y - r * 0.2, r * 0.85, r * 0.85, "#363a5e", 0.001)


# ---------------------------------------------------------------- kitchen / apple props (apple story)
APPLE_RED, APPLE_FLESH = "#e2483a", "#f6e7a6"


def apple(ctx, x, y, r=60, peeled=0.0, rot=0.0, leaf=True, bite=False):
    """Apple centred at (x, y). peeled 0..1 turns it into pale flesh from the top down with a
    spiral cut line (after the peeler); bite=True takes a round bite out of the right side."""
    lw = lw_at(ctx, r * 2)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)

    def body():
        ctx.new_path()
        ctx.move_to(0, -0.72 * r)
        ctx.curve_to(0.5 * r, -1.1 * r, 1.12 * r, -0.62 * r, 1.0 * r, 0.05 * r)
        ctx.curve_to(0.92 * r, 0.7 * r, 0.45 * r, 1.0 * r, 0, 0.88 * r)
        ctx.curve_to(-0.45 * r, 1.0 * r, -0.92 * r, 0.7 * r, -1.0 * r, 0.05 * r)
        ctx.curve_to(-1.12 * r, -0.62 * r, -0.5 * r, -1.1 * r, 0, -0.72 * r)
        ctx.close_path()
    if bite:
        ctx.save()
        ctx.arc(1.0 * r, 0.0, 0.42 * r, 0, 2 * PI)
        ctx.rectangle(-3 * r, -3 * r, 6 * r, 6 * r)
        ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        ctx.clip()
    body()
    fill_ink(ctx, hexc(APPLE_RED), lw)
    if peeled > 0:
        ctx.save()
        body()
        ctx.clip()
        ctx.rectangle(-1.3 * r, -1.2 * r, 2.6 * r, 2.3 * r * peeled)
        _fill(ctx, hexc(APPLE_FLESH))
        ctx.fill()
        for k in range(int(9 * peeled) + 1):       # the spiral cut line
            yy = -0.8 * r + k * 0.22 * r
            ctx.move_to(-1.1 * r, yy + 0.08 * r)
            ctx.line_to(1.1 * r, yy - 0.08 * r)
        _ink(ctx, lw * 0.6, hexc("#c9a85a"))
        ctx.restore()
        body()
        _ink(ctx, lw)
    if bite:
        ctx.restore()
        ctx.new_sub_path()
        ctx.arc(1.0 * r, 0.0, 0.42 * r, PI * 0.55, PI * 1.45)
        _ink(ctx, lw)
    poly(ctx, [(0, -0.72 * r), (0.08 * r, -1.08 * r)], hexc("#6a4a2e"), lw * 1.6, close=False)
    if leaf:
        oval(ctx, 0.32 * r, -1.0 * r, 0.24 * r, 0.1 * r, "#5aa878", lw, rot=-0.5)
    ctx.restore()


def apple_chunks(ctx, x, y, s=1.0, seed=4):
    """Badly hacked apple pieces on a board (someone who sucks at slicing fruit)."""
    lw = lw_at(ctx, 96 * s)
    u = 96 * s
    rect(ctx, x - 1.8 * u, y - 0.15 * u, 3.6 * u, 0.3 * u, "#d8b07a", lw, r=0.08 * u)
    rnd = random.Random(seed)
    for k in range(7):
        cx, cy = x + rnd.uniform(-1.5, 1.5) * u, y - 0.3 * u - rnd.uniform(0, 0.25) * u
        rr = rnd.uniform(0.15, 0.32) * u
        a = rnd.uniform(0, PI)
        pts = [(cx + math.cos(a + j * 2.0) * rr * rnd.uniform(0.7, 1.2), cy + math.sin(a + j * 2.0) * rr * 0.8)
               for j in range(3)]
        poly(ctx, pts, APPLE_FLESH, lw)
        poly(ctx, [pts[0], pts[1]], APPLE_RED, lw * 2.2, close=False)


def knife(ctx, x, y, s=1.0, rot=0.0):
    """Kitchen knife, handle end at (x, y)."""
    lw = lw_at(ctx, 96 * s)
    u = 96 * s
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    rect(ctx, -0.2 * u, -0.1 * u, 0.9 * u, 0.2 * u, "#3a2a22", lw, r=0.06 * u)
    poly(ctx, [(0.7 * u, -0.14 * u), (2.1 * u, -0.14 * u), (2.4 * u, 0.0), (0.7 * u, 0.16 * u)], "#d8dde2", lw)
    ctx.restore()


def peeler(ctx, x, y, s=1.0, crank=0.0, apple_on=1.0, blade=0.0, peeled=0.0, speed=0.0, ribbon=0.0):
    """Crank apple peeler seen from the side, base centre at (x, y) on the table.
    crank: handle angle (radians); apple_on 0..1 slides the apple onto the prongs;
    blade 0 = blade arm swung away, 1 = snapped onto the apple; peeled 0..1;
    speed 0..1 draws spin lines; ribbon 0..1 lets a red peel ribbon spill out."""
    lw = lw_at(ctx, 96 * s)
    u = 96 * s
    metal, dark = "#b8bec6", "#6a6e76"
    # base clamp + post
    rect(ctx, x - 1.5 * u, y - 0.25 * u, 1.3 * u, 0.25 * u, dark, lw, r=0.08 * u)
    rect(ctx, x - 1.0 * u, y - 1.9 * u, 0.3 * u, 1.65 * u, metal, lw)
    ry = y - 1.75 * u                                  # the rod height
    rect(ctx, x - 1.6 * u, ry - 0.07 * u, 3.2 * u, 0.14 * u, metal, lw)      # threaded rod
    for k in range(12):
        xx = x - 1.5 * u + k * 0.26 * u
        poly(ctx, [(xx, ry - 0.07 * u), (xx + 0.1 * u, ry + 0.07 * u)], INK, lw * 0.5, close=False)
    # crank handle on the left (rotates)
    cx0 = x - 1.65 * u
    hx, hy = cx0 + math.cos(crank) * 0.0, ry + math.sin(crank) * 0.75 * u
    bar(ctx, (cx0, ry), (hx, hy), dark, 0.09 * u)
    rect(ctx, hx - 0.45 * u, hy - 0.11 * u, 0.45 * u, 0.22 * u, "#c0392b", lw, r=0.1 * u)
    # prongs + apple on the right
    px = x + 1.6 * u
    for k in (-1, 0, 1):
        bar(ctx, (px, ry + k * 0.08 * u), (px + 0.35 * u, ry + k * 0.16 * u), metal, 0.05 * u)
    ax = px + 0.6 * u + (1 - apple_on) * 1.6 * u
    if apple_on > 0:
        apple(ctx, ax, ry, 0.62 * u, peeled=peeled, rot=crank * 0.15 if speed < 0.5 else 0.0, leaf=peeled < 0.1)
        if speed > 0:
            for k in range(3):
                a0 = crank + k * 2.1
                ctx.new_sub_path()
                ctx.arc(ax, ry, 0.85 * u, a0, a0 + 0.9 * speed)
                _ink(ctx, lw * 1.2)
    # blade arm: pivots under the apple, swings up onto its side
    pvx, pvy = px + 0.1 * u, y - 0.25 * u
    a = lerp_angle(-2.2, -1.25, blade)
    bx, by = pvx + math.cos(a) * 1.25 * u, pvy + math.sin(a) * 1.25 * u
    bar(ctx, (pvx, pvy), (bx, by), metal, 0.11 * u)
    rect(ctx, bx - 0.12 * u, by - 0.2 * u, 0.24 * u, 0.4 * u, "#d8dde2", lw)
    if ribbon > 0:                                     # red peel ribbon curling down off the apple
        ctx.move_to(ax + 0.5 * u, ry + 0.2 * u)
        for k in range(int(30 * ribbon) + 2):
            tt = k / 30
            ctx.line_to(ax + 0.6 * u + math.sin(tt * 18) * 0.35 * u + tt * 0.6 * u, ry + 0.3 * u + tt * 3.2 * u)
        _ink(ctx, 0.16 * u, hexc(APPLE_RED))


def lerp_angle(a, b, t):
    return a + (b - a) * max(0.0, min(1.0, t))


def saturn(ctx, x, y, r=170, col="#f0c84a"):
    """Yellow planet with a ring (the peeled apple 'looks like Saturn')."""
    lw = lw_at(ctx, r * 2)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(-0.3)
    ctx.save()
    ctx.scale(1, 0.28)
    ctx.arc(0, 0, r * 1.75, PI, 2 * PI)
    ctx.restore()
    _ink(ctx, r * 0.16, hexc("#c99a3a"))
    oval(ctx, 0, 0, r, r, col, lw)
    for k in (-0.4, 0.05, 0.45):
        ctx.save()
        ctx.arc(0, 0, r, 0, 2 * PI)
        ctx.clip()
        poly(ctx, [(-r, k * r), (r, k * r + 0.08 * r)], hexc("#d9a83a"), r * 0.12, close=False)
        ctx.restore()
    ctx.save()
    ctx.scale(1, 0.28)
    ctx.arc(0, 0, r * 1.75, 0, PI)
    ctx.restore()
    _ink(ctx, r * 0.16, hexc("#c99a3a"))
    ctx.restore()


def stars_field(ctx, seed=2, n=40):
    rnd = random.Random(seed)
    for _ in range(n):
        sparkle(ctx, rnd.uniform(20, W - 20), rnd.uniform(60, H - 60), rnd.uniform(5, 13), "#fff6c8")


def stopwatch(ctx, x, y, r=200, seconds=5.0, label=None):
    """Stopwatch with a sweeping hand; label is the big digital readout (default 0:0N)."""
    lw = lw_at(ctx, r * 2)
    rect(ctx, x - 0.18 * r, y - 1.32 * r, 0.36 * r, 0.25 * r, "#8a8a8a", lw, r=0.05 * r)
    oval(ctx, x, y, 1.08 * r, 1.08 * r, "#8a8a8a", lw)
    oval(ctx, x, y, 0.95 * r, 0.95 * r, "#ffffff", lw)
    for k in range(12):
        a = k * PI / 6
        poly(ctx, [(x + math.cos(a) * 0.8 * r, y + math.sin(a) * 0.8 * r),
                   (x + math.cos(a) * 0.9 * r, y + math.sin(a) * 0.9 * r)], INK, lw, close=False)
    a = -PI / 2 + seconds / 60 * 2 * PI
    poly(ctx, [(x, y), (x + math.cos(a) * 0.78 * r, y + math.sin(a) * 0.78 * r)], hexc("#d8322a"), lw * 2.2,
         close=False)
    oval(ctx, x, y, 0.06 * r, 0.06 * r, INK, 0.001)
    rect(ctx, x - 0.45 * r, y + 0.25 * r, 0.9 * r, 0.32 * r, "#202428", lw, r=0.04 * r)
    scrawl(ctx, label or f"0:{int(seconds):02d}", x, y + 0.41 * r, 0.24 * r, hexc("#7cf08a"))


def test_paper(ctx, x, y, s=1.0, grade="F", rot=-0.06):
    """School test sheet with a big red grade."""
    lw = lw_at(ctx, 96 * s)
    u = 96 * s
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    rect(ctx, -1.5 * u, -2.0 * u, 3.0 * u, 4.0 * u, "#fbf7ee", lw)
    for k in range(9):
        yy = -1.2 * u + k * 0.36 * u
        poly(ctx, [(-1.2 * u, yy), (0.6 * u if k % 3 else 1.2 * u, yy)], hexc("#9ab0d0"), lw * 0.8, close=False)
        poly(ctx, [(0.85 * u, yy - 0.1 * u), (1.0 * u, yy + 0.05 * u), (1.15 * u, yy - 0.15 * u)],
             hexc("#d8322a"), lw, close=False)
    ctx.new_sub_path()
    ctx.arc(0.75 * u, -1.35 * u, 0.55 * u, 0, 2 * PI)
    _ink(ctx, lw * 2.0, hexc("#d8322a"))
    scrawl(ctx, grade, 0.75 * u, -1.38 * u, 0.8 * u, hexc("#d8322a"))
    ctx.restore()


def gift_box(ctx, x, y, s=1.0, open_=0.0, col="#e2604e", ribbon="#f0c814"):
    """Wrapped present, bottom centre at (x, y); open_ lifts the lid."""
    lw = lw_at(ctx, 96 * s)
    u = 96 * s
    rect(ctx, x - 0.8 * u, y - 1.2 * u, 1.6 * u, 1.2 * u, col, lw)
    rect(ctx, x - 0.12 * u, y - 1.2 * u, 0.24 * u, 1.2 * u, ribbon, lw)
    ly = y - 1.2 * u - open_ * 0.8 * u
    rect(ctx, x - 0.9 * u, ly - 0.3 * u, 1.8 * u, 0.3 * u, col, lw)
    rect(ctx, x - 0.12 * u, ly - 0.3 * u, 0.24 * u, 0.3 * u, ribbon, lw)
    for k in (-1, 1):
        oval(ctx, x + k * 0.25 * u, ly - 0.42 * u, 0.25 * u, 0.13 * u, ribbon, lw, rot=k * 0.4)


def question(ctx, x, y, size=160, col="#ffffff", rot=0.12):
    """Big comic question mark with an ink outline."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    e = ctx.text_extents("?")
    ctx.move_to(-e.width / 2 - e.x_bearing, e.height / 2)
    ctx.text_path("?")
    _fill(ctx, hexc(col) if isinstance(col, str) else col)
    ctx.fill_preserve()
    _ink(ctx, lw_at(ctx, size) * 1.3)
    ctx.restore()


def speed_lines(ctx, x, y, r, n=10, seed=1):
    rnd = random.Random(seed)
    lw = lw_at(ctx, r)
    for k in range(n):
        a = k * 2 * PI / n + rnd.uniform(-0.1, 0.1)
        r0 = r * rnd.uniform(1.05, 1.2)
        poly(ctx, [(x + math.cos(a) * r0, y + math.sin(a) * r0),
                   (x + math.cos(a) * r0 * 1.45, y + math.sin(a) * r0 * 1.45)], INK, lw * 1.4, close=False)


def kitchen(ctx, back="#fed68e", side="#f2c27e", floor="#b07a58", counter_y=900, counter="#e9e3d8"):
    """Kitchen: one-point box room with a cupboard row and a counter across the bottom
    (characters stand behind it, the counter hides their legs)."""
    room_box(ctx, back=back, side=side, floor=floor, rug=None, door=False, shelf=False)
    lw = lw_at(ctx, 140)
    for k in range(3):
        rect(ctx, 195 + k * 112, 345, 104, 120, "#ffffff", lw, r=6)
        oval(ctx, 290 + k * 112, 405, 6, 6, INK, 0.001)


def counter_front(ctx, y=900, col="#e9e3d8", top="#c9c2b6"):
    lw = lw_at(ctx, 140)
    rect(ctx, -300, y, W + 600, 40, top, lw)
    rect(ctx, -300, y + 40, W + 600, 600, col, lw)
    for k in range(4):
        rect(ctx, 40 + k * 170, y + 80, 150, 260, col, lw, r=8)


# ---------------------------------------------------------------- Halloween props (halloween story)
def pumpkin(ctx, x, y, r=60, face=True, lit=True):
    """Jack-o'-lantern, centre at (x, y)."""
    lw = lw_at(ctx, r * 2)
    for k, (dx, w) in enumerate(((-0.45, 0.62), (0.45, 0.62), (0.0, 0.7))):
        oval(ctx, x + dx * r, y, w * r, 0.85 * r, "#f08a24" if k < 2 else "#f59a32", lw)
    rect(ctx, x - 0.1 * r, y - 1.05 * r, 0.2 * r, 0.3 * r, "#5c7a2e", lw, r=0.05 * r)
    if face:
        glow = "#ffd84a" if lit else "#3a2a22"
        for k in (-1, 1):
            poly(ctx, [(x + k * 0.38 * r, y - 0.35 * r), (x + k * 0.18 * r, y - 0.05 * r),
                       (x + k * 0.58 * r, y - 0.05 * r)], glow, lw)
        poly(ctx, [(x - 0.55 * r, y + 0.2 * r), (x - 0.3 * r, y + 0.42 * r), (x - 0.1 * r, y + 0.28 * r),
                   (x + 0.1 * r, y + 0.45 * r), (x + 0.32 * r, y + 0.28 * r), (x + 0.55 * r, y + 0.2 * r),
                   (x + 0.3 * r, y + 0.6 * r), (x - 0.3 * r, y + 0.6 * r)], glow, lw)


def witch_hat(ctx, cx, top, U, col="#3a2a4a", band="#8a5ad8"):
    lw = lw_at(ctx, U)
    oval(ctx, cx, top + 0.02 * U, 0.75 * U, 0.12 * U, col, lw)
    poly(ctx, [(cx - 0.42 * U, top), (cx + 0.1 * U, top - 1.1 * U), (cx + 0.38 * U, top - 0.95 * U),
               (cx + 0.42 * U, top)], col, lw)
    rect(ctx, cx - 0.41 * U, top - 0.16 * U, 0.82 * U, 0.14 * U, band, lw)


def cat_ears(ctx, cx, top, U, col="#2e2e30", inner="#f2a0b4"):
    lw = lw_at(ctx, U)
    for k in (-1, 1):
        poly(ctx, [(cx + k * 0.42 * U, top + 0.04 * U), (cx + k * 0.36 * U, top - 0.36 * U),
                   (cx + k * 0.12 * U, top + 0.04 * U)], col, lw)
        poly(ctx, [(cx + k * 0.36 * U, top), (cx + k * 0.33 * U, top - 0.22 * U), (cx + k * 0.2 * U, top)], inner, lw)


def cape(ctx, cx, top, U, length=3.0, col="#1c1a24", lining="#b8222a", spread=1.0):
    """Vampire cape BEHIND a character (call before drawing it): wide from the shoulders down."""
    lw = lw_at(ctx, U)
    sh = top + 0.9 * U
    ctx.move_to(cx - 0.5 * U, sh)
    ctx.curve_to(cx - 1.2 * spread * U, sh + 1.0 * U, cx - 1.3 * spread * U, sh + 2.2 * U,
                 cx - 1.0 * spread * U, sh + length * U)
    for k in range(5):     # scalloped hem
        xa = cx - 1.0 * spread * U + (k + 0.5) * 0.4 * spread * U
        ctx.line_to(xa, sh + (length - 0.25) * U)
        ctx.line_to(xa + 0.2 * spread * U, sh + length * U)
    ctx.curve_to(cx + 1.3 * spread * U, sh + 2.2 * U, cx + 1.2 * spread * U, sh + 1.0 * U, cx + 0.5 * U, sh)
    ctx.close_path()
    fill_ink(ctx, hexc(lining), lw)
    ctx.move_to(cx - 0.5 * U, sh)
    ctx.curve_to(cx - 1.0 * spread * U, sh + 1.0 * U, cx - 1.1 * spread * U, sh + 2.0 * U,
                 cx - 0.85 * spread * U, sh + (length - 0.1) * U)
    ctx.line_to(cx + 0.85 * spread * U, sh + (length - 0.1) * U)
    ctx.curve_to(cx + 1.1 * spread * U, sh + 2.0 * U, cx + 1.0 * spread * U, sh + 1.0 * U, cx + 0.5 * U, sh)
    ctx.close_path()
    fill_ink(ctx, hexc(col), lw)


def cape_collar(ctx, cx, bottom, U, col="#1c1a24", lining="#b8222a"):
    """High pointed collar standing up beside the head (call after drawing the character)."""
    lw = lw_at(ctx, U)
    for k in (-1, 1):
        poly(ctx, [(cx + k * 0.45 * U, bottom + 0.05 * U), (cx + k * 0.95 * U, bottom - 0.55 * U),
                   (cx + k * 0.6 * U, bottom + 0.25 * U)], lining, lw)
        poly(ctx, [(cx + k * 0.6 * U, bottom + 0.25 * U), (cx + k * 0.95 * U, bottom - 0.55 * U),
                   (cx + k * 1.0 * U, bottom + 0.3 * U)], col, lw)


def fangs(ctx, cx, my, U):
    """Two white fangs under the mouth line (draw after the face; my = mouth y)."""
    lw = lw_at(ctx, U)
    for k in (-1, 1):
        poly(ctx, [(cx + k * 0.07 * U, my), (cx + k * 0.035 * U, my + 0.09 * U), (cx + k * 0.0 * U, my)],
             "#ffffff", lw * 0.8)


def ghost(ctx, x, y, s=1.0, T=0.0):
    """Kid under a white sheet with eye holes, bottom centre at (x, y)."""
    lw = lw_at(ctx, 96 * s)
    u = 96 * s
    ctx.move_to(x - 0.7 * u, y)
    ctx.curve_to(x - 0.8 * u, y - 1.6 * u, x - 0.6 * u, y - 2.6 * u, x, y - 2.6 * u)
    ctx.curve_to(x + 0.6 * u, y - 2.6 * u, x + 0.8 * u, y - 1.6 * u, x + 0.7 * u, y)
    for k in range(4):
        xa = x + 0.7 * u - (k + 0.5) * 0.35 * u
        ctx.line_to(xa, y - (0.12 if k % 2 else 0.0) * u - 0.1 * u)
        ctx.line_to(xa - 0.175 * u, y)
    ctx.close_path()
    fill_ink(ctx, hexc("#f6f6f2"), lw)
    for k in (-1, 1):
        oval(ctx, x + k * 0.22 * u, y - 1.95 * u, 0.1 * u, 0.15 * u, "#1c1a24", lw * 0.6)


def candy_bowl(ctx, x, y, s=1.0, full=1.0, seed=7):
    """Bowl of wrapped candy, bowl rim centre at (x, y); full 0..1."""
    lw = lw_at(ctx, 96 * s)
    u = 96 * s
    rnd = random.Random(seed)
    cols = ["#e2483a", "#f0c814", "#7e54ae", "#3aa8a0", "#f08a24", "#9cb41e"]
    for k in range(int(14 * full)):
        cx, cy = x + rnd.uniform(-1.05, 1.05) * u, y - rnd.uniform(0.0, 0.45) * u
        a = rnd.uniform(-0.6, 0.6)
        c = cols[k % len(cols)]
        ctx.save()
        ctx.translate(cx, cy)
        ctx.rotate(a)
        for e in (-1, 1):
            poly(ctx, [(e * 0.16 * u, 0), (e * 0.3 * u, -0.1 * u), (e * 0.3 * u, 0.1 * u)], c, lw * 0.8)
        oval(ctx, 0, 0, 0.18 * u, 0.12 * u, c, lw * 0.8)
        ctx.restore()
    ctx.move_to(x - 1.3 * u, y)
    ctx.curve_to(x - 1.2 * u, y + 1.0 * u, x + 1.2 * u, y + 1.0 * u, x + 1.3 * u, y)
    ctx.close_path()
    fill_ink(ctx, hexc("#f08a24"), lw)
    oval(ctx, x, y, 1.3 * u, 0.12 * u, "#f59a32", lw)


def sign(ctx, x, y, w, h, lines, col="#fbf7ee", ink="#1c1a24", rot=0.0, size=None):
    """Hand-written cardboard sign (e.g. PLEASE TAKE 1)."""
    lw = lw_at(ctx, w * 0.4)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    rect(ctx, -w / 2, -h / 2, w, h, col, lw)
    size = size or h / (len(lines) + 0.8)
    for k, ln in enumerate(lines):
        scrawl(ctx, ln, 0, -h / 2 + size * (k + 0.95), size * 0.8, hexc(ink), 0.0)
    ctx.restore()


def bucket(ctx, x, y, s=1.0):
    """Pumpkin trick-or-treat bucket, centre at (x, y), handle on top."""
    u = 96 * s
    ctx.new_sub_path()
    ctx.arc(x, y - 0.3 * u, 0.55 * u, PI, 2 * PI)
    _ink(ctx, lw_at(ctx, u) * 1.5)
    pumpkin(ctx, x, y + 0.2 * u, 0.5 * u)


def night_street(ctx, T=0.0, sky="#2e2a4a", ground="#3a3550"):
    """Flat night street: moon, a row of simple houses with lit windows, pumpkins on the steps."""
    lw = lw_at(ctx, 150)
    bg(ctx, sky)
    stars_field(ctx, seed=5, n=18)
    moon(ctx, 560, 260, 70)
    for k, (x, w, h, col, roof) in enumerate(((60, 230, 300, "#5a4e74", "#2a2236"), (300, 200, 360, "#4e5a74", "#22283a"),
                                             (510, 250, 280, "#6a4e5e", "#30222a"))):
        rect(ctx, x, 880 - h, w, h, col, lw)
        poly(ctx, [(x - 20, 880 - h), (x + w / 2, 880 - h - 110), (x + w + 20, 880 - h)], roof, lw)
        for j in range(2):
            rect(ctx, x + 30 + j * (w - 100), 880 - h + 60, 60, 70, "#ffd84a", lw)
    rect(ctx, -300, 880, W + 600, 700, ground, lw)


# ---------------------------------------------------------------- effect marks
def sparkle(ctx, x, y, r, col="#f0c814", rot=0.0):
    """4-point star (glint on a new object, joy stars around a happy face)."""
    if r <= 0:
        return
    lw = lw_at(ctx, r * 3)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    pts = []
    for k in range(8):
        a = k * PI / 4
        rr = r if k % 2 == 0 else r * 0.22
        pts.append((math.cos(a) * rr, math.sin(a) * rr))
    poly(ctx, pts, col, lw * 0.8)
    ctx.restore()


def swear(ctx, x, y, s=1.0, T=0.0):
    """Cursing scribble: spiral, '!', '#', jagged line (monitor ref 0.8 s)."""
    u = 40 * s
    lw = lw_at(ctx, 120 * s)
    ctx.new_sub_path()
    for k in range(60):
        a = k * 0.35
        r = 0.05 * u + k * 0.012 * u
        ctx.line_to(x + math.cos(a) * r, y + math.sin(a) * r)
    _ink(ctx, lw)
    scrawl(ctx, "!", x + 0.9 * u, y - 0.4 * u, 1.4 * u, hexc("#f0c814"))
    scrawl(ctx, "#", x + 0.2 * u, y + 1.2 * u, 1.2 * u, INK, 0.2)
    pts = [(x + 1.4 * u, y + 0.9 * u)]
    for k in range(5):
        pts.append((x + 1.6 * u + k * 0.4 * u, y + 0.9 * u + (0.35 if k % 2 else -0.35) * u))
    poly(ctx, pts, INK, lw, close=False)


def impact(ctx, x, y, s=1.0, col="#d8322a"):
    """Short red strokes radiating from a hit (knock, window ref 18.3 s)."""
    lw = lw_at(ctx, 96 * s) * 1.6
    u = 96 * s
    for a in (-2.6, -2.2, -0.9, -0.5, 2.5):
        ctx.move_to(x + math.cos(a) * 0.55 * u, y + math.sin(a) * 0.55 * u)
        ctx.line_to(x + math.cos(a) * 0.9 * u, y + math.sin(a) * 0.9 * u)
        _ink(ctx, lw, hexc(col))


def stress(ctx, x, y, s=1.0):
    """Worry arcs above a head (monitor ref 16.8 s)."""
    lw = lw_at(ctx, 96 * s)
    u = 96 * s
    for dx, a0 in ((-0.35, 0.2), (0.15, -0.2)):
        ctx.new_sub_path()
        ctx.arc(x + dx * u, y + 0.3 * u, 0.35 * u, PI + 0.9 + a0, PI + 2.0 + a0)
        _ink(ctx, lw)


def tear(ctx, x, y, s=1.0):
    u = 96 * s
    lw = lw_at(ctx, u)
    ctx.move_to(x, y - 0.12 * u)
    ctx.curve_to(x + 0.08 * u, y, x + 0.07 * u, y + 0.08 * u, x, y + 0.08 * u)
    ctx.curve_to(x - 0.07 * u, y + 0.08 * u, x - 0.08 * u, y, x, y - 0.12 * u)
    fill_ink(ctx, TEAR, lw)


def gloom(ctx, cx, top, U, hh):
    """Grey shame shadow over the top of a head (monitor ref 24.3 s). Call after the char."""
    lw = lw_at(ctx, U)
    ctx.move_to(cx - 0.5 * U, top - 0.02 * U)
    ctx.line_to(cx + 0.5 * U, top - 0.02 * U)
    ctx.line_to(cx + 0.48 * U, top + 0.5 * hh)
    ctx.curve_to(cx + 0.2 * U, top + 0.42 * hh, cx - 0.2 * U, top + 0.58 * hh, cx - 0.48 * U, top + 0.5 * hh)
    ctx.close_path()
    fill_ink(ctx, hexc("#8c8880"), lw)


# ---------------------------------------------------------------- items held in a hand (BoxChar item=...)
def draw_item(ctx, item, x, y, U, t, side):
    s = U / 96
    if callable(item):
        item(ctx, x, y, s, t, side)
    elif item == "hammer":
        hammer(ctx, x, y, s * 0.5, rot=-PI / 2 + side * 0.25)
    elif item == "hammer_side":
        hammer(ctx, x - side * 0.15 * U, y, s * 0.5, rot=0 if side > 0 else PI)
    elif item == "phone":
        phone(ctx, x, y - 0.35 * U, s * 0.55)
    elif item == "bat":
        bat(ctx, x, y, s, rot=-PI / 2 + side * 0.3)
    elif item == "balloons":
        balloons(ctx, x, y, s * 0.8, t)
    elif item == "teddy":
        teddy(ctx, x, y + 0.25 * U, s * 0.55)
    elif item == "box":
        cardboard_box(ctx, x - side * 0.3 * U, y + 0.5 * U, s * 0.55)
    elif item == "apple":
        apple(ctx, x, y - 0.1 * U, 0.3 * U)
    elif item == "spiral_apple":
        apple(ctx, x, y - 0.25 * U, 0.38 * U, peeled=1.0, leaf=False)
    elif item == "knife":
        knife(ctx, x, y, s * 0.6, rot=-PI / 2 - side * 0.5)
    elif item == "gift":
        gift_box(ctx, x - side * 0.1 * U, y + 0.35 * U, s * 0.55)
    elif item == "bucket":
        bucket(ctx, x, y + 0.45 * U, s * 0.6)
    elif item == "ball":
        ball(ctx, x, y + 0.2 * U, 0.3 * U)
    else:
        raise ValueError(f"unknown item {item}")
