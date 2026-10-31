"""Box-head style (style_bible.md): flat 2D comic characters with a rounded-box head,
a one-piece onesie body (body, arms and legs one colour, one outline), mitten hands,
footed legs, no shading, and a thin near-black ink line of constant screen width.

BoxChar.draw() has the same signature as reference_examples/animator/style2.py Char2.draw(),
so story templates can swap styles. (x, y) is the point between the feet; s=1 makes an
adult whose head is 96 px wide and who is 3.0 head-widths (about 290 px) tall."""
import math

import cairo

import engine
from engine import PI, hexc, _NOW, _VOICE, voice_level

INK = hexc("#100c0c")
SKIN = hexc("#fdf1e5")
HAIR = hexc("#9a6630")
HAIR_DARK = hexc("#734e2a")
TEAR = hexc("#5ac0fc")
MOUTH = hexc("#8c3a32")
WHITE = (1, 1, 1)
LAST_BOX = {"box": None}   # screen-independent user-space box of the last draw (for safezone)

# proportions in head-widths (style_bible.md section 2)
BUILDS = {
    # torso = torso width (the arms hang outside it, so shoulders + arms ~ 1.0-1.3 HW), arm = limb width
    "adult": dict(hw=1.0, head_h=0.70, torso=1.13, leg=1.20, shoulder=0.76, hip=0.80, armw=0.29, thigh=0.40, reach=1.0),
    "kid": dict(hw=0.86, head_h=0.74, torso=0.98, leg=0.88, shoulder=0.98, hip=1.02, armw=0.33, thigh=0.50, reach=0.88),
    "chunky": dict(hw=1.0, head_h=0.74, torso=1.15, leg=1.05, shoulder=1.05, hip=1.05, armw=0.33, thigh=0.50, reach=1.0),
    "tall": dict(hw=1.0, head_h=0.72, torso=1.25, leg=1.45, shoulder=0.74, hip=0.76, armw=0.27, thigh=0.38, reach=1.15),
}


def pen(ctx, head_w_user):
    """Line width in user units for a thin constant pen: 1.7 px + 0.35% of the head width on screen
    (measured 2-3 px at full body, ~3.5 px in a face close-up)."""
    dx, dy = ctx.user_to_device_distance(1.0, 0.0)
    k = math.hypot(dx, dy) or 1.0
    return (1.7 + 0.0035 * head_w_user * k) / k


def _ink(ctx, lw, col=INK):
    ctx.set_source_rgb(*col[:3])
    ctx.set_line_width(lw)
    ctx.stroke()


def _fill(ctx, col):
    if len(col) == 4:
        ctx.set_source_rgba(*col)
    else:
        ctx.set_source_rgb(*col)


def fill_ink(ctx, col, lw):
    _fill(ctx, col)
    ctx.fill_preserve()
    _ink(ctx, lw)


# ---------------------------------------------------------------- limb tubes
def _bez(p0, p1, p2, n=22):
    out = []
    for i in range(n + 1):
        u = i / n
        a, b, c = (1 - u) ** 2, 2 * u * (1 - u), u * u
        out.append((a * p0[0] + b * p1[0] + c * p2[0], a * p0[1] + b * p1[1] + c * p2[1]))
    return out


def _sides(pts, widths):
    L, R = [], []
    for i, (x, y) in enumerate(pts):
        a = pts[max(0, i - 1)]
        b = pts[min(len(pts) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / d, dx / d
        w = widths[i] / 2
        L.append((x + nx * w, y + ny * w))
        R.append((x - nx * w, y - ny * w))
    return L, R


def joint_path(pts, n=26):
    """Points along a limb through joints (shoulder, elbow, hand): straight segments with the
    joints rounded off (the references bend arms and legs at soft elbows / knees)."""
    seg = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])]
    tot = sum(seg) or 1.0
    raw = []
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        k = max(2, int(n * seg[i] / tot))
        raw += [(a[0] + (b[0] - a[0]) * j / k, a[1] + (b[1] - a[1]) * j / k) for j in range(k)]
    raw.append(pts[-1])
    out = []
    for i in range(len(raw)):
        win = raw[max(0, i - 2):i + 3]
        if i < 2 or i > len(raw) - 3:
            out.append(raw[i])
        else:
            out.append((sum(p[0] for p in win) / len(win), sum(p[1] for p in win) / len(win)))
    return out


def tube(ctx, pts, w0, w1, col, lw, inside=None, skip_root=1.0, hand=0.0, thumb=0):
    """A tapered noodle limb (one silhouette with the body): filled, then outlined except where
    its root runs inside the body (inside(x, y) -> bool, only within the first skip_root of it).
    hand > 0 widens the end into a mitten; thumb = +1/-1 adds a thumb bump on that side."""
    pts = pts if len(pts) > 3 else joint_path(pts)
    n = len(pts)
    widths = []
    for i in range(n):
        u = i / (n - 1)
        w = w0 + (w1 - w0) * u
        if hand and u > 0.82:
            w = w1 + (hand - w1) * math.sin(min(1.0, (u - 0.82) / 0.18) * PI / 2)
        widths.append(w)
    L, R = _sides(pts, widths)
    ex, ey = pts[-1]
    dx, dy = ex - pts[-3][0], ey - pts[-3][1]
    a0 = math.atan2(dy, dx)
    rr = widths[-1] / 2
    cap = [(ex + rr * math.cos(a0 + PI / 2 - k * PI / 10), ey + rr * math.sin(a0 + PI / 2 - k * PI / 10))
           for k in range(11)]
    # cap goes from the left side (+normal) round the tip to the right side
    ctx.new_path()
    ctx.move_to(*L[0])
    for p in L[1:]:
        ctx.line_to(*p)
    for p in cap:
        ctx.line_to(*p)
    for p in reversed(R):
        ctx.line_to(*p)
    ctx.close_path()
    _fill(ctx, col)
    ctx.fill()

    def first_out(side):
        for i, p in enumerate(side):
            if i / (n - 1) > skip_root or inside is None or not inside(*p):
                return i
        return n - 1
    iL, iR = first_out(L), first_out(R)
    ctx.move_to(*L[iL])
    for p in L[iL + 1:]:
        ctx.line_to(*p)
    for p in cap:
        ctx.line_to(*p)
    for p in reversed(R[iR:]):
        ctx.line_to(*p)
    _ink(ctx, lw)
    if thumb:
        side = L if thumb > 0 else R
        p, q = side[int(n * 0.8)], pts[-1]
        mx, my = p[0] * 0.55 + q[0] * 0.45, p[1] * 0.55 + q[1] * 0.45
        ctx.move_to(*p)
        ctx.curve_to(mx, my, mx, my, q[0] * 0.7 + p[0] * 0.3, q[1] * 0.7 + p[1] * 0.3)
        _ink(ctx, lw * 0.85)
    return pts[-1]


# ---------------------------------------------------------------- the character
class BoxChar:
    """Same draw() signature as style2.Char2 / engine.Char."""

    def __init__(self, body, hair="none", hair_col=None, build="adult", skin=None, chest=False,
                 headset=False, glasses=False, stripes=None, head_h=None):
        self.body = hexc(body)
        self.hair = hair
        self.hair_col = hexc(hair_col) if hair_col else HAIR
        self.b = dict(BUILDS[build])
        if head_h:
            self.b["head_h"] = head_h
        self.skin = hexc(skin) if skin else SKIN
        self.chest = chest
        self.headset = headset
        self.glasses = glasses
        self.stripes = hexc(stripes) if stripes else None

    def unit(self, s):
        """Head width in px for size s."""
        return 96 * s * self.b["hw"]

    # ------------------------------------------------------------------
    def draw(self, ctx, x, y, s=1.0, expr="neutral", t=0.0, talk=False,
             arms=("down", "down"), pose="stand", look=0.0, bob=1.0,
             item=None, item_hand=1, walk_phase=0.0, lean=0.0, head_nod=0.0, shadow=False):
        b = self.b
        U = self.unit(s)
        lw = pen(ctx, U)
        L, T, hh = b["leg"] * U, b["torso"] * U, b["head_h"] * U
        sw, hw = b["shoulder"] * U, b["hip"] * U
        aw = b["armw"] * U
        ctx.save()
        ctx.translate(x, y)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        if pose == "lie":
            ctx.rotate(-PI / 2)
        if shadow == "spot":   # pale spotlight disc under a lone figure (the only "shadow" in the style)
            ctx.save()
            ctx.scale(1, 0.32)
            ctx.arc(0, 0, 1.3 * U, 0, 2 * PI)
            ctx.restore()
            fill_ink(ctx, hexc("#f4f4f4"), lw)

        breathe = (0.006 * U * bob) if int(t * 1.0) % 2 else 0.0
        legs = self._legs(pose, U, L, hw, walk_phase)
        crotch = legs["hip"]
        top = crotch - T - breathe
        lean_total = lean + (0.45 if pose == "bow" else 0.0)
        bot = crotch + 0.03 * U

        def torso_path(c):
            r = 0.07 * U
            x0, x1 = -sw / 2, sw / 2
            bx0, bx1 = -hw / 2, hw / 2
            c.new_path()
            c.move_to(x0, top + r)
            c.curve_to(x0, top + r * 0.3, x0 + r * 0.3, top, x0 + r, top)
            c.line_to(x1 - r, top)
            c.curve_to(x1 - r * 0.3, top, x1, top + r * 0.3, x1, top + r)
            c.curve_to(x1 + 0.01 * U, top + T * 0.55, bx1, bot - 0.25 * U, bx1, bot - 0.05 * U)
            c.curve_to(bx1, bot, bx1 - 0.05 * U, bot, bx1 - 0.1 * U, bot)
            c.line_to(bx0 + 0.1 * U, bot)
            c.curve_to(bx0 + 0.05 * U, bot, bx0, bot, bx0, bot - 0.05 * U)
            c.curve_to(bx0, bot - 0.25 * U, x0 - 0.01 * U, top + T * 0.55, x0, top + r)
            c.close_path()

        # torso hit-test (in the torso's own leaned frame)
        scratch = cairo.Context(cairo.ImageSurface(cairo.FORMAT_A8, 1, 1))
        torso_path(scratch)

        def inside(px, py):
            return scratch.in_fill(px, py)

        def lean_frame():
            ctx.translate(0, crotch)
            ctx.rotate(lean_total)
            ctx.translate(0, -crotch)

        # held-pose settle: every quarter second the head and hands shift a little, then hold
        # (the references change a drawing every 3-4 frames and hold it in between)
        beat = (1 if int(t * 4) % 2 else -1) * bob
        # capped in screen pixels: close-ups stay almost still, like the references
        dpx = math.hypot(*ctx.user_to_device_distance(1.0, 0.0)) or 1.0
        hb = top + 0.05 * U + head_nod + min(0.026 * U, 4.0 / dpx) * beat
        hx = look * 0.03 * U
        arm_pts = []
        for i, side in enumerate((-1, 1)):
            a = arms[i] if i < len(arms) else "down"
            sx, sy = side * (sw / 2 - aw * 0.2), top + 0.13 * U
            pts = self._arm_joints(a, side, sx, sy, U, t)
            if a not in ("behind", "wave"):
                j = min(0.06 * U, 10.0 / dpx) * beat
                pts = [pts[0], (pts[1][0] + side * j * 0.5, pts[1][1] - j * 0.4), (pts[2][0] + side * j, pts[2][1] - j)]
            arm_pts.append((a, side, pts))

        def cap(pts):
            """Rounded shoulder, outlined only outside the torso (drawn under the head)."""
            ctx.save()
            ctx.new_sub_path()
            ctx.arc(pts[0][0], pts[0][1], aw * 0.5, 0, 2 * PI)
            _fill(ctx, self.body)
            ctx.fill()
            torso_path(ctx)
            ctx.rectangle(-50 * U, -50 * U, 100 * U, 100 * U)
            ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
            ctx.clip()
            ctx.new_sub_path()
            ctx.arc(pts[0][0], pts[0][1], aw * 0.5, 0, 2 * PI)
            _ink(ctx, lw)
            ctx.restore()

        def draw_arm(i, a, side, pts):
            tip = tube(ctx, pts, aw, aw * 0.8, self.body, lw, inside=inside, skip_root=0.3,
                       hand=aw * 1.05, thumb=-side if a in ("down", "show", "wave", "point", "up", "reach", "ear") else 0)
            if item and i == item_hand:
                import sets
                sets.draw_item(ctx, item, tip[0], tip[1], U, t, side)

        # arms behind the body (hand on the back) go first
        ctx.save()
        lean_frame()
        for i, (a, side, pts) in enumerate(arm_pts):
            if a == "behind":
                cap(pts)
                draw_arm(i, a, side, pts)
        torso_path(ctx)
        fill_ink(ctx, self.body, lw)
        ctx.restore()
        # legs over the hem: their outline only shows outside the torso, so only the crotch V remains
        for side in (-1, 1):
            tube(ctx, legs[side], b["thigh"] * U, 0.17 * U, self.body, lw,
                 inside=lambda px, py: inside(px, py) and py < bot - 0.01 * U)

        ctx.save()
        lean_frame()
        if self.chest:   # two soft S-curves (monitor ref 9.5 s)
            for k in (-0.15, 0.1):
                x0, y0 = k * U + 0.04 * U, top + 0.3 * U
                ctx.move_to(x0, y0)
                ctx.curve_to(x0 - 0.07 * U, y0 + 0.06 * U, x0 - 0.07 * U, y0 + 0.15 * U, x0 + 0.01 * U, y0 + 0.22 * U)
                _ink(ctx, lw * 0.85)
        for a, side, pts in arm_pts:
            if a != "behind":
                cap(pts)
        if self.stripes is not None:
            for k in (-1, 1):
                ctx.rectangle(k * sw * 0.26 - 0.06 * U, top + 0.02 * U, 0.12 * U, T * 0.92)
                _fill(ctx, self.stripes)
                ctx.fill_preserve()
                _ink(ctx, lw * 0.8)
        if pose == "back":
            self._head(ctx, hx, hb, U, hh, lw, expr, t, talk, look, back=True)
        else:
            self._head(ctx, hx, hb, U, hh, lw, expr, t, talk, look)
        for i, (a, side, pts) in enumerate(arm_pts):
            if a != "behind":
                draw_arm(i, a, side, pts)
        ctx.restore()
        ctx.restore()
        half = max(sw / 2 + aw, 0.6 * U) + 0.1 * U
        LAST_BOX["box"] = (x - half, y + hb - hh - 0.35 * U, x + half, y + 0.05 * U)

    def draw_close(self, ctx, cx, head_top, head_w, expr="neutral", t=0.0, **kw):
        """Face close-up helper: head of width head_w px with its top at head_top (body runs off
        the bottom of the frame, like the references' chest-up shots)."""
        s = head_w / (96 * self.b["hw"])
        U = self.unit(s)
        b = self.b
        kw.setdefault("arms", ("behind", "behind"))     # chest-up: no hands in frame (like the references)
        saved = b["torso"]
        # the body runs off the bottom edge: stretch the (off-screen) torso so no legs show
        b["torso"] = max(saved, (1400 - head_top) / U - b["head_h"])
        try:
            y = head_top + (b["head_h"] + b["torso"] + b["leg"] - 0.05) * U
            self.draw(ctx, cx, y, s, expr, t, **kw)
        finally:
            b["torso"] = saved
        return y, s

    # ------------------------------------------------------------------
    def _legs(self, pose, U, L, hw, phase):
        th = self.b["thigh"] * U
        hx = max(hw / 2 - th / 2, th * 0.5)
        out = {}
        for side in (-1, 1):
            if pose in ("stand", "back", "lie", "bow"):
                hip = -L
                pts = [(side * hx, hip - 0.15 * U), (side * (hx + 0.03 * U), hip * 0.5), (side * (hx + 0.07 * U), -0.07 * U)]
            elif pose == "walk":
                hip = -L * 0.98
                sw = math.sin(phase * 2 * PI + (0 if side < 0 else PI))
                pts = [(side * hx, hip - 0.15 * U), (side * hx + sw * 0.12 * U, hip * 0.5),
                       (side * hx + sw * 0.32 * U, -0.07 * U - max(0, sw) * 0.1 * U)]
            elif pose == "sit":       # front view on a chair: short foreshortened thighs, shins down
                hip = -L * 0.62
                pts = [(side * hx, hip - 0.15 * U), (side * (hx + 0.08 * U), hip + 0.12 * U),
                       (side * (hx + 0.12 * U), -0.07 * U)]
            elif pose == "kneel":     # knees on the floor, feet tucked behind
                hip = -L * 0.48
                pts = [(side * hx, hip - 0.15 * U), (side * (hx + 0.05 * U), hip * 0.4), (side * (hx + 0.08 * U), -0.1 * U)]
            elif pose == "squat":     # wide bent legs (crying kid, monitor ref 16.8 s)
                hip = -L * 0.75
                pts = [(side * hx, hip - 0.12 * U), (side * (hx + 0.7 * U), hip * 0.45), (side * (hx + 0.5 * U), -0.07 * U)]
            else:
                raise ValueError(f"unknown pose {pose}")
            out[side] = pts
        out["hip"] = hip
        return out

    def _arm_joints(self, a, side, sx, sy, U, t):
        """Shoulder, elbow and hand for each arm pose (offsets in head-widths from the shoulder)."""
        s = side
        tbl = {
            "down": ((s * 0.06, 0.52), (s * 0.08, 1.05)),
            "hip": ((s * 0.42, 0.5), (s * 0.0, 0.8)),
            "behind": ((s * 0.22, 0.5), (-s * 0.15, 0.82)),
            "cross": ((s * 0.1, 0.6), (-s * 0.42, 0.45)),
            "point": ((s * 0.5, 0.18), (s * 1.05, 0.05)),
            "point_down": ((s * 0.42, 0.42), (s * 0.85, 0.92)),
            "up": ((s * 0.28, -0.45), (s * 0.34, -0.98)),
            "wave": ((s * 0.5, -0.12), (s * (0.62 + 0.14 * math.sin(t * 12)), -0.68)),
            "hold": ((s * 0.32, 0.55), (s * 0.02, 0.62)),
            "carry": ((s * 0.22, 0.55), (s * 0.42, 0.62)),
            "show": ((s * 0.4, 0.45), (s * 0.48, -0.12)),
            "pray": ((s * 0.36, 0.48), (s * 0.04, -0.04)),
            "face": ((s * 0.42, 0.38), (s * 0.2, -0.32)),
            "fist": ((s * 0.6, 0.25), (s * 0.55, -0.38)),
            "reach": ((s * 0.3, 0.42), (s * 0.58, 0.5)),
            "swing": ((s * 0.35, -0.48), (s * 0.08, -1.02)),
            "ear": ((s * 0.62, 0.2), (s * 0.5, -0.38)),
            "knock": ((s * 0.5, 0.02), (s * 1.0, -0.42)),
            "shrug": ((s * 0.62, 0.3), (s * 0.72, -0.16)),
        }
        (ex, ey), (hx, hy) = tbl.get(a, tbl["down"])
        k = U * self.b["reach"]
        return [(sx, sy), (sx + ex * k, sy + ey * k), (sx + hx * k, sy + hy * k)]

    # ------------------------------------------------------------------
    def _head(self, ctx, cx, bottom, U, hh, lw, expr, t, talk, look, back=False):
        draw_head(ctx, cx, bottom, U, hh, lw, expr, t, talk, look, self, back)

    def draw_head(self, ctx, x, y, s=1.0, expr="neutral", t=0.0, talk=False, look=0.0, rot=0.0, back=False):
        """Just the head (bottom centre at x, y): pillow shots, heads poking into frame."""
        U = self.unit(s)
        lw = pen(ctx, U)
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(rot)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        draw_head(ctx, 0, 0, U, self.b["head_h"] * U, lw, expr, t, talk, look, self, back)
        ctx.restore()


def head_path(ctx, cx, bottom, U, hh):
    """Rounded, slightly hand-drawn box: the top edge is a little wider than the bottom."""
    tl, tr = (cx - 0.505 * U, bottom - hh), (cx + 0.5 * U, bottom - hh - 0.01 * U)
    br, bl = (cx + 0.475 * U, bottom), (cx - 0.48 * U, bottom + 0.005 * U)
    r = 0.07 * U
    ctx.new_path()
    ctx.move_to(tl[0] + r, tl[1])
    ctx.line_to(tr[0] - r, tr[1])
    ctx.curve_to(tr[0] - r * 0.2, tr[1], tr[0], tr[1] + r * 0.2, tr[0], tr[1] + r)
    ctx.curve_to(tr[0] + 0.012 * U, (tr[1] + br[1]) / 2, br[0] + 0.004 * U, br[1] - 0.3 * hh, br[0], br[1] - r)
    ctx.curve_to(br[0], br[1] - r * 0.2, br[0] - r * 0.2, br[1], br[0] - r, br[1])
    ctx.line_to(bl[0] + r, bl[1])
    ctx.curve_to(bl[0] + r * 0.2, bl[1], bl[0], bl[1] - r * 0.2, bl[0], bl[1] - r)
    ctx.curve_to(bl[0] - 0.01 * U, bl[1] - 0.4 * hh, tl[0] + 0.004 * U, tl[1] + 0.3 * hh, tl[0], tl[1] + r)
    ctx.curve_to(tl[0], tl[1] + r * 0.2, tl[0] + r * 0.2, tl[1], tl[0] + r, tl[1])
    ctx.close_path()


def draw_head(ctx, cx, bottom, U, hh, lw, expr, t, talk, look, ch, back=False):
    top = bottom - hh
    hair, hc = ch.hair, ch.hair_col
    # hair behind the head
    if hair == "pony":
        ctx.move_to(cx + 0.05 * U, top + 0.02 * U)
        ctx.curve_to(cx + 0.15 * U, top - 0.42 * U, cx + 0.62 * U, top - 0.36 * U, cx + 0.66 * U, top + 0.12 * U)
        ctx.curve_to(cx + 0.7 * U, top + 0.4 * U, cx + 0.68 * U, top + 0.62 * U, cx + 0.78 * U, top + 0.78 * U)
        ctx.curve_to(cx + 0.62 * U, top + 0.8 * U, cx + 0.5 * U, top + 0.6 * U, cx + 0.48 * U, top + 0.4 * U)
        ctx.close_path()
        fill_ink(ctx, hc, lw)
    elif hair == "bob":
        ctx.move_to(cx - 0.64 * U, bottom - 0.12 * hh)
        ctx.curve_to(cx - 0.7 * U, top - 0.1 * U, cx - 0.4 * U, top - 0.2 * U, cx, top - 0.2 * U)
        ctx.curve_to(cx + 0.4 * U, top - 0.24 * U, cx + 0.7 * U, top - 0.12 * U, cx + 0.64 * U, bottom - 0.12 * hh)
        ctx.line_to(cx + 0.46 * U, bottom - 0.14 * hh)
        ctx.line_to(cx - 0.46 * U, bottom - 0.14 * hh)
        ctx.close_path()
        fill_ink(ctx, hc, lw)
    head_path(ctx, cx, bottom, U, hh)
    _fill(ctx, ch.skin)
    ctx.fill_preserve()
    ctx.save()
    ctx.clip_preserve()
    ctx.new_path()
    if hair in ("pony", "bob", "short", "fringe") or (back and hair != "none"):
        band = {"pony": 0.36, "bob": 0.3, "short": 0.2, "fringe": 0.33}.get(hair, 0.3) * hh
        if back:
            band = hh * (0.55 if hair == "short" else 0.95)
        ctx.move_to(cx - 0.6 * U, top - 0.1 * U)
        ctx.line_to(cx + 0.6 * U, top - 0.1 * U)
        ctx.line_to(cx + 0.6 * U, top + band)
        if hair in ("pony", "fringe") and not back:   # centre parting: two arcs meeting in a peak
            ctx.curve_to(cx + 0.35 * U, top + band * 0.95, cx + 0.06 * U, top + band * 0.8, cx, top + 0.04 * U)
            ctx.curve_to(cx - 0.06 * U, top + band * 0.8, cx - 0.35 * U, top + band * 0.95, cx - 0.6 * U, top + band)
        elif hair == "short" and not back:
            for k in range(6, -1, -1):
                ctx.line_to(cx - 0.6 * U + k * 0.2 * U, top + band * (1.0 if k % 2 else 0.7))
        else:
            ctx.curve_to(cx + 0.2 * U, top + band * 1.1, cx - 0.2 * U, top + band * 0.9, cx - 0.6 * U, top + band)
        ctx.close_path()
        fill_ink(ctx, hc, lw)
    ctx.restore()
    head_path(ctx, cx, bottom, U, hh)
    _ink(ctx, lw)
    if ch.headset:
        ctx.new_sub_path()
        ctx.arc(cx, top + 0.25 * hh, 0.56 * U, PI * 1.08, PI * 1.92)
        _ink(ctx, 0.07 * U, hexc("#2e2e30"))
        for k in (-1, 1):
            ctx.new_sub_path()
            ctx.arc(cx + k * 0.52 * U, top + 0.5 * hh, 0.16 * U, 0, 2 * PI)
            fill_ink(ctx, hexc("#3a3a3e"), lw)
    if not back:
        face(ctx, cx, top, U, hh, lw, expr, t, talk, look, ch)


# ---------------------------------------------------------------- faces
EXPRS = ("neutral", "smile", "happy", "content", "stern", "angry", "shout", "sad", "worried", "cry",
         "sob", "shock", "squint", "grimace", "smug", "sleep", "pleading")


def face(ctx, cx, top, U, hh, lw, expr, t, talk, look, ch=None):
    lx = look * 0.12 * U
    ey = top + 0.56 * hh
    my = top + 0.83 * hh
    ex0 = 0.2 * U
    fl = lw * 0.95      # feature line

    def line(pts, w=fl, col=INK):
        ctx.move_to(*pts[0])
        for p in pts[1:]:
            ctx.line_to(*p)
        _ink(ctx, w, col)

    def curve(x0, y0, x1, y1, x2, y2, w=fl):
        ctx.move_to(x0, y0)
        ctx.curve_to(x0 + (x1 - x0) * 0.66, y0 + (y1 - y0) * 0.66, x2 + (x1 - x2) * 0.66, y2 + (y1 - y2) * 0.66, x2, y2)
        _ink(ctx, w)

    def dot(x, y, rx=0.024 * U, ry=0.036 * U):
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(rx, ry)
        ctx.arc(0, 0, 1, 0, 2 * PI)
        ctx.restore()
        _fill(ctx, INK)
        ctx.fill()

    def brow(side, lift=0.0, tilt=0.0, bend=0.02):
        """tilt > 0: inner end up (sad); tilt < 0: inner end down (angry)."""
        bx = cx + side * ex0 + lx
        by = ey - 0.11 * U - lift * U
        inner = (bx - side * 0.075 * U, by - tilt * U)
        outer = (bx + side * 0.075 * U, by + tilt * 0.4 * U)
        curve(inner[0], inner[1], bx, by - bend * U, outer[0], outer[1])

    def closed_arc(x, y, up=True, w=0.06):
        ctx.new_sub_path()
        if up:
            ctx.arc(x, y + 0.02 * U, w * U, PI + 0.4, 2 * PI - 0.4)
        else:
            ctx.arc_negative(x, y - 0.03 * U, w * U, PI - 0.4, 0.4)
        _ink(ctx, fl)

    def chevron(x, y, side):
        d = 0.05 * U
        line([(x - side * d, y - d * 0.8), (x + side * d * 0.4, y), (x - side * d, y + d * 0.8)])

    sq = expr in ("shout", "squint", "sob")
    for side in (-1, 1):
        ex = cx + side * ex0 + lx
        if expr in ("happy", "content"):
            closed_arc(ex, ey)
            if expr == "content":
                for k in range(3):
                    a = PI + 0.5 + k * 0.5
                    line([(ex + math.cos(a) * 0.065 * U, ey + 0.02 * U + math.sin(a) * 0.065 * U),
                          (ex + math.cos(a) * 0.1 * U, ey + 0.02 * U + math.sin(a) * 0.1 * U)], fl * 0.7)
            brow(side, 0.03)
        elif expr == "sleep":
            line([(ex - 0.05 * U, ey), (ex + 0.05 * U, ey)])
            brow(side, -0.01)
        elif sq:
            chevron(ex, ey, side)
            for k in (-1, 0, 1):
                line([(ex - side * 0.06 * U, ey + k * 0.035 * U), (ex - side * 0.1 * U, ey + k * 0.05 * U)],
                     fl * 0.6)
            brow(side, 0.0, tilt=0.03 if expr != "shout" else -0.03)
        elif expr in ("shock", "pleading"):
            rx, ry = (0.075, 0.085) if expr == "shock" else (0.06, 0.07)
            ctx.save()
            ctx.translate(ex, ey)
            ctx.scale(rx * U, ry * U)
            ctx.arc(0, 0, 1, 0, 2 * PI)
            ctx.restore()
            fill_ink(ctx, WHITE, fl)
            if expr == "shock":
                dot(ex + lx * 0.2, ey, 0.022 * U, 0.026 * U)
                brow(side, 0.06)
            else:
                dot(ex + lx * 0.2, ey + 0.01 * U, 0.045 * U, 0.052 * U)
                ctx.arc(ex + 0.012 * U, ey - 0.01 * U, 0.016 * U, 0, 2 * PI)
                _fill(ctx, WHITE)
                ctx.fill()
                brow(side, 0.04, tilt=0.04)
        elif expr == "smug":
            dot(ex, ey + 0.008 * U, 0.024 * U, 0.024 * U)
            line([(ex - 0.045 * U, ey - 0.012 * U), (ex + 0.045 * U, ey - 0.012 * U)])
            brow(side, 0.05 if side > 0 else 0.0, tilt=-0.02 if side < 0 else 0.0)
        else:
            dot(ex, ey)
            if expr == "stern":
                brow(side, -0.01, tilt=-0.025, bend=0.0)
            elif expr == "angry":
                brow(side, -0.02, tilt=-0.05, bend=-0.01)
            elif expr in ("sad", "cry"):
                brow(side, 0.02, tilt=0.045, bend=0.01)
            elif expr == "worried":
                curve(ex - 0.045 * U, ey - 0.035 * U, ex, ey - 0.06 * U, ex + 0.045 * U, ey - 0.035 * U, fl * 0.8)
                brow(side, 0.03, tilt=0.05)
            elif expr == "grimace":
                brow(side, 0.0, tilt=-0.015, bend=0.0)
            else:
                brow(side, 0.0)

    # tears (streams from both eyes to the jaw)
    if expr in ("cry", "sob"):
        for side in (-1, 1):
            ex = cx + side * ex0 + lx
            ctx.rectangle(ex - 0.045 * U, ey + 0.02 * U, 0.09 * U, top + hh - ey - 0.03 * U)
            fill_ink(ctx, TEAR, fl)
    if expr == "content":
        for side in (-1, 1):
            for k in range(3):
                bx = cx + side * 0.32 * U + k * 0.025 * U
                line([(bx, ey + 0.09 * U), (bx - 0.02 * U, ey + 0.13 * U)], fl * 0.7, hexc("#e8707a"))

    # mouth
    mx = cx + lx * 1.1
    mouth = expr
    if talk and engine.LIPSYNC:
        level = None
        if _VOICE["env"] is not None and (_NOW.get("speaker") is ch or talk is True):
            level = voice_level()
        open_now = (level > 0.15) if level is not None else (int(t * 8) % 3 != 2)
        if open_now and expr not in ("cry", "sob", "shout"):
            mouth = "talk_wide" if (level or 0.6) > 0.5 and int(t * 8) % 2 == 0 else "talk"
    if mouth in ("neutral", "stern", "sleep"):
        line([(mx - 0.05 * U, my), (mx + 0.05 * U, my)])
    elif mouth in ("smile", "happy", "content"):
        curve(mx - 0.13 * U, my - 0.03 * U, mx, my + 0.05 * U, mx + 0.13 * U, my - 0.03 * U)
    elif mouth == "smug":
        curve(mx - 0.08 * U, my + 0.01 * U, mx, my + 0.02 * U, mx + 0.08 * U, my - 0.025 * U)
    elif mouth in ("sad", "worried", "pleading"):
        if mouth == "worried":
            ctx.save()
            ctx.translate(mx, my)
            ctx.scale(0.03 * U, 0.022 * U)
            ctx.arc(0, 0, 1, 0, 2 * PI)
            ctx.restore()
            fill_ink(ctx, MOUTH, fl)
        else:
            line([(mx - 0.07 * U, my + 0.01 * U), (mx - 0.03 * U, my - 0.01 * U), (mx + 0.02 * U, my + 0.005 * U),
                  (mx + 0.07 * U, my - 0.005 * U)])
    elif mouth in ("angry", "talk", "talk_wide", "shout", "cry", "sob", "shock"):
        if mouth == "shock":
            w0, w1, h = 0.035, 0.04, 0.06
        elif mouth == "talk":
            w0, w1, h = 0.05, 0.04, 0.035
        elif mouth == "angry":
            w0, w1, h = 0.07, 0.05, 0.045
        elif mouth == "sob":
            w0, w1, h = 0.09, 0.13, 0.06
        else:  # talk_wide / shout / cry: open trapezoid, wider at the bottom
            w0, w1, h = 0.11, 0.15, 0.1
        y0 = my - h * U * 0.55
        ctx.move_to(mx - w0 * U, y0)
        ctx.line_to(mx + w0 * U, y0 - 0.005 * U)
        ctx.line_to(mx + w1 * U, y0 + h * U)
        ctx.line_to(mx - w1 * U, y0 + h * U)
        ctx.close_path()
        fill_ink(ctx, MOUTH, fl)
        if mouth in ("cry", "shout", "talk_wide"):   # top teeth band
            ctx.save()
            ctx.move_to(mx - w0 * U, y0)
            ctx.line_to(mx + w0 * U, y0 - 0.005 * U)
            ctx.line_to(mx + w1 * U, y0 + h * U)
            ctx.line_to(mx - w1 * U, y0 + h * U)
            ctx.close_path()
            ctx.clip()
            ctx.rectangle(mx - w1 * U, y0 - 0.02 * U, 2 * w1 * U, h * U * 0.32)
            fill_ink(ctx, WHITE, fl * 0.8)
            ctx.restore()
    elif mouth in ("grimace", "squint"):
        w = 0.1 if mouth == "grimace" else 0.075
        ctx.rectangle(mx - w * U, my - 0.03 * U, 2 * w * U, 0.06 * U)
        fill_ink(ctx, WHITE, fl)
        line([(mx - w * U, my), (mx + w * U, my)], fl * 0.7)
    if ch is not None and ch.glasses:
        for side in (-1, 1):
            ctx.new_sub_path()
            ctx.arc(cx + side * ex0 + lx, ey, 0.085 * U, 0, 2 * PI)
            _ink(ctx, fl)
        line([(cx - ex0 + 0.085 * U + lx, ey), (cx + ex0 - 0.085 * U + lx, ey)])


# ---------------------------------------------------------------- the cast (style_bible.md section 2)
MOM = BoxChar("#fdcdc7", hair="pony", chest=True)
KID = BoxChar("#c6f6d2", build="kid")
GAMER = BoxChar("#c6f6d2", build="kid", headset=True)
PATIENT = BoxChar("#7aa6aa", build="kid", skin="#f6d4c2", stripes="#54787e")
FRIEND = BoxChar("#e4661e", build="kid", skin="#f6d4c2")
NURSE = BoxChar("#d2eaf6", hair="bob", hair_col="#734e2a", skin="#dec6b4")
MAN = BoxChar("#d8ae12", build="tall")
OLDMAN = BoxChar("#90782a", build="tall", glasses=True)
DAD = BoxChar("#6f8fc8", hair="short", hair_col="#3e2c1e", build="chunky")
GIRL = BoxChar("#f2b8d8", hair="pony", build="kid")
CAST = dict(MOM=MOM, KID=KID, GAMER=GAMER, PATIENT=PATIENT, FRIEND=FRIEND, NURSE=NURSE, MAN=MAN,
            OLDMAN=OLDMAN, DAD=DAD, GIRL=GIRL)
