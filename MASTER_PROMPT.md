# Master prompt: new voice + SRT → box-head style animated short

Open a new Claude Code chat on this repository (from any device: claude.ai/code or the Claude app → Code).
1. Attach your voiceover (mp3/wav) and the SRT.
2. Paste the text inside the box below.

```
I am attaching a voiceover and its SRT. Make a 9:16 animated short from it in exactly
the box-head style of this repository (flat 2D box-head characters, a flat colour per cut,
hard cuts, locked camera, sad C-minor piano bed). Latest example: animator/sample.py.

SETUP
- Run `bash setup.sh` (installs packages, ffmpeg and the analysis model).
- Read these first and follow them strictly:
  CLAUDE.md, style_bible.md, visual_grammar.md (all sections, especially 2 = camera angles
  and 4 = sentence -> shot), sound_design.md, assembler/README.md.
- Style code: animator/style.py (BoxChar + cast), animator/sets.py (backgrounds, sets, props,
  effects, MOOD palette), animator/angles.py (the only camera angles allowed).
- Template to copy: animator/sample.py (20 shots, one per phrase, static angle per shot,
  hard cuts, callback ending, SFX list at ~7 per 10 s).
  Do not change engine.py / style.py unless something is broken; add new props to sets.py.

STEP 1 - WORDS
- Strip any "(Transcribed by ...)" text from the SRT.
- Run `python3 analysis/align_words.py <voice> <subs.srt> output/<story_name>` for word timings.

STEP 2 - VISUAL PLAN
- Split the narration into phrases of 2-5 words: one shot each (0.8-2.0 s), cut just before the key word.
- Tag each phrase with a rule from visual_grammar.md section 4 and an angle from section 2
  (face / extreme / full / two / ots / insert / wide / bed / scenery / low).
- Show what is SAID, literally:
  - each noun gets its object as an insert;
  - a list gets one shot per item;
  - a time jump gets calendar pages crossed out;
  - a feeling gets a face with tears / stars / gloom;
  - the twist gets an extreme close-up of the proof.
- A new flat background colour from sets.MOOD at every cut (by mood, never the same twice in a row).
- The last shot repeats shot 1's angle and colour (callback; the Short loops).
- Safe zone: the WHOLE character and key props inside x 38-680, y 149-1013 (below y 678 only up to x 599).
  Call safezone.fit(SHOTS, sys.modules[__name__]) right before render(). Full-frame face/extreme/bed close-ups set safe=False.

STEP 3 - BUILD AND CHECK FRAMES
- Write animator/<story_name>.py (new props/sets go into sets.py).
- Before the full render: `(cd animator && python3 contact.py <story_name> ../output/<story_name>/contact.png)`
  and look at it. Fix anything small, cut off, hidden or outside the red safe-zone line.

STEP 4 - MY DEFAULTS
- No captions, no camera moves, no camera whoosh, hard cuts (render xfade=0, fade_in=0, fade_out=0).
- No lip-sync on narration; the speaker's mouth flaps only during a quoted line (talk= window).
- Limited animation: engine.ANIM_FPS = 8, engine.DRIFT = False, engine.VIGNETTE = 0.
- Music: music_sad.wav from animator/audio.py at --music-volume 0.19. SFX: --sfx-scale 0.3.
- Synthesised SFX and music only (animator/audio.py).

STEP 5 - MEASURE, THEN SEND
- analysis/new_visuals.py: a new visual every 1.2-1.6 s.
- analysis/flow.py on the animation: camera median under 1.5, non-camera motion 2.5-5.
- analysis/audio_ref.py on the final mp4:

  | Measure | Target |
  |---|---|
  | Music vs voice | -13.5 ± 2 dB, C minor |
  | SFX per 10 s | 5-8 |
  | SFX median vs voice | -3 to -10 dB |
  | SFX on cuts | 40-70% |

  If the music or SFX level is off, correct --music-volume / --sfx-scale with the formulas in
  sound_design.md section 3 and re-assemble (no re-render).
- Send me the final mp4, and commit and push the code (output/ is git-ignored).
- Tell me honestly what could not match the reference.
- For fixes later: patch only the needed shots, never regenerate everything.
```

## Notes
- Everything (engine, characters, sets, angles, rules, measured sound targets) is on `main`.
- The reference videos are not needed again. Their analysis is saved in:
  - `style_bible.md`
  - `visual_grammar.md`
  - `sound_design.md`
  - `analysis/ref_data/`
- To skip `setup.sh` in every new chat, paste `bash setup.sh` into the cloud environment's **Setup script** (session title bar → environment menu → Edit).
- A ~30 s video takes about 20-40 minutes in total: planning and drawing new props, then a render of under a minute, then checks.
- **No voice yet?** Write the script, then make a test voice with Piper TTS:
  - `pip install piper-tts`;
  - download the voice from the GitHub release `rhasspy/piper` v0.0.2, `voice-en-us-ryan-high.tar.gz`;
  - run `python3 -m piper -m en-us-ryan-high.onnx --length-scale 0.86 -f voice.wav`.

  A real voiceover sounds better.
