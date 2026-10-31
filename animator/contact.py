"""Contact sheet of a story before the full render: one frame per shot (at `at` of the shot,
default 0.7), after safezone.fit, with the Shorts safe zone drawn in red.
Usage: python3 contact.py <story_module> out.png [at=0.7]
The story module must define SHOTS (and may define TOTAL); engine settings for the box-head style
(DRIFT off, ANIM_FPS 8, no vignette) are applied here like in the story's __main__."""
import importlib
import sys

import cairo

import engine
import safezone
from engine import W, H


def main(name, out, at=0.7):
    engine.DRIFT = False
    engine.ANIM_FPS = 8
    engine.VIGNETTE = 0.0
    mod = importlib.import_module(name)
    shots = mod.SHOTS
    safezone.fit(shots, mod, verbose=False)
    tw, th = 180, 320
    cols = 7
    rows = (len(shots) + cols - 1) // cols
    sheet = cairo.ImageSurface(cairo.FORMAT_RGB24, cols * tw, rows * (th + 18))
    sc = cairo.Context(sheet)
    sc.set_source_rgb(1, 1, 1)
    sc.paint()
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    zone = [(safezone.X0, safezone.Y0), (safezone.X1, safezone.Y0), (safezone.X1, safezone.NOTCH_Y),
            (safezone.NOTCH_X, safezone.NOTCH_Y), (safezone.NOTCH_X, safezone.Y1), (safezone.X0, safezone.Y1)]
    for i, s in enumerate(shots):
        t = (s["end"] - s["start"]) * at
        engine._draw_shot(s, t, surf, None)
        c = cairo.Context(surf)
        c.move_to(*zone[0])
        for p in zone[1:]:
            c.line_to(*p)
        c.close_path()
        c.set_source_rgba(1, 0.1, 0.1, 0.8)
        c.set_line_width(3)
        c.stroke()
        x, y = (i % cols) * tw, (i // cols) * (th + 18)
        sc.save()
        sc.translate(x, y + 18)
        sc.scale(tw / W, th / H)
        sc.set_source_surface(surf, 0, 0)
        sc.paint()
        sc.restore()
        sc.set_source_rgb(0, 0, 0)
        sc.select_font_face("DejaVu Sans")
        sc.set_font_size(11)
        sc.move_to(x + 3, y + 13)
        sc.show_text(f"{i + 1} {s['start']:.2f}s {s['draw'].__name__} {s.get('angle', '')}")
    sheet.write_to_png(out)
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 0.7)
