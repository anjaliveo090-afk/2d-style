# Style Bible: "box-head" flat 2D shorts

Measured from the 2 reference videos the user uploaded:

| Video | Length | Shots |
|---|---|---|
| Mom Forced Him to Smash His Monitor | 29.7 s | 26 |
| The Boy Who Described a View He Couldn't See | 32.6 s | 30 |

Methods:
- `analysis/frame_log.py` at 4 fps (every sheet was looked at);
- full-resolution frames for pixel measures;
- `analysis/new_visuals.py` and `analysis/flow.py`;
- a 1-frame-difference pass for cut type and drawing rate.

Raw numbers are in `analysis/ref_data/monitor.json` and `analysis/ref_data/window.json`.

Code: `animator/style.py` (characters), `animator/sets.py` (backgrounds, props, effects), `animator/sample.py` (template story).

## 1. Format and safe zones
- **9:16, 720x1280, 30 fps.** Length 30-33 s, 107-123 words (**3.6-3.8 words/s**). The voice is a fast, calm storyteller with very short pauses.
- **Drawn like a hand-made Procreate / MS-Paint comic, not 3D.** Every frame is flat colour fills with a thin black ink line. No gradients, no shading, no lighting effects, no vignette, no film grain, no depth of field.
- **Captions in the references:** one word at a time, white bold sans-serif with a soft dark shadow, in the **middle of the frame** (about y 55%). Our default is **no captions** (the user adds them). If they are ever needed: `assemble.py --words 1`.
- **Safe zone (the user's Shorts template):**
  - The whole character and key props stay inside x 38-680, y 149-1013.
  - Below y 678 the right edge is x 599 (like/comment buttons).
  - Captions go under y 1013.
  - Enforced by `safezone.fit(SHOTS, module)`. Big face close-ups that fill the frame, as in the references, are allowed. The fit only shrinks a shot when a whole-body character crosses the zone, so mark close-ups with `safe=False` (see `CLAUDE.md`).
- The references have a creator signature scribbled at the top of a few frames. **Never copy it**, and put no logo or text watermark in our frames.

## 2. Characters (measured in head-widths, HW)
All characters are built from one template. Only the onesie colour, the hair and the size change.

| Part | Measure | Notes |
|---|---|---|
| **Head** | A **rounded box**, width 1 HW, height **0.68-0.85 HW** (adults 0.68-0.75, kids 0.75-0.85) | Hand-drawn: the top edge is slightly wider than the bottom, corners rounded about 0.06 HW, edges not perfectly straight. No neck, no ears (one ear only in a listening close-up). No nose. |
| **Skin** | Cream `#fdf1e5` (monitor) / peach `#f6d4c2` (window boy) / tan `#dec6b4` (nurse) | Flat, no blush except as an expression mark |
| **Body** | One-piece **onesie** silhouette (body, arms and legs one colour, one outline) | Shoulders as wide as the head (1.0 HW, kids up to 1.3 HW), round shoulders that start right under the head's bottom corners. Torso tapers slightly to 0.75 HW at the hips. |
| **Torso length** | Head bottom to crotch **1.13 HW** (adult), 0.95 HW (kid) | Mom has two small curve marks on the chest |
| **Legs** | Crotch to feet **1.2 HW** (adult), 0.9 HW (kid) | Thigh 0.30 HW wide, tapering to 0.17 HW at the ankle. Feet are rounded points (footed onesie), turned slightly out. No shoes. |
| **Arms** | Length about 1.15 HW | 0.25 HW wide at the shoulder, 0.19 HW at the wrist. Soft noodle bend, no elbow joint. |
| **Hands** | Rounded **mitten**, 0.22 HW wide, with a thumb bump; fists are a round knob with 1-2 finger lines | Same colour as the onesie (gloves) |
| **Total height** | Head top to feet **3.0 HW** (adult), about 2.6 HW (kid) | An adult stands about 1.3x as tall as a kid |
| **Outline** | Near-black `#100c0c`, **2-3 px at full body and about 3.5 px in a face close-up** | A thin constant pen. It does not scale with the character. Code: screen width = 1.7 px + 0.0035 x head width in px. |
| **Light / shading / rim** | **None** | Flat fills only. No cast shadows, except a pale spotlight ellipse under a lone character for drama (last shot of the monitor video). |
| **Hair** | Flat brown `#9a6630` (dark brown `#734e2a`) shapes laid on the box | Mom: a fringe band over the top third of the head with a centre parting (an M edge), plus a ponytail rising behind on one side. Nurse: a bob framing the head. Most boys are **bald boxes**. |

Cast built in `style.py`:
- `MOM`: pink `#fdcdc7`, fringe + ponytail.
- `KID`: mint `#c6f6d2`, bald, kid build.
- `PATIENT`: hospital teal `#7aa6aa` with dark stripes `#54787e`.
- `FRIEND`: orange `#e4661e`.
- `NURSE`: pale blue `#d2eaf6`, bob `#734e2a`.
- `MAN`: mustard `#d8ae12`.
- `OLDMAN`: olive `#90782a`.

New characters only change the colour and the hair (`BoxChar(color, hair=..., build=...)`).

## 3. Faces and the expression set
- Features sit in the **lower 2/3 of the box**. Eyes sit at 55% of the head height, about 0.22 HW apart from the centre. Mouth at 80%.
- Eyes are small black ovals: 0.035 HW wide, 0.05 HW tall.
- Brows are thin curved strokes above the eyes. They do most of the acting.
- Mouths are a thin line, a small U, an open trapezoid (dark red `#8c3a32` inside) or a white teeth bar.

| `expr` | Drawn as | Seen in |
|---|---|---|
| `neutral` | Dot eyes, short flat mouth | mom listening |
| `smile` | Dot eyes, soft U mouth | mom at 0.0 s |
| `happy` | Closed arcs `^ ^`, U smile | nurse "said softly" |
| `content` | Closed arcs with lash ticks, small smile, blush hatching | boy "kept him going" |
| `stern` | Dot eyes, brows angled down to the centre, flat mouth | mom arms crossed |
| `angry` | V brows, small open shouting mouth | mom "You either smash" |
| `shout` | Squeezed `> <` eyes, wide open mouth | kid with headset swearing |
| `sad` | Dot eyes under raised inner brows, small wavy frown | kid holding the hammer |
| `worried` | Eyes with a lid arc, tilted brows, small open `o` | boy looking at the window |
| `cry` | Blue tear streams `#5ac0fc` from both eyes to the jaw, open red trapezoid mouth | "crying hysterically" |
| `sob` | Squeezed eyes, tear streams, mouth pulled down | "sobbed over the wreckage" |
| `shock` | Big white round eyes with small pupils, `o` mouth | kid "Mom, please" |
| `squint` | `> <` eyes with lash ticks, grimace | sick boy in pain |
| `grimace` | Flat brows, white teeth bar with a middle line | boy "through the pain", nurse "He didn't" |
| `smug` | Half-lid eyes, one brow up, crooked mouth | mom "Maybe now you'll learn" |
| `sleep` | Closed flat lines | patient in bed |
| `pleading` | Big glossy eyes (white highlight), raised brows | kid begging, hands together |

- Extra marks (`sets.py`):
  - a tear drop on the cheek;
  - stress arcs above the head;
  - a swear scribble (`@ ! #` plus a spiral);
  - sparkle stars;
  - red impact ticks;
  - a sweat drop;
  - a gloom cap (grey shadow over the top of the head when ashamed).
- **Expressions snap** from one drawing to the next. There are no tweens.
- Mouths flap only while a character speaks a **quoted line**: "Mom, please", "You either...", "Tell me what you see", "He didn't". During narration the mouth holds the expression.

## 4. Palette (hex, sampled from the frames)
**Background colours.** Every shot has one flat colour, and the colour changes at every cut.

| Mood | Colours |
|---|---|
| Neutral / intro | steel blue `#6296ce`, royal blue `#4666aa`, periwinkle `#c2d2fe`, sky `#aed6ea` |
| Warm / happy / memory | peach `#fece92`, apricot `#fed68e`, butter `#fefaca`, aqua `#7ed6d6`, rose `#e2929e`, mint `#5aeeca`, tan `#e2b672` |
| Tension / threat / anger | hot orange `#fe722e`, deep purple `#62527a`, orange `#de6a1e` |
| Shock / bad news | mustard `#eaca22`, orange `#e28212` |
| Sadness / loss / aftermath | slate `#565e66`, dusk navy `#5a5e76`, `#52567a`, lavender `#8a76b2`, deep green `#028666`, orchid `#ca8ace` |
| Hospital / story base (used again as a callback at the end) | brick red `#ce7a6a`, salmon `#d28682` |
| Extreme close-up | the skin colour itself `#f6d6c6` fills the background |

**Character and prop colours:**
- outline `#100c0c`;
- skin `#fdf1e5`;
- hair `#9a6630`;
- tears `#5ac0fc`;
- mouth `#8c3a32`;
- monitor `#000000` with a dark grey bezel `#303030`;
- metal grey `#848484`;
- wood `#6a4a2e`;
- window glass `#aee4f0`;
- brick `#c08060` / `#9c9c9c`;
- sparkle yellow `#f0c814`.

## 5. Sets and backgrounds
- **About 60% of shots are a character or prop on a plain colour background.** There is no floor line and no horizon: the character simply floats on the colour.
- **About 40% are a minimal set,** drawn with the same thin ink line and flat fills:
  - **Box room:** one-point perspective, light back wall and side walls, a dark navy floor, a door, a shelf. Seen from the bedroom or garage door.
  - **Wall and floor:** a pale wall over a darker floor band, with a wall socket and plug.
  - **Bunk / hospital bed:** grey metal frame, white mattress, teal blanket, pale blue pillow, a window above.
  - **Window close-up:** a brown frame and blue glass, or a brick wall behind it (the reveal).
  - **Landscape:** a flat sunset with a big sun, layered wavy green hills, cloud bands on a sky.
  - **Desk:** desk and monitor, shelf, door.
- **Prop inserts** fill the frame, on a plain colour:
  - monitor with a sparkle;
  - hammer in a hand;
  - calendar pages with red X;
  - phone;
  - balloons;
  - knocking fist;
  - a hand pulling a plug;
  - glass shards.
- **Depth of field:** none. **Lighting:** none. Mood comes **only from the background colour**: warm colours for happy memories, dark slate and navy for loss, orange and purple for threats.

## 6. Shot sizes (in order of use)
1. **Face close-up** (head 60-80% of the frame width), cut at the chest. Used for every emotional beat and every quote.
2. **Full figure(s) on colour.** Two characters for confrontation: the tall adult and the kneeling kid.
3. **Prop insert** filling the frame.
4. **Wide set** (room, bunk bed) with small characters.
5. **Extreme close-up:** one eye, a fist, a hand, a cheek against the screen edge.
6. **Odd angles:** top-down onto the head (hammer swing), over the shoulder from behind the mom, tilted head on a pillow.

## 7. Animation
- **Limited animation:** drawings update every 3-4 frames (about 8 per second). **77-81% of frames are exact holds.** Code: `engine.ANIM_FPS = 8`.
- Motion is pose swaps and a few in-betweens:
  - an arm waves at the window;
  - the hammer flies in on a curve;
  - tears stream;
  - a hand pulls the plug;
  - a calendar page drops;
  - a body slides on a cut.
- **The camera is locked.** The median camera speed is 0.2-0.5 % of the width per second. A "move" is a cut to a closer framing.
