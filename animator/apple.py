"""Story: "I tried an apple peeler" (user's voiceover, 35.2 s, first-person comedy monologue).
Built from sample.py: one static reference angle per phrase, hard cuts, a new flat colour
at every cut, limited animation, callback ending (the last shot = shot 1's angle and colour).

Word times: output/apple/aligned.json, checked against the voice stem
(Yo 16.7 s, Wait/this is crazy 18.8-19.8 s, What? 20.0 s, let's try it 31.0 s, Yeah 34.7 s).
Usage: python3 apple.py out.mp4 cues.json [voice] [first_frame last_frame]"""
import math
import sys

import angles as ang
import engine
import sets as st
from engine import PI, clamp, ease, keyed, render
from style import BoxChar, FRIEND

TOTAL = 35.6
ME = BoxChar("#f6c453", hair="short", hair_col="#3e2c1e")     # the narrator (yellow onesie)
ME_HAND = "#f6c453"
AQUA = "#7ed6d6"


PX, PY, PS = 285, 900, 1.3            # peeler placement: the whole tool centred in the frame
PU = 96 * PS
APPLE_XY = (PX + 2.2 * PU, PY - 1.75 * PU)
BLADE_XY = (540, 700)                  # where the blade meets the apple


def peel(ctx, **kw):
    st.peeler(ctx, PX, PY, PS, **kw)


def zoom(ctx, z, focus):
    """Draw the following (until restore) as an extreme close-up of `focus` (static, like a cut-in)."""
    ctx.save()
    ctx.translate(360, 640)
    ctx.scale(z, z)
    ctx.translate(-focus[0], -focus[1])


def pop_in(T, t0, d=0.12):
    x = clamp((T - t0) / d)
    return 0.0 if x <= 0 else (1.0 + 0.15 * math.sin(PI * x) if x < 1 else 1.0)


def crank_at(T, t0, rps):
    return (T - t0) * rps * 2 * PI


# ================================================================ scenes
def s_open(ctx, t, d):
    T = t
    st.bg(ctx, AQUA)
    ang.face(FRIEND, ctx, keyed(T, [(0, "smile"), (0.2, "happy")]), T)


def s_gift(ctx, t, d):
    T = 0.42 + t
    st.bg(ctx, "#fece92")
    sf, sm = ang.full_size(FRIEND, 0.42), ang.full_size(ME, 0.5)
    FRIEND.draw(ctx, 190, 990, sf, "happy", T, arms=("down", "reach"), item="gift", look=0.6)
    ME.draw(ctx, 520, 990, sm, keyed(T, [(0, "neutral"), (0.65, "smile")]), T, arms=("reach", "down"), look=-0.6)


def s_peeler(ctx, t, d):
    T = 1.10 + t
    st.bg(ctx, "#c2d2fe")
    sc = 1.55 * pop_in(T, 1.12, 0.15)
    if sc > 0:
        st.peeler(ctx, PX + 30, PY, PS * sc / 1.55, crank=0.4, apple_on=0.0)
    if T >= 1.2:
        st.sparkle(ctx, 560, 470, 70 * pop_in(T, 1.2, 0.1), "#fff6c8")


def s_suck(ctx, t, d):
    T = 1.55 + t
    st.bg(ctx, "#fe722e")
    ang.full(ME, ctx, keyed(T, [(0, "worried"), (1.9, "grimace")]), T, height=0.55, feet=0.8,
             arms=("down", "show"), item="knife")
    lw = st.lw_at(ctx, 200)
    st.rect(ctx, 60, 790, 600, 34, "#d8b07a", lw)                              # table hides his legs
    st.rect(ctx, 80, 824, 560, 400, "#c99a5e", lw)
    st.apple_chunks(ctx, 360, 775, 1.1, seed=4 + int(T * 4) % 2)
    if T >= 2.3:
        st.stress(ctx, 360, 330, 1.2)


def s_box(ctx, t, d):
    T = 2.85 + t
    st.bg(ctx, "#4666aa")
    st.rect(ctx, 150, 860, 560, 40, "#d8b07a", st.lw_at(ctx, 200))            # table
    st.gift_box(ctx, 450, 862, 1.4, open_=0.0)
    ME.draw_close(ctx, 120, 760, 330, "neutral", T, pose="back")


def s_figure(ctx, t, d):
    T = 3.70 + t
    st.bg(ctx, "#e2929e")
    ang.face(ME, ctx, keyed(T, [(0, "neutral"), (4.08, "worried")]), T)
    if T >= 4.3:
        st.question(ctx, 590, 300, 150 * pop_in(T, 4.3), "#ffffff")


def s_how(ctx, t, d):
    T = 4.70 + t
    st.bg(ctx, "#fefaca")
    peel(ctx, crank=0.4, apple_on=0.0)
    for k, (at, x, y) in enumerate(((4.75, 560, 420), (4.96, 180, 330))):
        if T >= at:
            st.question(ctx, x, y, 170 * pop_in(T, at), "#ffffff", rot=0.15 - 0.3 * k)


def s_put(ctx, t, d):
    T = 5.20 + t
    st.bg(ctx, "#5aeeca")
    on = ease((T - 5.75) / 0.3)
    peel(ctx, crank=0.4, apple_on=on)
    ax = APPLE_XY[0] + (1 - on) * 1.6 * PU
    st.hand(ctx, ax + 60, APPLE_XY[1] - 10, 1.1, rot=-0.3, col=ME_HAND, pose="open")


def s_spin(ctx, t, d):
    T = 6.50 + t
    st.kitchen(ctx)
    ME.draw(ctx, 330, 1010, 1.15, "neutral", T, arms=("reach", "down"))
    st.counter_front(ctx, 880)
    st.peeler(ctx, 420, 880, 0.7, crank=crank_at(T, 6.5, 0.8), apple_on=1.0)


def s_dunno(ctx, t, d):
    T = 7.45 + t
    st.bg(ctx, "#8a76b2")
    ang.face(ME, ctx, keyed(T, [(0, "worried"), (8.3, "squint")]), T, look=keyed(T, [(0, -0.6), (8.3, 0.3)]))


def s_touch(ctx, t, d):
    T = 8.70 + t
    st.bg(ctx, "#aed6ea")
    wob = 0.08 * math.sin(T * 9)
    zoom(ctx, 2.0, BLADE_XY)
    peel(ctx, crank=0.4, apple_on=1.0, blade=0.15 + wob)
    ctx.restore()
    if T >= 9.33:                      # "touch that": a question mark at the gap
        st.question(ctx, 200, 470, 190 * pop_in(T, 9.33), "#ffffff", rot=-0.1)


def s_oh(ctx, t, d):
    T = 10.55 + t
    st.bg(ctx, "#eaca22")
    ang.face(ME, ctx, keyed(T, [(0, "worried"), (10.66, "shock")]), T)


def s_snap(ctx, t, d):
    T = 11.40 + t
    st.bg(ctx, "#c2d2fe")
    b = ease((T - 12.0) / 0.12)
    zoom(ctx, 2.0, BLADE_XY)
    peel(ctx, crank=0.4, apple_on=1.0, blade=0.15 + 0.85 * b)
    ctx.restore()
    if T >= 12.13:
        st.impact(ctx, 360, 640, 1.6)


def s_gotit(ctx, t, d):
    T = 12.85 + t
    st.bg(ctx, "#fece92")
    ang.face(ME, ctx, keyed(T, [(0, "neutral"), (13.76, "smug")]), T)


def s_try(ctx, t, d):
    T = 14.08 + t
    st.bg(ctx, "#de6a1e")
    ang.full(ME, ctx, "stern", T, height=0.52, feet=0.74, arms=("fist", "hip"))


def s_turn(ctx, t, d):
    T = 15.45 + t
    st.bg(ctx, "#6296ce")
    a = crank_at(T, 15.45, 0.9)
    peel(ctx, crank=a, apple_on=1.0, blade=1.0, peeled=clamp((T - 15.6) / 4.0), ribbon=clamp((T - 15.7) / 2.0) * 0.5)
    st.hand(ctx, PX - 1.65 * PU - 0.25 * PU, PY - 1.75 * PU + math.sin(a) * 0.75 * PU, 0.9, rot=PI,
            col=ME_HAND, pose="fist")


def s_yo(ctx, t, d):
    T = 16.65 + t
    st.bg(ctx, "#f6d6c6")
    st.eye(ctx, 360, 600, 2.1, pupil=keyed(T, [(0, "dot"), (16.75, "wide")]))


def s_fast(ctx, t, d):
    T = 17.50 + t
    st.bg(ctx, "#5a5e76")
    p = 0.3 + clamp((T - 17.5) / 1.2) * 0.6
    peel(ctx, crank=crank_at(T, 17.5, 3.0), apple_on=1.0, blade=1.0, peeled=p,
         speed=1.0, ribbon=0.5 + 0.5 * clamp((T - 17.5) / 1.0))


def s_crazy(ctx, t, d):
    T = 18.75 + t
    st.bg(ctx, "#fe722e")
    ang.face(ME, ctx, keyed(T, [(0, "shock"), (19.27, "shout")]), T, talk=False)


def s_what(ctx, t, d):
    T = 19.85 + t
    st.bg(ctx, "#62527a")
    ang.full(ME, ctx, "shock", T, height=0.55, feet=0.76, arms=("up", "up"))


def s_look(ctx, t, d):
    T = 21.30 + t
    st.bg(ctx, "#4666aa")
    zoom(ctx, 1.8, (APPLE_XY[0] - 20, APPLE_XY[1] + 40))
    peel(ctx, crank=crank_at(T, 21.3, 3.0), apple_on=1.0, blade=1.0, peeled=0.95, speed=1.0, ribbon=1.0)
    ctx.restore()
    st.speed_lines(ctx, 380, 568, 160, seed=int(T * 8))


def s_omg(ctx, t, d):
    T = 22.60 + t
    st.bg(ctx, "#e2929e")
    ang.extreme(ME, ctx, "shock", T, width=1.15, top=0.12)


def s_watch(ctx, t, d):
    T = 23.45 + t
    st.bg(ctx, "#fefaca")
    secs = min(5.0, (T - 23.45) / 0.62 * 5.0)
    st.stopwatch(ctx, 360, 620, 230, seconds=secs, label="0:05" if T >= 24.07 else None)


def s_show(ctx, t, d):
    T = 24.85 + t
    st.bg(ctx, "#5aeeca")
    ang.face(ME, ctx, "happy", T, width=0.5, top=0.22, arms=("down", "show"), item="spiral_apple")


def s_spiral(ctx, t, d):
    st.bg(ctx, "#c2d2fe")
    st.apple(ctx, 360, 640, 200, peeled=1.0, leaf=False, rot=0.0)
    ctx.save()                     # the loose peel ring around it
    ctx.translate(360, 650)
    ctx.rotate(-0.25)
    ctx.scale(1, 0.3)
    ctx.arc(0, 0, 330, 0, 2 * PI)
    ctx.restore()
    st._ink(ctx, 26, st.hexc(st.APPLE_RED))


def s_saturn(ctx, t, d):
    T = 27.60 + t
    st.bg(ctx, "#52567a")
    st.stars_field(ctx, seed=3, n=30)
    st.saturn(ctx, 360, 600, 170 * (pop_in(T, 27.85, 0.15) or 1.0))


def s_planet(ctx, t, d):
    T = 28.50 + t
    st.bg(ctx, "#e2b672")
    ang.face(ME, ctx, keyed(T, [(0, "worried"), (30.06, "smug")]), T, arms=("shrug", "shrug"), width=0.5,
             top=0.26)


def s_school(ctx, t, d):
    T = 30.35 + t
    st.bg(ctx, "#fed68e")
    st.test_paper(ctx, 360, 640, 1.6 * (pop_in(T, 30.4, 0.12) or 1.0))


def s_bite(ctx, t, d):
    T = 31.00 + t
    st.bg(ctx, "#8a76b2")
    ang.face(ME, ctx, keyed(T, [(0, "smile"), (31.6, "happy")]), T, width=0.52, top=0.22,
             arms=("down", "show"), item="spiral_apple")


def s_chew(ctx, t, d):
    T = 31.95 + t
    st.bg(ctx, "#fece92")
    ang.extreme(ME, ctx, "content", T, width=1.1, top=0.14)
    st.apple(ctx, 560, 1000, 120, peeled=1.0, leaf=False, bite=True)
    for at, x, y, r in ((32.3, 610, 220, 60), (32.9, 120, 300, 46), (33.4, 600, 640, 52)):
        if T >= at:
            st.sparkle(ctx, x, y, r * pop_in(T, at, 0.1), "#f0c814")


def s_end(ctx, t, d):
    T = 33.90 + t
    st.bg(ctx, AQUA)                       # callback: shot 1's angle and colour
    ang.face(ME, ctx, keyed(T, [(0, "content"), (34.68, "happy")]), T, arms=("down", "up"))


# ================================================================ shots (one static angle each)
S = []


def shot(start, draw, angle, **kw):
    S.append(dict(start=start, draw=draw, keys=ang.cam(start), angle=angle, vignette=0.0, **kw))


shot(0.00, s_open, "face", safe=False)
shot(0.42, s_gift, "two")
shot(1.10, s_peeler, "insert")
shot(1.55, s_suck, "full")
shot(2.85, s_box, "ots", safe=False)
shot(3.70, s_figure, "face", safe=False)
shot(4.70, s_how, "insert")
shot(5.20, s_put, "insert")
shot(6.50, s_spin, "wide")
shot(7.45, s_dunno, "face", safe=False)
shot(8.70, s_touch, "extreme")
shot(10.55, s_oh, "face", safe=False)
shot(11.40, s_snap, "extreme")
shot(12.85, s_gotit, "face", safe=False)
shot(14.08, s_try, "full")
shot(15.45, s_turn, "insert")
shot(16.65, s_yo, "extreme")
shot(17.50, s_fast, "insert")
shot(18.75, s_crazy, "face", safe=False)
shot(19.85, s_what, "full")
shot(21.30, s_look, "extreme")
shot(22.60, s_omg, "extreme", safe=False)
shot(23.45, s_watch, "insert")
shot(24.85, s_show, "face", safe=False)
shot(26.30, s_spiral, "insert")
shot(27.60, s_saturn, "scenery")
shot(28.50, s_planet, "face", safe=False)
shot(30.35, s_school, "insert")
shot(31.00, s_bite, "face", safe=False)
shot(31.95, s_chew, "extreme", safe=False)
shot(33.90, s_end, "face", safe=False)
SHOTS = S
for k, s in enumerate(SHOTS):
    s["end"] = SHOTS[k + 1]["start"] if k + 1 < len(SHOTS) else TOTAL

# ================================================================ SFX (~6-7 per 10 s, about half on cuts)
SFX = [
    (0.44, "pop.wav", 0.7), (1.20, "shine.wav", 0.7), (2.30, "snap.wav", 0.7), (2.90, "pop.wav", 0.6),
    (4.30, "pop.wav", 0.6), (4.96, "pop.wav", 0.6), (6.06, "click.wav", 0.8), (7.50, "pop.wav", 0.6),
    (9.30, "swish.wav", 0.6), (10.66, "thud.wav", 0.8), (12.13, "knock.wav", 0.9), (13.76, "pop.wav", 0.6),
    (14.12, "pop.wav", 0.6), (16.70, "thud.wav", 0.9), (17.55, "swish.wav", 0.7), (19.90, "boing.wav", 0.6),
    (21.35, "swish.wav", 0.6), (22.65, "thud.wav", 0.8), (24.07, "tick.wav", 0.9), (24.90, "pop.wav", 0.7),
    (27.85, "shine.wav", 0.8), (30.40, "thud.wav", 0.7), (32.30, "click.wav", 0.8), (32.90, "pop.wav", 0.6),
    (34.68, "pop.wav", 0.7),
]


if __name__ == "__main__":
    import json
    import safezone
    from sample import angle_mix
    engine.DRIFT = False
    engine.ANIM_FPS = 8
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
