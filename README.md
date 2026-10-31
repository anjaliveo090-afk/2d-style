# 2d-style: box-head flat 2D shorts from a voice + SRT

A toolkit that turns any voiceover and its SRT into a 9:16 (720x1280) animated short, drawn entirely in code (pycairo), in one fixed style measured from reference videos:
- flat 2D comic characters with rounded-box heads and one-piece onesie bodies, a thin black ink line, no shading;
- a new flat background colour at every hard cut, about every 1.3 s;
- a locked camera with a fixed set of measured angles (face close-up, extreme close-up, full figure, over the shoulder, prop insert, wide minimal set, in bed);
- limited animation (about 8 drawings per second);
- a sad C-minor piano bed about 13.5 dB under the voice, with a few loud SFX on cuts and impacts.

## Start a new video (the message for a new chat)
Attach your voiceover and SRT in a new Claude Code chat on this repo and send:

```
I am attaching a voiceover and its SRT. Run bash setup.sh, then read MASTER_PROMPT.md and follow the prompt inside it exactly.
```

## What's inside

| Path | What |
|---|---|
| `CLAUDE.md` | The workflow Claude follows for every voice + SRT |
| `MASTER_PROMPT.md` | The full prompt (steps, defaults, measured targets) |
| `style_bible.md` | The look: format, safe zone, characters in head-widths, expressions, palette, sets |
| `visual_grammar.md` | Pace and camera numbers, **the measured camera angles**, sentence type → shot table |
| `sound_design.md` | Measured music and SFX, targets, mix correction formulas |
| `animator/style.py` | `BoxChar` characters (same `draw()` signature as the kit's `Char2`) + the cast |
| `animator/sets.py` | Backgrounds, sets (box room, bunk/hospital bed, window, sunset), props, effect marks |
| `animator/angles.py` | The reference camera angles as placement helpers |
| `animator/sample.py` | Template story ("Mister Button", 23 s) |
| `animator/contact.py` | One-frame-per-shot contact sheet with the Shorts safe zone drawn |
| `animator/test_sheet.py` | Style check sheets (all expressions, poses, reference comparison) |
| `animator/thumbnail.py` | 1080x1920 + 1280x720 thumbnails (`--no-stroke` for a flat version) |
| `animator/engine.py`, `audio.py`, `safezone.py` | Renderer, synthesised SFX and music (`music_sad`), safe-zone fitting |
| `analysis/` | Reference analysis tools + `ref_data/*.json` (the measurements) |
| `assembler/assemble.py` | Mixes the animation, voice, music and SFX into the final mp4 |
| `reference_examples/` | Worked examples of the method from the toolkit's earlier styles (not this look) |

## Sample
```bash
bash setup.sh
O=output/sample; mkdir -p $O && cp examples/sample/voice.wav examples/sample/sample.srt $O/
python3 animator/audio.py $O/sfx 23.3
(cd animator && python3 sample.py ../$O/clips/animation.mp4 ../$O/cues.json ../$O/voice.wav)
python3 assembler/assemble.py --clips $O/clips --voice $O/voice.wav --sfx $O/cues.json --sfx-dir $O/sfx \
  --sfx-scale 0.3 --music $O/sfx/music_sad.wav --music-volume 0.19 --out $O/sample_final.mp4
```

## Limits
- This is 2D code animation. Pace, camera angles, colour logic, expressions and sound levels match the reference measurements closely.
- The hand-drawn wobble of the reference ink line is approximated.
- Only the style is copied, never the reference channel's characters, signature, text or audio.
