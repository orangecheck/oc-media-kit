"""Text → SVG path, so banner copy bakes into vector outlines (no runtime
font dependency — same philosophy as the glyph marks). Uses the bundled
family fonts under build/fonts/. Advance-width layout only (no GPOS kerning);
fine for the short wordmark / tagline / hostname strings the banners carry."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

FONTS = Path(__file__).resolve().parent / "fonts"

# Logical font names → bundled TTF.
_FILES = {
    "inter": "Inter-Regular.ttf",
    "inter-semibold": "Inter-SemiBold.ttf",
    "mono": "JetBrainsMono-Regular.ttf",
    "mono-medium": "JetBrainsMono-Medium.ttf",
}


@lru_cache(maxsize=None)
def _font(name: str) -> TTFont:
    return TTFont(FONTS / _FILES[name])


def text_to_path(
    s: str, font: str, size: float, x: float = 0.0, y: float = 0.0
) -> tuple[str, float]:
    """Return (svg_path_d, advance_width_px) for `s` set in `font` at `size`px,
    baseline-anchored at (x, y). Path is in user units ready to drop into an SVG.
    """
    tt = _font(font)
    upm = tt["head"].unitsPerEm
    scale = size / upm
    cmap = tt.getBestCmap()
    glyphs = tt.getGlyphSet()
    hmtx = tt["hmtx"]

    d_parts: list[str] = []
    pen_x = 0.0
    for ch in s:
        gname = cmap.get(ord(ch))
        if gname is None:
            gname = ".notdef"
        adv = hmtx[gname][0]
        pen = SVGPathPen(glyphs)
        glyphs[gname].draw(pen)
        d = pen.getCommands()
        if d:
            # Place this glyph: scale to px, flip Y (font up → svg down),
            # translate to the running pen position + baseline.
            tx = x + pen_x * scale
            d_parts.append(
                f'<path transform="translate({tx:.2f} {y:.2f}) '
                f'scale({scale:.5f} {-scale:.5f})" d="{d}"/>'
            )
        pen_x += adv
    return "\n".join(d_parts), pen_x * scale


def text_width(s: str, font: str, size: float) -> float:
    """Advance width in px for `s` set in `font` at `size`px."""
    tt = _font(font)
    scale = size / tt["head"].unitsPerEm
    cmap = tt.getBestCmap()
    hmtx = tt["hmtx"]
    total = 0.0
    for ch in s:
        gname = cmap.get(ord(ch), ".notdef")
        total += hmtx[gname][0]
    return total * scale
