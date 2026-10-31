"""Style check sheets for style.py / sets.py.
Usage: python3 test_sheet.py out_dir [ref_frames_dir]
Writes expressions.png (every character x every expression), poses.png (every character x the
main poses) and, when reference frames are given, compare.png (reference | ours, same shot)."""
import os
import sys

import cairo

import sets as st
from style import CAST, EXPRS, MOM, KID, PATIENT, NURSE, FRIEND

POSES = [("stand", ("down", "down"), None), ("stand", ("hip", "hip"), None), ("stand", ("cross", "cross"), None),
         ("stand", ("point", "down"), None), ("stand", ("point_down", "fist"), None), ("walk", ("down", "down"), None),
         ("stand", ("wave", "down"), None), ("stand", ("hold", "hold"), "hammer_side"), ("kneel", ("pray", "pray"), None),
         ("squat", ("shrug", "shrug"), None), ("sit", ("down", "down"), None), ("stand", ("swing", "down"), None),
         ("stand", ("face", "face"), None), ("back", ("down", "down"), None)]
POSE_EXPR = ["neutral", "stern", "stern", "angry", "angry", "smile", "happy", "sad", "pleading", "cry", "sob",
             "cry", "sob", "neutral"]
BGS = ["#6296ce", "#fece92", "#c2d2fe", "#62527a", "#5a5e76", "#7ed6d6", "#e2929e", "#028666", "#fe722e"]


def surface(w, h):
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
    return s, cairo.Context(s)


def label(ctx, s, x, y):
    ctx.select_font_face("DejaVu Sans")
    ctx.set_font_size(13)
    ctx.set_source_rgb(0.1, 0.1, 0.1)
    ctx.move_to(x, y)
    ctx.show_text(s)


def expressions(out):
    names = ["MOM", "KID", "PATIENT", "NURSE", "FRIEND", "GAMER", "MAN", "DAD"]
    cw, chh = 132, 150
    surf, ctx = surface(110 + cw * len(EXPRS), 30 + chh * len(names))
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()
    for j, e in enumerate(EXPRS):
        label(ctx, e, 110 + j * cw + 8, 20)
    for i, n in enumerate(names):
        ch = CAST[n]
        label(ctx, n, 8, 30 + i * chh + 80)
        for j, e in enumerate(EXPRS):
            x0, y0 = 110 + j * cw, 30 + i * chh
            ctx.save()
            ctx.rectangle(x0 + 2, y0 + 2, cw - 4, chh - 4)
            ctx.clip()
            st.bg(ctx, BGS[(i + j) % len(BGS)])
            ch.draw_head(ctx, x0 + cw / 2, y0 + chh - 22, 1.0 / ch.b["hw"], e, t=0.3)
            ctx.restore()
    surf.write_to_png(out)


def poses(out):
    names = ["MOM", "KID", "PATIENT", "NURSE", "FRIEND", "MAN"]
    cw, chh = 170, 400
    surf, ctx = surface(90 + cw * len(POSES), 30 + chh * len(names))
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()
    for j, (p, a, item) in enumerate(POSES):
        label(ctx, f"{p}/{a[0]}", 90 + j * cw + 6, 20)
    for i, n in enumerate(names):
        ch = CAST[n]
        label(ctx, n, 8, 30 + i * chh + 200)
        for j, (p, a, item) in enumerate(POSES):
            x0, y0 = 90 + j * cw, 30 + i * chh
            ctx.save()
            ctx.rectangle(x0 + 2, y0 + 2, cw - 4, chh - 4)
            ctx.clip()
            st.bg(ctx, BGS[(i * 3 + j) % len(BGS)])
            ch.draw(ctx, x0 + cw / 2, y0 + chh - 30, 0.95, POSE_EXPR[j], 0.3, arms=a, pose=p, item=item)
            ctx.restore()
    surf.write_to_png(out)


def ours(k, ctx):
    """Our version of each reference frame used in compare.png (720x1280 world)."""
    if k == 0:    # mom stern, hand on hip; kid kneeling, begging (monitor 9.5 s)
        st.bg(ctx, "#fece92")
        MOM.draw(ctx, 250, 810, 1.95, "stern", 0.3, arms=("behind", "hip"), look=0.3)
        KID.draw(ctx, 470, 880, 1.6, "sad", 0.3, arms=("pray", "pray"), pose="kneel", lean=-0.45, head_nod=8)
    elif k == 1:  # kid squatting, crying with the hammer (monitor 16.8 s)
        st.bg(ctx, "#028666")
        KID.draw(ctx, 360, 1190, 3.3, "cry", 0.3, arms=("shrug", "shrug"), pose="squat", item="hammer_side")
        st.stress(ctx, 330, 330, 2.6)
    elif k == 2:  # mom face close-up (monitor 0.0 s)
        st.bg(ctx, "#6296ce")
        MOM.draw_close(ctx, 360, 300, 540, "smile", 0.3)
        st.swear(ctx, 600, 160, 1.4)
    elif k == 3:  # patient on the pillow (window 0.0 s)
        st.bg(ctx, "#ce7a6a")
        st.in_bed(ctx, PATIENT, 380, 560, 2.9, "squint", 0.3, rot=0.55)
    elif k == 4:  # bunk bed, friend waving at the window (window 4.0 s)
        st.bg(ctx, "#4666aa")
        st.window(ctx, 470, 270, 150, 170)
        lo, up = st.bunk(ctx, 360, 1080, 1.15, blanket="#7aa6aa")
        FRIEND.draw(ctx, 500, up + 5, 0.9, "happy", 0.3, arms=("down", "wave"), pose="sit")
        PATIENT.draw_head(ctx, 180, lo + 5, 0.9, "sleep", 0.3, rot=-1.4)
    elif k == 5:  # nurse (window 28.5 s)
        st.bg(ctx, "#e2b672")
        NURSE.draw_close(ctx, 360, 330, 400, "happy", 0.3)


def compare(out, ref_dir):
    refs = ["m_9.5.png", "m_16.8.png", "m_0.0.png", "w_0.0.png", "w_4.0.png", "w_28.5.png"]
    tw, th = 270, 480
    surf, ctx = surface(tw * 2 * 3 + 40, (th + 30) * 2)
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()
    for k, r in enumerate(refs):
        col, row = k % 3, k // 3
        x0, y0 = col * (tw * 2 + 20), row * (th + 30) + 22
        label(ctx, f"reference {r}", x0 + 4, y0 - 6)
        label(ctx, "ours (style.py)", x0 + tw + 4, y0 - 6)
        img = cairo.ImageSurface.create_from_png(os.path.join(ref_dir, r))
        ctx.save()
        ctx.translate(x0, y0)
        ctx.scale(tw / 720, th / 1280)
        ctx.set_source_surface(img, 0, 0)
        ctx.paint()
        ctx.restore()
        ctx.save()
        ctx.translate(x0 + tw, y0)
        ctx.rectangle(0, 0, tw, th)
        ctx.clip()
        ctx.scale(tw / 720, th / 1280)
        ours(k, ctx)
        ctx.restore()
    surf.write_to_png(out)


if __name__ == "__main__":
    o = sys.argv[1]
    os.makedirs(o, exist_ok=True)
    expressions(os.path.join(o, "expressions.png"))
    poses(os.path.join(o, "poses.png"))
    if len(sys.argv) > 2:
        compare(os.path.join(o, "compare.png"), sys.argv[2])
    print("wrote sheets to", o)
