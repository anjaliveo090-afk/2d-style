"""Sample story in the box-head style: "Mister Button" (22.9 s made-up narration, voice in
output/sample/voice.wav, words in output/sample/aligned.json).

How it follows the references (style_bible.md, visual_grammar.md, angles.py):
- a hard cut on almost every phrase (20 shots, ~1.2 s each), a new flat background colour
  at every cut, no camera moves (static keys, engine.DRIFT = False);
- every shot is one of the measured reference angles (angles.py): face close-up, extreme
  close-up, full figure, over the shoulder, prop insert, wide minimal set, in-bed tilt;
- limited animation (engine.ANIM_FPS = 8), expressions snap on the key word, mouths flap only
  on the two quoted lines;
- the last shot repeats shot 1's framing and colour (callback, and the Short loops);
- ~7 SFX per 10 s, half of them on cuts (sound_design.md).

Usage: python3 sample.py out.mp4 cues.json [voice.wav] [first_frame last_frame]"""
import math
import sys

import angles as ang
import engine
import sets as st
from engine import PI, clamp, ease, keyed, lerp, render
from style import BoxChar, DAD, GIRL

TOTAL = 23.3
GIRL_GROWN = BoxChar("#f2b8d8", hair="pony")
DAD_SKIN = "#6f8fc8"   # dad's onesie colour for his hands in inserts


def pop_in(T, t0, d=0.12):
    """0 -> 1 scale over d seconds with a small overshoot (props popping on)."""
    x = clamp((T - t0) / d)
    return 0.0 if x <= 0 else (1.0 + 0.15 * math.sin(PI * x) if x < 1 else 1.0)


# ================================================================ scenes
def s_open(ctx, t, d, T0=0.0, final=False):
    T = T0 + t
    st.bg(ctx, "#6296ce")
    if final:      # callback: same framing, now he understands
        expr = keyed(T, [(0, "sad"), (22.19, "sob")])
    else:
        expr = keyed(T, [(0, "neutral"), (0.39, "stern")])
    ang.face(DAD, ctx, expr, T)


def s_teddy(ctx, t, d):
    T = 0.70 + t
    st.bg(ctx, "#fefaca")
    sw = 0.18 * math.sin((T - 0.7) * 7) if T >= 1.52 else 0.0
    ctx.save()
    ctx.translate(380, 520)
    ctx.rotate(sw)
    st.teddy(ctx, 0, 300, 2.2, rot=0.05)
    st.hand(ctx, 70, 10, 1.3, rot=-PI / 3, col=DAD_SKIN, pose="fist", length=9)
    ctx.restore()


def s_trash(ctx, t, d):
    T = 1.95 + t
    st.bg(ctx, "#92b6a2")
    f = ease((T - 2.0) / 0.25)
    st.teddy(ctx, 360 + 20 * (1 - f), lerp(120, 660, f), 1.3, rot=lerp(-1.2, 0.3, f))
    st.trash_bin(ctx, 360, 1010, 1.45, lid=1.0 - ease((T - 2.36) / 0.08))


def s_school(ctx, t, d):
    T = 2.50 + t
    st.room_box(ctx, back="#c2d2fe", side="#aebef0", floor="#606696", rug=None, door=False, shelf=False)
    st.chalkboard(ctx, 360, 470, 300, 170)
    kids = [(170, "#7ed6d6", None), (360, None, GIRL), (550, "#fece92", None)]
    for k, (x, col, ch) in enumerate(kids):
        c = ch or BoxChar(col, build="kid", skin="#f6d4c2")
        c.draw(ctx, x, 980, 0.95, "neutral" if ch is None else keyed(T, [(0, "neutral"), (3.1, "smile")]), T,
               pose="sit", arms=("hold", "hold"), look=0.2 * (k - 1))
        st.school_desk(ctx, x, 905, 0.95)


def s_home(ctx, t, d):
    T = 3.70 + t
    st.room_box(ctx, back="#fece92", side="#f2c27e", floor="#9a6a50", rug=None, door=False, shelf=False)
    st.rect(ctx, 290, 420, 140, 280, "#6a4a2e", st.lw_at(ctx, 140))          # open front door
    st.rect(ctx, 300, 430, 120, 270, "#aed6ea", st.lw_at(ctx, 140))
    st.rect(ctx, 225, 640, 70, 90, "#e2604e", st.lw_at(ctx, 100), r=14)       # backpack dropped
    GIRL.draw(ctx, 365, 880, 1.05, keyed(T, [(0, "smile"), (4.3, "neutral")]), T, arms=("down", "wave"))


def s_search(ctx, t, d):
    T = 4.65 + t
    st.bg(ctx, "#5aeeca")
    look = -1.0 if int(T * 4) % 2 else 1.0
    arms = ("shrug", "shrug") if T < 5.08 else ("reach", "ear")
    ang.full(GIRL, ctx, "worried", T, height=0.52, arms=arms, look=look)


def s_ask(ctx, t, d):
    T = 5.55 + t
    st.bg(ctx, "#e2929e")
    ang.face(GIRL, ctx, "pleading", T, width=0.6, talk=5.6 <= T < 7.35)


def s_ots(ctx, t, d):
    T = 7.40 + t
    st.bg(ctx, "#fe722e")
    st.sofa(ctx, 470, 800, 480)
    DAD.draw(ctx, 470, 990, 1.35, "stern", T, pose="sit", arms=("hold", "hold"), item="phone",
             talk=7.45 <= T < 8.6, look=-0.4)
    GIRL.draw_close(ctx, 110, 900, 340, "neutral", T, pose="back")


def s_phone(ctx, t, d):
    T = 8.65 + t
    st.bg(ctx, "#62527a")
    tap = 9.4 <= T < 9.6
    st.phone(ctx, 360, 640, 4.0, rot=-0.08, glow=1.0)
    st.hand(ctx, 170, 760, 1.5, rot=PI * 0.8, col=DAD_SKIN, pose="fist")
    st.hand(ctx, 560 - (20 if tap else 0), 700 - (40 if tap else 0), 1.5, rot=PI * 0.15, col=DAD_SKIN)


def s_night(ctx, t, d):
    st.bg(ctx, "#52567a")
    st.window(ctx, 360, 600, 380, 470, view="night", tilt=-0.04)
    ctx.save()
    ctx.rectangle(180, 380, 360, 440)
    ctx.clip()
    st.moon(ctx, 450, 470, 55)
    ctx.restore()


def s_pillow(ctx, t, d):
    T = 10.85 + t
    st.bg(ctx, "#ca8ace")
    expr = keyed(T, [(0, "sad"), (12.13, "cry")])
    ang.bed(GIRL, ctx, expr, T, st, rot=0.42, width=0.46)
    lw = st.lw_at(ctx, 200)
    st.oval(ctx, 300, 820, 150, 95, "#ffffff", lw, rot=0.4)                  # the hugged pillow
    for x, y in ((220, 770), (390, 880)):
        st.oval(ctx, x, y, 40, 34, GIRL.body, lw)


def s_years(ctx, t, d):
    T = 12.60 + t
    st.bg(ctx, "#cae2fe")
    for k, (yr, x, y, r, at) in enumerate((("2016", 250, 360, -0.12, 12.6), ("2021", 480, 610, 0.1, 12.81),
                                           ("2026", 260, 880, -0.06, 13.07))):
        if T >= at:
            st.calendar(ctx, x, y, 1.15, yr, crossed=clamp((T - at - 0.1) / 0.25) if k < 2 else 0.0, rot=r)


def s_moveout(ctx, t, d):
    T = 13.40 + t
    st.room_box(ctx, back="#fed68e", side="#f2c27e", floor="#b07a58", rug=None, door=True, shelf=False)
    for x, y in ((150, 1010), (230, 1010), (190, 905)):
        st.cardboard_box(ctx, x, y, 0.75)
    GIRL_GROWN.draw(ctx, 450, 990, 1.0, "neutral", T, pose="walk", walk_phase=T * 1.6,
                    arms=("carry", "carry"), item="box", item_hand=1, look=0.6)


def s_closet(ctx, t, d):
    T = 14.40 + t
    st.bg(ctx, "#565e66")
    st.closet(ctx, 460, 1000, 360, 600, open_=1.0)
    DAD.draw(ctx, 175, 1000, 1.2, "worried", T, arms=("down", "reach"), look=0.8)


def s_box(ctx, t, d):
    T = 15.35 + t
    st.bg(ctx, "#4666aa")
    sc = 2.4 * pop_in(T, 15.6, 0.15) if T >= 15.6 else 2.4
    st.cardboard_box(ctx, 360, 860, sc)
    if T >= 15.95:
        g = clamp((T - 15.95) / 0.25) * (1 - clamp((T - 16.4) / 0.2))
        st.sparkle(ctx, 560, 560, 90 * g, "#fff6c8")


def s_note(ctx, t, d):
    T = 16.55 + t
    st.bg(ctx, "#e2b672")
    u = ease((T - 16.85) / 0.3)
    st.note(ctx, 360, 620, 2.2, unfold=u, rot=-0.05)
    for side in (-1, 1):
        st.hand(ctx, 360 + side * 300, 640, 1.4, rot=0 if side > 0 else PI, col=DAD_SKIN, pose="fist")


def s_flash(ctx, t, d):
    T = 17.60 + t
    st.bg(ctx, "#fece92")
    ang.bed(GIRL, ctx, "content", T, st, rot=0.35, width=0.44, cover="#f2b8d8")
    st.teddy(ctx, 250, 820, 1.25, rot=0.3, worn=False)
    for at, x, y, r in ((17.92, 610, 300, 60), (18.46, 160, 420, 48), (18.86, 600, 820, 54)):
        if T >= at:
            st.sparkle(ctx, x, y, r * pop_in(T, at, 0.1), "#f0c814")


def s_late(ctx, t, d):
    T = 18.80 + t
    st.room_box(ctx, back="#5a5e76", side="#4a4e66", floor="#363a5e", rug=None, door=False, shelf=False)
    st.window(ctx, 360, 470, 150, 170, view="night")
    st.rect(ctx, 110, 470, 120, 330, "#2a2c3a", st.lw_at(ctx, 140))            # dark doorway
    GIRL.draw(ctx, 175, 860, 0.8, "sad", T, arms=("hold", "hold"), item="teddy", look=1.0)
    DAD.draw(ctx, 470, 1010, 1.0, "stern", T, pose="sit", arms=("hold", "hold"), look=-0.3)
    st.desk(ctx, 470, 880, 330)
    st.monitor(ctx, 470, 790, 190, on=True)


def s_sit(ctx, t, d):
    T = 20.25 + t
    st.bg(ctx, "#5a5e76")
    st.spotlight(ctx, 400, 1000, 500)
    st.bed_side(ctx, 380, 830, 560, blanket="#f2b8d8")
    DAD.draw(ctx, 420, 1000, 2.2, keyed(T, [(0, "worried"), (21.2, "sad")]), T, pose="sit",
             arms=("hold", "hold"), item=lambda c, x, y, s, tt, side: st.note(c, x, y - 10, s * 0.28, 1.0, 0.1,
                                                                              lines=("", "")))


def s_end(ctx, t, d):
    s_open(ctx, t, d, T0=21.65, final=True)


# ================================================================ shots (one static angle each)
S = []


def shot(start, draw, angle, **kw):
    S.append(dict(start=start, draw=draw, keys=ang.cam(start), angle=angle, vignette=0.0, **kw))


shot(0.00, s_open, "face", safe=False)
shot(0.70, s_teddy, "insert")
shot(1.95, s_trash, "insert")
shot(2.50, s_school, "wide")
shot(3.70, s_home, "wide")
shot(4.65, s_search, "full")
shot(5.55, s_ask, "face", safe=False, speaker=GIRL)
shot(7.40, s_ots, "ots", safe=False, speaker=DAD)
shot(8.65, s_phone, "extreme", safe=False)
shot(9.95, s_night, "insert")
shot(10.85, s_pillow, "bed", safe=False)
shot(12.60, s_years, "insert")
shot(13.40, s_moveout, "wide")
shot(14.40, s_closet, "wide")
shot(15.35, s_box, "insert")
shot(16.55, s_note, "insert")
shot(17.60, s_flash, "bed", safe=False)
shot(18.80, s_late, "wide")
shot(20.25, s_sit, "full")
shot(21.65, s_end, "face", safe=False)
SHOTS = S
for k, s in enumerate(SHOTS):
    s["end"] = SHOTS[k + 1]["start"] if k + 1 < len(SHOTS) else TOTAL

# ================================================================ SFX (~7 per 10 s, half on cuts; sound_design.md)
SFX = [
    (1.55, "swish.wav", 0.8), (2.25, "thud.wav", 0.9), (2.52, "pop.wav", 0.7), (3.75, "click.wav", 0.7),
    (5.08, "swish.wav", 0.7), (5.58, "snap.wav", 0.6), (7.42, "pop.wav", 0.8), (9.40, "click.wav", 0.7),
    (12.13, "pop.wav", 0.5), (12.60, "swoosh_long.wav", 0.8), (13.45, "pop.wav", 0.7), (15.95, "shine.wav", 0.7),
    (17.92, "pop.wav", 0.7), (18.46, "pop.wav", 0.7), (20.50, "thud.wav", 0.8), (22.19, "thud.wav", 0.9),
]


def angle_mix(shots):
    """Share of each reference angle in this story (compare with angles.ANGLE_MIX)."""
    out = {}
    for s in shots:
        out[s["angle"]] = out.get(s["angle"], 0) + (s["end"] - s["start"])
    tot = sum(out.values())
    return {k: round(v / tot, 2) for k, v in sorted(out.items(), key=lambda kv: -kv[1])}


if __name__ == "__main__":
    import json
    import safezone
    engine.DRIFT = False        # locked camera
    engine.ANIM_FPS = 8         # drawings update ~8x per second (77-81% held frames in the references)
    engine.VIGNETTE = 0.0
    json.dump([{"time": round(t, 3), "file": f, "volume": v} for t, f, v in sorted(SFX)],
              open(sys.argv[2], "w"), indent=1)
    if len(sys.argv) > 3 and sys.argv[3].endswith((".wav", ".mp3")):
        engine.set_voice(sys.argv[3])
    kw = {}
    if len(sys.argv) > 5:
        kw["frames"] = (int(sys.argv[4]), int(sys.argv[5]))
    print("angle mix:", angle_mix(SHOTS))
    safezone.fit(SHOTS, sys.modules[__name__])
    render(SHOTS, TOTAL, sys.argv[1], xfade=0.0, grain=0, fade_in=0.0, fade_out=0.0, **kw)
