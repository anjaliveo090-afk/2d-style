# Visual grammar: how the references turn each phrase into a picture

Source: the 2 reference videos, read at 4 fps with the spoken line on every frame (`analysis/frame_log.py`).

Rulebook for every new voiceover. Tag every phrase with a rule from section 4 and an angle from section 2 before writing shots.

## 1. Measured pace and camera

| What | monitor | window | **Target for our renders** |
|---|---|---|---|
| New visual (`new_visuals.py`) | every 1.24 s (median gap 1.25) | every 1.49 s (median gap 1.50) | **every 1.2-1.6 s**, no gap over 2.6 s |
| Hard-cut shot length | median 1.24 s, 0.6-1.8 s | median 0.94 s (1.1 s mean), 0.25-2.5 s | 0.8-2.0 s per shot |
| Transitions | hard cuts, 1 frame | hard cuts, 1 frame | **hard cuts** (`xfade=0`), no dissolves, no fades |
| Camera speed, median (`flow.py`, % width/s) | 0.47 | 0.20 | **under 1.5** (locked camera) |
| Camera speed, mean | 2.99 | 3.57 | 1-5 (only from the rare snap or slide) |
| Non-camera motion | 3.28 | 3.43 | **2.5-5** (pose swaps, props moving) |
| Drawing rate | every 3-4 frames | every 3-4 frames | `engine.ANIM_FPS = 8` |
| Identical-frame share | 0.77 | 0.81 | about 0.75 |
| Words per second | 3.6 | 3.8 | the voice decides |

The sample (`animator/sample.py`) measured:

| Measure | Sample |
|---|---|
| New visual | every 1.29 s (median gap 1.35 s) |
| Camera speed median / mean | 0.02 / 4.86 |
| Non-camera motion | 3.27 |
| Held frames | 0.87 |

What this means:
- The pace comes from **cuts on almost every phrase** (2-5 words) and from **pose and expression swaps**, not from camera moves.
- The camera never pans or pushes. To get closer, **cut** to a closer framing. Every shot uses a single static key: `keys=[(start, zoom, (cx, cy))]` with `engine.DRIFT = False`.
- **The background colour changes at every cut** (style_bible §4). Two shots in a row never share a colour, unless they are the same scene continuing.
- The rare in-shot motion is drawn:
  - a body or bed slides in during its first 0.3 s;
  - the hammer flies at the camera;
  - a calendar page drops;
  - sparkle stars pop in one by one.


## 2. Camera angles (measured shot by shot: use ONLY these)
Each of the 56 reference shots was labelled with its angle and measured: the largest head box as a % of the frame width, plus its position.

**The camera never moves. A shot IS its angle.** `animator/angles.py` turns each angle into placement helpers, so a story picks an angle per phrase and draws there.

| Angle | Share of shots | Measured framing | Reference shots | Helper |
|---|---|---|---|---|
| **face** | 22% | Chest-up, frontal or slight 3/4. Head **55-75% of the width**, head top at y 180-300 (14-23%), face centre at y 400-530. Body runs off the bottom. No hands unless they hold the prop. | mom smiling 0.0 s; kid with hammer 6.0 / 7.0 s; begging 10.3 s; mom with phone 26.4 s; boy 9.8 / 14.1 s; nurse 28.3 / 29.3 s | `angles.face(ch, ctx, expr, T)` |
| **extreme** | 11% | One feature fills the frame (head wider than the frame): an eye, cheek + hands, the top of a head | eye staring 2.4 s, cheek 12.3 s, content face + hands 16.0 s, blind eye 29.8 s, hammer from above 18.4 s | `angles.extreme(...)`, `sets.eye(...)` |
| **full** | 13% | Whole figure on a flat colour, **45-70% of the frame height**, centred, feet around y 1000 | crying squat 16.6 s; sobbing 21.6 s; slumped on a chair in a spotlight 28.4 s; balloon man 7.2 s | `angles.full(ch, ctx, expr, T, height=0.58)` |
| **two** | 5% | Tall adult (60%+ height) and small kid, both whole. The adult leans in or towers, sometimes cut by the edge | mom + kneeling kid 9.2 s; mom over the kid 11.6 s | `angles.two(adult, kid, ...)` |
| **ots** | 5% | Over the shoulder: the back of one character, big, cut by a bottom corner (40-50% of the frame); the other whole and smaller | kid's head in front of mom 7.8 s; mom's back holding the bat, kid far 13.3 s | `angles.ots(front, back, ...)` / `draw_close(..., pose="back")` |
| **insert** | 14% | One prop fills 50-80% of the frame on its own colour; a hand may enter from an edge | socket + hand 2.5 s; monitor + sparkle 3.3 s; shards 20.1 s; calendars 25.4 s; empty hospital bed 1.6 s; fist knock 18.1 s; window → bricks 25.2 s | `sets.*` props, `sets.hand(...)` |
| **wide** | 14% | Minimal set in one-point perspective (box room, bunk bed), heads only **7-11% of the width** | garage 4.6 / 18.7 s; bunk + window 3.7 s; nurses moving him 21.3 s; empty bed 20.6 s | `sets.room_box`, `sets.bunk` |
| **bed** | 6% | Lying on a pillow, head tilted about 25-30°, **44-48% of the width**, body under a blanket to the bottom-left | sick boy 0.0 s; "why did he lie" 26.6 s; callback 30.7 s | `angles.bed(ch, ctx, expr, T, sets)` |
| **scenery** | 4% | Flat landscape or sky, no character | sunset 8.2 s; sky + sun 17.4 s | `sets.sunset`, `sets.sky` |
| **low / top** | 6% | From below the upper bunk looking up; top-down onto a raised hammer; high angle into a room corner | 12.8 s; 17.8 s; 1.7 s | build per story |

Rules:
- Pick the angle from the phrase type (section 4), then use the helper's default numbers.
- **No other angles:** no dutch tilts, no pans, no dolly moves, no depth of field, no shots between the measured sizes.
- Two shots in a row never share both the angle and the colour.
- The last shot repeats shot 1's angle and colour (callback).
- Over a whole video, aim for roughly the reference mix:

  | Angle group | Share |
  |---|---|
  | face + extreme | 30-35% |
  | full + two + ots | 20-25% |
  | insert + scenery | 15-25% |
  | wide + bed + low | 20-25% |

- Check the mix with `sample.angle_mix(SHOTS)` (give every shot an `angle=`).

Sample (`animator/sample.py`):
- face + extreme 24%;
- full + ots 15%;
- insert 25%;
- wide + bed 37%.

It leans on sets because the story moves through many places. A story with more dialogue should use more face shots.

## 3. Structure of a 30 s short
1. **0-3 s, the hook:** the main character's face close-up and the inciting detail ("heard her son swearing", "a sick boy... hospital bed"), 2-3 cuts.
2. **3-10 s, setup:** each noun shown literally (socket, monitor, garage, bunk bed, window). A list gets one shot per item.
3. **10-20 s, escalation:**
   - quotes as face close-ups with mouths flapping;
   - confrontation as two full figures (tall adult and small kneeling kid);
   - the action beat (swing, knock).
4. **20-26 s, the loss or turn:** the aftermath on a dark slate or navy background (shards, empty bed), a time skip ("months later", "later") with a prop (calendar) or a moved scene.
5. **26-32 s, the twist line:** an extreme close-up reveal (an eye, a brick wall in the window, a phone), then a **callback to the first image or a lone figure** for the last words. The film just stops on the last word: no outro, no fade.

## 4. Sentence type → what is shown → camera angle → character reaction

| # | When the phrase... | Show | Angle (section 2) | Character reaction | Examples from the references |
|---|---|---|---|---|---|
| 1 | Introduces the main character ("This mother", "A sick boy") | **Face close-up** of that person on a flat colour | Close-up, head 70-80% of the width, cut at the chest | Calm, then the expression snaps on the key word | mom smiling on steel blue; boy squinting on a pillow |
| 2 | Says what they **perceive** ("heard", "staring") | The **sense made visible**: swear scribble pops by the head; an extreme close-up of an eye | Same close-up, or a cut to an extreme close-up | Smile → stern on "swearing"; wide eye | `@!#` scribble; eye staring at the pink-purple wall |
| 3 | Names a **concrete thing** (monitor, socket, hammer, balloons, phone) | **That object alone**, filling the frame, on its own colour | Insert, centred | A hand acts on it (pulls the plug, hands the hammer) | plug pulled from the socket; monitor with a sparkle |
| 4 | Names a **place** (garage, hospital bed, bunk) | A **minimal set** (box room, bed, bunk), wide | Wide, static | Small figures, one peeking through the door | garage box room; empty hospital bed |
| 5 | Is a **quoted line** ("Mom, please", "Tell me what you see", "He didn't") | **Speaker's face close-up**, often holding the prop | Close-up | **Mouth flaps** while speaking; pleading / grimace / happy | kid with the hammer pleading; nurse grimacing |
| 6 | Is a **threat / order** | **Two full figures**: the adult towering, leaning in and pointing; the kid small | Full figure, the adult cut off at the frame edge | angry ↔ scared | mom over the kid on purple; over the shoulder with a bat on hot orange |
| 7 | Is a **list** ("children playing, a man selling balloons, sunsets glowing gold") | **One shot per item**, each on a new colour | Full figure / wide | Each item does its one action | kids kicking a ball, balloon man, sunset |
| 8 | Is an **action verb** (swung, knocked, tap, moved) | The **action at its most extreme pose**, from an odd angle (top-down, from below the bunk, the fist alone) | Unusual angle, close | Effort face | hammer over the head seen from above; fist knocking with red impact ticks |
| 9 | Is a **feeling** (crying, sobbed, smiled through the pain, kept him going) | **Full figure or close-up with the emotion marks**: tear streams, gloom cap, blush, sparkle stars | Full figure for despair, extreme close-up for joy | cry / sob / content | squatting, crying on deep green; content face with 4 sparkle stars |
| 10 | Is a **result / aftermath** | **What is left**: shards on the floor, empty bed, dark window | Wide or insert on a dark colour (slate, navy, purple) | Absent, or alone | shards on navy; empty bunk under a dark window |
| 11 | Is a **time jump** ("months later", "then one day", "later") | **Calendar pages being crossed out**, or a sky with the sun moving | Insert | None | MARCH/APRIL/MAY crossed in red; sky with sun and clouds |
| 12 | Is the **twist reveal** ("saw only another wall", "He was blind", "admitted online") | **Extreme close-up of the proof**: the window turning into bricks, the eye's pupil turning to a dashed ring, the phone in the hands | Extreme close-up, static | Shock / regret | window glass → brick wall; dashed pupil |
| 13 | Is the **last line** | A **callback** to shot 1, or the main character alone in a spotlight | Same framing as shot 1, or a full figure in the middle | Sad, holding | boy back on the brick-red pillow; kid slumped on a chair in a spotlight |

## 5. Composition rules
- Characters are mostly centred. The adult is often **cropped by the frame edge** (the over-the-shoulder side) to look big.
- **Over the shoulder:** the foreground character's back or shoulder is cut off at the bottom corner, the other character is smaller mid-frame.
- Close-ups place the head in the upper-middle of the frame, with the body going off the bottom edge.
- Floating figures need no ground line. Several full figures are placed at slightly different heights for depth.
- Keep whole characters inside the safe zone (`safezone.fit`). Close-ups may run off the edges like the references.

## 6. Expression timing
- An expression snaps on the **key word** of the phrase, not at the start of the shot. Use `keyed(T, [(0, "smile"), (1.0, "stern")])`.
- Speakers flap their mouths **only on quotes** (`talk=True` for the speaker during the quote's words).
- Effects arrive on their word: a tear stream, a scribble, a sparkle, impact ticks.

## 7. How to plan a new voiceover
1. Get word times (`analysis/align_words.py`).
2. Split into phrases of 2-5 words. Each phrase is one shot of 0.8-2.0 s, cut **just before its key word** (about 0.1 s).
3. Tag each phrase with a rule from section 4, take its angle from section 2 and pick the background colour from `sets.MOOD` (warm / tension / sad...). Never repeat the previous shot's colour.
4. Pick 1-2 callbacks: the last shot reuses the first shot's framing and colour.
5. Add a visual event (scribble, plug pulled, sparkle, tear) inside shots longer than 1.5 s, so the picture keeps changing.
