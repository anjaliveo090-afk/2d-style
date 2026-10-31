# Project: box-head flat 2D shorts (voice + SRT → 9:16 animated short)

This repo turns a voiceover and its SRT into a 9:16 animated short in one fixed style:
- flat 2D comic characters with rounded-box heads and one-piece onesie bodies;
- a flat background colour that changes at every hard cut;
- a locked camera and limited animation;
- a sad C-minor piano bed with loud, sparse SFX.

The style was measured from 2 reference videos. Everything is drawn in code (pycairo) by `animator/`.

## Read first (every new video)
- `style_bible.md`: format, safe zone, characters in head-widths, expressions, palette, sets.
- `visual_grammar.md`:
  - §1 measured pace and camera;
  - **§2 the only camera angles allowed** (measured shot by shot, helpers in `animator/angles.py`);
  - §4 sentence type → shot table.
- `sound_design.md`: measured music and SFX, target numbers, how to correct the mix levels.
- Code:
  - `animator/style.py`: `BoxChar`, with the same `draw()` signature as the kit's `Char2`, plus the cast `MOM KID GAMER PATIENT FRIEND NURSE MAN OLDMAN DAD GIRL`;
  - `animator/sets.py`: backgrounds, sets, props, effect marks, `MOOD` palette;
  - `animator/angles.py`: the measured angles;
  - `animator/sample.py`: **the template to copy**.
- `reference_examples/` holds the toolkit's older styles as worked examples of the method (literal visual per phrase, word-timed shots, measured targets). **Do not use their characters or look here.**

## Workflow when the user gives voice + SRT
`O=output/<story>`. `output/` is git-ignored.

1. **Words.**
   - Strip "(Transcribed by …)" from the SRT.
   - `python3 analysis/align_words.py <voice> <subs.srt> $O` writes `$O/aligned.json` with a time for every word.
   - Spot-check the times against the SRT line starts.
2. **Plan the shots** with `visual_grammar.md`:
   - Split into phrases of 2-5 words, one shot each (0.8-2.0 s). Cut about 0.1 s before the key word.
   - Tag each phrase with a §4 rule and take its **angle from §2** (`face / extreme / full / two / ots / insert / wide / bed / scenery / low`).
   - Pick a background colour from `sets.MOOD` by mood. Never repeat the previous shot's colour.
   - Show what is said literally (a noun gets its object, a list gets one shot per item, a time skip gets a calendar).
   - The last shot is a callback to shot 1 (same angle and colour).
3. **Build** `animator/<story>.py` by copying `animator/sample.py`:
   - Keep the shot helper `shot(start, draw, angle, ...)` with static `ang.cam(start)` keys and `vignette=0`.
   - Keep the `__main__`:
     - `engine.DRIFT = False`, `engine.ANIM_FPS = 8`, `engine.VIGNETTE = 0`;
     - `safezone.fit(SHOTS, sys.modules[__name__])` right before `render()`;
     - `render(..., xfade=0.0, grain=0, fade_in=0.0, fade_out=0.0)`: hard cuts, no fades, loops back to shot 1.
   - Add new props or sets to `sets.py` and new characters as `BoxChar(colour, hair=..., build=...)`.
   - Expressions snap on the key word (`keyed`).
   - Give the speaker `talk=` only during a **quoted line**.
4. **Check a contact sheet with the safe zone drawn** before rendering: `(cd animator && python3 contact.py <story> ../$O/contact.png)`. Look at it.
   - Whole characters and key props must sit inside the red zone: x 38-680, y 149-1013, and below y 678 only up to x 599. Add `keep=[(x0, y0, x1, y1)]` for key props.
   - Deliberate face, extreme and in-bed close-ups that fill the frame like the references set `safe=False`.
   - Fix anything cut off, hidden, too small or unreadable.
5. **Render and assemble.** TOTAL is the voice length plus about 0.4 s.
   ```bash
   python3 animator/audio.py $O/sfx <TOTAL>
   (cd animator && python3 <story>.py ../$O/clips/animation.mp4 ../$O/cues.json ../<voice>)
   python3 assembler/assemble.py --clips $O/clips --voice <voice> --sfx $O/cues.json --sfx-dir $O/sfx \
     --sfx-scale 0.3 --music $O/sfx/music_sad.wav --music-volume 0.19 --xfade 0.1 --out $O/<story>_final.mp4
   ```
   - The render takes about 1 s per second of video.
   - `--xfade` does nothing with a single clip.
   - No `--srt`, so no captions.
6. **Measure** against the targets and fix anything outside them:
   - `python3 analysis/new_visuals.py $O/clips/animation.mp4`: a new visual every **1.2-1.6 s**, no gap over 2.6 s.
   - `python3 analysis/flow.py $O/clips/animation.mp4`:
     - camera median **< 1.5**;
     - camera mean 1-5;
     - non-camera motion **2.5-5** (the references measure 3.3-3.4).
   - `python3 analysis/audio_ref.py $O/<story>_final.mp4 <subs.srt> $O/check`:
     - music **−13.5 ± 2 dB**, C minor;
     - SFX **5-8 per 10 s**, median **−3 to −10 dB**, **40-70% on cuts**.
   - Correct the music volume and SFX scale with the formulas in `sound_design.md` §3, then re-assemble (no re-render needed).
7. **Send the mp4** to the user, with the measured numbers and anything that could not match.
8. **Fix requests:** patch only the shots that need it (their `s_*` functions, times or SFX lines), then re-render and re-assemble. Never rewrite the whole story.

## Defaults (change only if the user asks)
- **No captions.** If wanted, add `--srt <word srt> --words 1`; the references show one word at a time, centred.
- **No lip-sync on narration.** The references only flap the speaker's mouth during quoted lines (`talk=` window). Do the same.
- **No camera whoosh** and no camera moves. The references cut.
- Synthesised SFX and music only (`animator/audio.py`), never files from the reference channel.
- Copy the style only: never the reference channel's characters, signature/logo, text or audio.

## Thumbnails (when asked)
`animator/thumbnail.py` (template = the sample story):
- one huge emotional face;
- the opponent;
- 2-3 words of text;
- a bright burst.

`python3 animator/thumbnail.py $O/thumbs` writes 1080x1920 and 1280x720. Add `--no-stroke` for a flat version without the white sticker outline (closer to the video style).

## Honest limits
This is 2D code animation. Pace, angles, colour logic, expressions and sound levels match the measurements closely. The hand-drawn wobble of the references' ink line is approximated by slightly uneven box heads and a constant thin pen.

## New reference videos
Run the analysis tools and add what you learn to the three .md files and `analysis/ref_data/`:
- `analysis/frame_log.py <video> <srt> <out> 4`: look at every sheet;
- `analysis/audio_ref.py <video> <srt> <out>`;
- `analysis/new_visuals.py <video>`;
- `analysis/flow.py <video>`.
