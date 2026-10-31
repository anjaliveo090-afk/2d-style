"""The references' camera angles, measured shot by shot (visual_grammar.md section 2),
as placement helpers. The camera itself never moves in this style: a shot IS its angle.
Every helper returns where to draw in the 720x1280 world with a static camera
(cam(start) keys), so a story picks an angle per phrase and draws the character there.

Measured on the 56 reference shots (head width = % of frame width, from the largest skin
box per shot plus the 4 fps contact sheets):

| angle      | share | framing                                                             |
|------------|-------|---------------------------------------------------------------------|
| face       | 22%   | chest-up, frontal, head 55-75% wide, head top at y 180-300          |
| extreme    | 11%   | one feature fills the frame: eye, cheek, fist, head from above      |
| full       | 13%   | whole figure on a flat colour, height 45-70% of frame, centred       |
| two        | 5%    | tall adult + small kid, both whole, adult often cut by the edge      |
| ots        | 5%    | over the shoulder: back of a head/shoulder big in a bottom corner    |
| insert     | 14%   | one prop fills the frame (socket, monitor, calendar, window, fist)   |
| wide       | 14%   | minimal set (box room, bunk bed), heads only 7-11% wide              |
| bed        | 6%    | lying on a pillow, head tilted ~30 deg, 44-48% wide, body under cover |
| scenery    | 4%    | sunset / sky, no character                                          |
| low / top  | 6%    | from below a bunk, top-down onto a raised hammer                     |
"""
from engine import W, H

ANGLE_MIX = {"face": 0.22, "extreme": 0.11, "full": 0.13, "two": 0.05, "ots": 0.05, "insert": 0.14,
             "wide": 0.14, "bed": 0.06, "scenery": 0.04, "low": 0.06}
C = (W / 2, H / 2)


def cam(start, z=1.0, c=C):
    """Static camera key list for a shot (the references never pan or push)."""
    return [(start, z, c)]


def face(ch, ctx, expr, t, width=0.62, top=0.2, dx=0.0, **kw):
    """Chest-up close-up: head `width` of the frame wide, head top at `top` of the frame height.
    Reference: 55-75% wide, top at 14-23%. Body runs off the bottom edge."""
    return ch.draw_close(ctx, W / 2 + dx * W, top * H, width * W, expr, t, **kw)


def extreme(ch, ctx, expr, t, width=1.1, top=0.1, dx=0.0, **kw):
    """Extreme close-up: the head is wider than the frame (only the face features show)."""
    return ch.draw_close(ctx, W / 2 + dx * W, top * H, width * W, expr, t, **kw)


def full_size(ch, height=0.6):
    """Size s that makes a standing character `height` of the frame tall."""
    b = ch.b
    return height * H / ((b["head_h"] + b["torso"] + b["leg"] - 0.05) * 96 * b["hw"])


def full(ch, ctx, expr, t, height=0.58, x=0.5, feet=0.78, **kw):
    """Whole figure on a flat colour: `height` of the frame tall, feet at `feet` of the frame
    (inside the Shorts safe zone: head top >= y 149, feet <= y 1013)."""
    s = full_size(ch, height)
    ch.draw(ctx, x * W, feet * H, s, expr, t, **kw)
    return s


def two(adult, kid, ctx, t, a_expr, k_expr, a_kw=None, k_kw=None, height=0.62):
    """Confrontation two-shot: tall adult left of centre, the kid smaller to the right
    (monitor ref 9.2 s / 11.6 s)."""
    s = full_size(adult, height)
    adult.draw(ctx, 0.36 * W, 0.79 * H, s, a_expr, t, **(a_kw or {}))
    kid.draw(ctx, 0.7 * W, 0.79 * H, s * 0.95, k_expr, t, **(k_kw or {}))
    return s


def ots(front, back, ctx, t, f_expr, f_kw=None, side=-1, f_height=0.42):
    """Over the shoulder: `back` seen from behind, big, cut by the bottom corner on `side`
    (-1 = left); `front` whole and smaller in the middle (monitor ref 7.8 s)."""
    s = full_size(front, f_height)
    front.draw(ctx, (0.5 - side * 0.12) * W, 0.66 * H, s, f_expr, t, **(f_kw or {}))
    back.draw_close(ctx, (0.5 + side * 0.3) * W, 0.6 * H, 0.62 * W, "neutral", t, pose="back")


def bed(ch, ctx, expr, t, sets, rot=0.5, width=0.46, **kw):
    """Lying in bed, tilted head on the pillow (window refs 0.0 / 26.6 / 30.7 s)."""
    s = width * W / (96 * ch.b["hw"])
    sets.in_bed(ctx, ch, 0.52 * W, 0.47 * H, s, expr, t, rot=rot, **kw)
    return s
