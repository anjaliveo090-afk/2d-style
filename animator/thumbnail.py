"""High-CTR thumbnails in the box-head style, drawn with the story's own characters:
1080x1920 (Shorts) and 1280x720 (search / suggested). Template: the sample story (sample.py).
Recipe: one huge emotional face, a clear opponent, 2-3 word text, bright burst behind,
white sticker outlines so everything pops, nothing important at the edges.
The video style itself has no white outline: --no-stroke gives a flat version closer to it.
Usage: python3 thumbnail.py out_dir [--no-stroke]
For a new story: change HEADLINE, the face character/expression and the opponent drawing."""
import math
import sys
from pathlib import Path

import cairo
import cv2
import numpy as np

import sets as st
from engine import hexc
from style import DAD, GIRL

HEADLINE = ("MY TEDDY", "IS GONE?!")
FONT = "Inter Display Black"
SUFFIX = ""


def surface(w, h):
    return cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)


def burst(ctx, w, h, cx, cy):
    g = cairo.RadialGradient(cx, cy, 0, cx, cy, max(w, h) * 0.9)
    g.add_color_stop_rgb(0, *hexc("#fff3a8"))
    g.add_color_stop_rgb(0.35, *hexc("#ffb347"))
    g.add_color_stop_rgb(1, *hexc("#e8433a"))
    ctx.set_source(g)
    ctx.paint()
    for k in range(18):
        a = k * math.pi / 9
        ctx.move_to(cx, cy)
        ctx.line_to(cx + math.cos(a) * 3000, cy + math.sin(a) * 3000)
        ctx.line_to(cx + math.cos(a + 0.09) * 3000, cy + math.sin(a + 0.09) * 3000)
        ctx.close_path()
    ctx.set_source_rgba(1, 1, 1, 0.16)
    ctx.fill()


STROKE = True   # white sticker outline around characters/props (False = no outline, only a soft shadow)


def sticker(dst_ctx, w, h, draw, outline=14, shadow=(10, 14)):
    """Draw `draw(ctx)` on its own layer, add a white outline + soft shadow, composite."""
    lay = surface(w, h)
    draw(cairo.Context(lay))
    lay.flush()
    a = np.ndarray((h, w, 4), np.uint8, lay.get_data())
    alpha = a[:, :, 3]
    if not STROKE:
        outline = 0
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * outline + 1, 2 * outline + 1))
    ring = cv2.dilate(alpha, k)
    sh = cv2.GaussianBlur(ring, (0, 0), 10)
    dx, dy = shadow
    sh = np.pad(sh, ((dy, 0), (dx, 0)))[:h, :w]           # shift down-right, no wrap-around
    base = np.zeros((h, w, 4), np.uint8)
    base[:, :, 3] = (sh * 0.45).astype(np.uint8)          # premultiplied black shadow
    ws = surface(w, h)
    wa = np.ndarray((h, w, 4), np.uint8, ws.get_data())
    wa[:] = base
    white = ring.astype(np.float32) / 255
    if STROKE:
        for c in range(3):
            wa[:, :, c] = np.clip(wa[:, :, c] * (1 - white) + 255 * white, 0, 255).astype(np.uint8)
        wa[:, :, 3] = np.maximum(wa[:, :, 3], ring)
    ws.mark_dirty()
    dst_ctx.set_source_surface(ws, 0, 0)
    dst_ctx.paint()
    dst_ctx.set_source_surface(lay, 0, 0)
    dst_ctx.paint()


def big_text(ctx, s, x, y, size, fill, tilt=0.0, stroke=0.16):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(tilt)
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    e = ctx.text_extents(s)
    ox, oy = -e.width / 2 - e.x_bearing, -e.height / 2 - e.y_bearing
    ctx.move_to(ox + size * 0.06, oy + size * 0.08)    # hard drop shadow
    ctx.text_path(s)
    ctx.set_source_rgba(0, 0, 0, 0.55)
    ctx.fill()
    ctx.move_to(ox, oy)
    ctx.text_path(s)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_source_rgb(0.08, 0.06, 0.1)
    ctx.set_line_width(size * stroke)
    ctx.stroke_preserve()
    ctx.set_source_rgb(*hexc(fill))
    ctx.fill()
    ctx.restore()
    return e.width


def fit_text(ctx, s, max_w, size):
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    return min(size, size * max_w / max(1, ctx.text_extents(s).width))


def face_sticker(ctx, cx, top, width, expr="cry"):
    """The huge emotional face (head + shoulders) of the main character."""
    GIRL.draw_close(ctx, cx, top, width, expr, 0.0, bob=0)


def opponent(ctx, x, y, s):
    """The opponent: dad holding the teddy over the bin, stern."""
    st.trash_bin(ctx, x + 1.25 * 96 * s, y, s * 0.55, lid=1.0)
    DAD.draw(ctx, x, y, s, "stern", 0.0, arms=("hip", "up"), item="teddy", bob=0, look=0.5)


def vertical(out):
    w, h = 1080, 1920
    surf = surface(w, h)
    ctx = cairo.Context(surf)
    burst(ctx, w, h, 540, 1150)
    big_text(ctx, HEADLINE[0], 540, 205, fit_text(ctx, HEADLINE[0], 900, 200), "#ffffff", tilt=-0.03)
    big_text(ctx, HEADLINE[1], 540, 410, fit_text(ctx, HEADLINE[1], 940, 230), "#ffe14a", tilt=-0.03)
    sticker(ctx, w, h, lambda c: opponent(c, 800, 1130, 1.45), outline=14)
    sticker(ctx, w, h, lambda c: _clip(c, w, h, lambda: face_sticker(c, 360, 1020, 560)), outline=18)
    surf.write_to_png(str(out / f"thumb_short_1080x1920{SUFFIX}.png"))


def horizontal(out):
    w, h = 1280, 720
    surf = surface(w, h)
    ctx = cairo.Context(surf)
    burst(ctx, w, h, 640, 470)
    burst(ctx, w, h, 330, 470)
    big_text(ctx, HEADLINE[0], 905, 100, fit_text(ctx, HEADLINE[0], 700, 115), "#ffffff", tilt=-0.03)
    big_text(ctx, HEADLINE[1], 905, 225, fit_text(ctx, HEADLINE[1], 680, 135), "#ffe14a", tilt=-0.03)
    sticker(ctx, w, h, lambda c: opponent(c, 1000, 705, 0.82), outline=12)
    sticker(ctx, w, h, lambda c: _clip(c, w, h, lambda: face_sticker(c, 245, 235, 400)), outline=14)
    surf.write_to_png(str(out / f"thumb_wide_1280x720{SUFFIX}.png"))


def _clip(ctx, w, h, fn):
    ctx.rectangle(0, 0, w, h)
    ctx.clip()
    fn()


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    if "--no-stroke" in sys.argv:
        STROKE, SUFFIX = False, "_nostroke"
    vertical(out)
    horizontal(out)
    print("wrote", out)
