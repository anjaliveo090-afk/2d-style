"""Story: "Types of people on Halloween" (user's voiceover, 10.4 s; fast list-style narration).
Built from sample.py: one static reference angle per phrase, hard cuts, a new flat colour
at every cut, limited animation, callback ending (the last shot = shot 1, so the Short loops).

Word times: SRT line times with the words spread evenly inside each line (the voice is
continuous speech, checked on the separated voice stem; the aligner matched only 21/43 words).
Usage: python3 halloween.py out.mp4 cues.json [voice] [first_frame last_frame]"""
import math
import sys

import angles as ang
import engine
import sets as st
from engine import PI, clamp, ease, keyed, render
from style import BoxChar, GIRL, KID

TOTAL = 10.7
YOU = KID                                                           # "you": the mint kid
VAMP = BoxChar("#2a2834", hair="short", hair_col="#1c1a24", build="tall", skin="#ece8f2")
DUSK = "#52567a"


def pop_in(T, t0, d=0.12):
    x = clamp((T - t0) / d)
    return 0.0 if x <= 0 else (1.0 + 0.15 * math.sin(PI * x) if x < 1 else 1.0)


# ================================================================ scenes
PUMPKINS = [(140 + c * 147, 500 + r * 250, -0.2 + (r * 4 + c) // 2 * 0.36) for r in range(2) for c in range(4)]


def s_eight(ctx, t, d, T0=0.0, final=False):
    T = T0 + t
    st.bg(ctx, DUSK)
    beat = 1 if int(T * 4) % 2 else -1
    for k, (x, y, at) in enumerate(PUMPKINS):
        sc = 1.0 if final else (pop_in(T, at) if T >= at else 0.0)
        if sc > 0:     # each pumpkin bobs out of phase with its neighbours (held 0.25 s each)
            st.pumpkin(ctx, x, y + 7 * beat * (1 if k % 2 else -1), 66 * sc)


def s_types(ctx, t, d):
    T = 1.20 + t
    st.night_street(ctx, T)
    s = 0.62
    # witch, ghost, vampire, the cat kid ("you") lined up on the pavement
    GIRL.draw(ctx, 130, 1000, s, "smug", T, arms=("down", "hip"))
    st.witch_hat(ctx, *GIRL.head_geo(130, 1000, s)[:3])
    st.ghost(ctx, 290, 990 - 12 * (int(T * 4) % 2), s * 1.05, T)          # the ghost floats
    vx, vtop, vU, vhh = VAMP.head_geo(450, 1000, s * 0.9)
    st.cape(ctx, vx, vtop, vU, length=2.6)
    VAMP.draw(ctx, 450, 1000, s * 0.9, "stern", T, arms=("cross", "cross"))
    st.cape_collar(ctx, vx, vtop + vhh, vU)
    YOU.draw(ctx, 600, 1000, s * 1.05, "happy", T, arms=("down", "hold"), item="bucket")
    st.cat_ears(ctx, *YOU.head_geo(600, 1000, s * 1.05)[:3])


def s_you(ctx, t, d):
    T = 2.85 + t
    st.bg(ctx, "#e2929e")
    ang.face(YOU, ctx, keyed(T, [(0, "neutral"), (3.1, "shock")]), T)


def s_kid(ctx, t, d):
    T = 3.75 + t
    st.bg(ctx, "#fece92")
    x, feet, h = 360, 0.78 * 1280, 0.5
    s = ang.full_size(YOU, h)
    YOU.draw(ctx, x, feet, s, keyed(T, [(0, "smile"), (4.2, "smug")]), T, arms=("down", "hold"), item="bucket")
    st.cat_ears(ctx, *YOU.head_geo(x, feet, s)[:3])


def s_grab(ctx, t, d):
    T = 4.45 + t
    st.bg(ctx, "#7ed6d6")
    lift = ease((T - 4.75) / 0.35)
    by = 760 - 100 * lift
    st.candy_bowl(ctx, 360, by, 2.0, full=1.0)
    for side in (-1, 1):
        st.hand(ctx, 360 + side * 300, by + 60, 1.4, rot=0 if side > 0 else PI, col=YOU.body, pose="fist")


def s_sign(ctx, t, d):
    T = 6.00 + t
    st.bg(ctx, "#fefaca")
    st.rect(ctx, 110, 850, 500, 36, "#a06c44", st.lw_at(ctx, 200))            # porch table
    st.candy_bowl(ctx, 360, 790, 1.6, full=0.0)
    st.sign(ctx, 360, 470, 400, 260, ["PLEASE", "TAKE 1"], rot=-0.04 + 0.02 * (1 if int(T * 4) % 2 else -1))
    if T >= 6.65:                                                         # "take ONE": circled
        ctx.save()
        ctx.translate(467, 520)
        ctx.scale(1, 0.8)
        ctx.new_sub_path()
        ctx.arc(0, 0, 50 * pop_in(T, 6.65), 0, 2 * PI)
        ctx.restore()
        st._ink(ctx, 9, st.hexc("#d8322a"))


def s_vamp(ctx, t, d):
    T = 7.05 + t
    st.bg(ctx, "#62527a")
    s = ang.full_size(VAMP, 0.55)
    x, feet = 360, 0.8 * 1280
    cx, top, U, hh = VAMP.head_geo(x, feet, s)
    spread = 0.75 + 0.45 * ease((T - 7.25) / 0.25) + 0.05 * (1 if int(T * 4) % 2 else -1)   # flutter
    st.cape(ctx, cx, top, U, length=3.0, spread=spread)
    VAMP.draw(ctx, x, feet, s, keyed(T, [(0, "neutral"), (7.7, "stern")]), T, arms=("up", "up") if spread > 1 else ("cross", "cross"))
    st.cape_collar(ctx, cx, top + hh, U)


def s_serious(ctx, t, d):
    T = 8.27 + t
    st.bg(ctx, "#de6a1e")
    head_top, head_w = 0.2 * 1280, 0.62 * 720
    expr = keyed(T, [(0, "stern"), (9.1, "angry")])
    U, hh = head_w, VAMP.b["head_h"] * head_w
    st.cape(ctx, 360, head_top, U, length=3.0, spread=1.0 + 0.04 * (1 if int(T * 4) % 2 else -1))
    ang.face(VAMP, ctx, expr, T)
    st.cape_collar(ctx, 360, head_top + hh, U)
    st.fangs(ctx, 360, head_top + 0.83 * hh + 0.01 * U, U)


def s_end(ctx, t, d):
    s_eight(ctx, t, d, T0=9.65, final=True)


# ================================================================ shots (one static angle each)
S = []


def shot(start, draw, angle, **kw):
    S.append(dict(start=start, draw=draw, keys=ang.cam(start), angle=angle, vignette=0.0, **kw))


shot(0.00, s_eight, "insert")
shot(1.20, s_types, "wide")
shot(2.85, s_you, "face", safe=False)
shot(3.75, s_kid, "full")
shot(4.45, s_grab, "insert")
shot(6.00, s_sign, "insert", keep=[(160, 340, 560, 600)])
shot(7.05, s_vamp, "full")
shot(8.27, s_serious, "face", safe=False)
shot(9.65, s_end, "insert")
SHOTS = S
for k, s in enumerate(SHOTS):
    s["end"] = SHOTS[k + 1]["start"] if k + 1 < len(SHOTS) else TOTAL

# ================================================================ SFX (~7 per 10 s, half on cuts)
SFX = [
    (0.18, "pop.wav", 0.6), (0.88, "pop.wav", 0.7), (1.22, "pop.wav", 0.7), (3.10, "thud.wav", 0.8), (3.78, "pop.wav", 0.7),
    (4.80, "swish.wav", 0.7), (6.02, "pop.wav", 0.7), (7.27, "swish.wav", 0.7), (9.15, "thud.wav", 0.9),
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
