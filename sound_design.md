# Sound design: what the box-head references do

Measured on the 2 reference videos with `analysis/audio_ref.py` (UVR MDX-Net voice/music split, SFX detection, key/tempo).

Raw data, including every SFX with its time, kind, loudness vs voice and spoken line, is in `analysis/ref_data/monitor.json` and `analysis/ref_data/window.json`.

Loudness is RMS in dB relative to the narration (0 dB = as loud as the voice).

## 1. Music (one sad piano/pluck bed, louder than in the kit's styles)

| What | monitor | window | **Rule for our videos** |
|---|---|---|---|
| Level vs voice | **−13.6 dB** | **−13.3 dB** | **−13.5 ± 2 dB**. Much louder than the kit's −20 dB: the music carries the emotion here |
| Key | C minor (0-15 s) → F minor (15-30 s) | C minor all along, the last 2.6 s resolve to C major | **C minor**, with an optional resolve to C major under the last line |
| Tempo | 91 bpm (the 133 reading is double-time) | 103 bpm (136 = double-time) | **~96 bpm** |
| Notes per second | 2.7 → 0.7 | 1.3-1.5 | **1.2-2** sparse notes/s |
| Drums (percussive share) | 0.01-0.05 | 0.12-0.17 | **None**: no beat, soft attacks only |
| Tone (energy share) | bass 0.39 / mid 0.47 / high 0.13 | bass 0.50 / mid 0.42 / high 0.08 | **Bass-heavy and warm**: sustained low piano chords, soft mid-range melody, nothing bright (centroid 1100-1600 Hz) |
| Shape | Starts at 0 s. Constant, except +4 dB from 8-17 s (the begging) and in the last 3 s | Constant (±2.5 dB) from 0 s to the end | One bed from the first frame. A gentle swell under the climax and the last line. It stops with the video (no fade tail) |

Our generator: `animator/audio.py music_sad(total, swell=(t0, t1), resolve_at=None)`. It plays C minor, 96 bpm, sustained soft piano chords over a warm bass, a sparse melody and a soft quarter-note arpeggio, with no drums. `python3 animator/audio.py <dir> <total>` writes it as `music_sad.wav`.

Measured on its own:
- 96 bpm, C minor;
- 1.8 notes/s, percussive share 0.04;
- bass/mid/high energy 0.46/0.48/0.06.

Measured in the sample mix (`output/sample/sample_final.mp4`, `--music-volume 0.19`):
- music **−13.6 dB** vs voice;
- C minor;
- brightness 1121 Hz;
- bass/mid/high 0.45/0.44/0.11.

## 2. SFX (few, loud, on cuts)

| What | monitor | window | Both | **Rule** |
|---|---|---|---|---|
| Count | 16 (5.4 / 10 s) | 24 (7.4 / 10 s) | 6.4 / 10 s | **5-8 per 10 s**: one on most cuts, not one per word |
| Median loudness vs voice | −9.6 dB | −1.8 dB | **−5.3 dB** (p25 −11, p75 −1) | **−3 to −10 dB**: the SFX are nearly as loud as the voice, and big hits are louder (up to +4 dB) |
| On a picture cut | **50%** | **67%** | 60% | **40-70% on cuts**: the pop marks the new picture (opposite to the kit's styles) |
| Length | | | median 0.08 s | Short and dry |

**Mix by kind** (40 SFX):

| Kind | Share | Loudness (median) | Used for | Our file (`audio.py`) |
|---|---|---|---|---|
| pop / snap / swish | 65% | −5 dB | **A new picture pops on** (each list item), a sparkle star, a scribble, a hand grabbing, a page | `pop.wav`, `snap.wav` (new), `swish.wav` (new) |
| tick / click | 15% | −13 dB | Plug pulled, phone, small taps, the knock's second hit | `tick.wav`, `click.wav` (new) |
| thud / boom | 12% | **0 dB** (loudest) | Knock on the bunk, "died", "blind", impact, a body dropped onto the bed | `thud.wav`, `knock.wav` (new) |
| ding / shine / sting | 8% | −10 dB | Monitor glint (rising shimmer), the hammer swing, "months later" (long noisy swish) | `shine.wav` (new), `sting_low.wav`, `swoosh_long.wav` (new) |

### Where the SFX land
- **On the cut into a new list item or prop:** "Children / man / sunsets" each got a pop exactly on the cut (-1 to -5 dB).
- **On each sparkle star** popping around the happy face: 4 pops 0.4 s apart.
- **On impacts:**
  - knock = pop + thud (+1 to +4 dB);
  - "died" = thud on the cut to the empty bed;
  - the nurses dropping the boy = thud;
  - "blind" = thud on the eye.
- **On the shine of a new object:** a rising shimmer when the monitor appears.
- **On a time skip:** a long swish (0.9 s) when the calendar pages appear.
- **Not on every cut:** about 40% of cuts are silent. Quiet emotional lines (sobbing, "smiled through the pain") have no SFX or only a soft tick.
- **No camera whoosh** (there is no camera move to whoosh).

## 3. Targets to check a render against
Run `python3 analysis/audio_ref.py final.mp4 subs.srt /tmp/check` and compare:

| Measure | Target |
|---|---|
| Music vs voice | **−13.5 ± 2 dB** |
| Music key | C minor (F minor or C major at the end also fine) |
| SFX per 10 s | **5-8** |
| SFX median vs voice | **−3 to −10 dB** |
| SFX on cuts | **40-70%** |
| Music percussive share | under 0.2 |

Defaults that hit these targets on the sample (Piper voice at −17.9 dB RMS):
- SFX cue volumes in the story: pop 0.6-0.8, thud 0.8-0.9, click/tick 0.6-0.7, shine 0.7, swoosh_long 0.8.
- Global SFX scale **0.3**: `--sfx-scale 0.3`.
- Music `music_sad.wav` at **`--music-volume 0.19`**.

Sample result:
- music −13.6 dB;
- SFX 6.4 per 10 s;
- SFX median −6.7 dB;
- 67% of SFX on cuts.

These factors are relative to the voice file's own loudness, so **measure every new mix and correct it**:
- new music volume = old volume x 10^((−13.5 − measured music dB) / 20);
- new SFX scale = old scale x 10^((−6.5 − measured SFX median dB) / 20).

One correction pass is usually enough.

Example: `animator/apple.py` with the user's real voiceover (−23.6 dB RMS, quieter than Piper).
- The first mix at 0.19 / 0.3 measured music −8.2 dB and SFX −0.3 dB.
- One correction gave **music 0.103 and SFX scale 0.147**.
- The SFX scale was then nudged to 0.18 so the quieter pops under the voice count. That moved SFX from 4.8 to 5.1 per 10 s.
- Final mix: music −13.4 dB, C minor, SFX 5.1 per 10 s, median −5.5 dB, 44% on cuts.
