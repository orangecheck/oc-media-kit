#!/usr/bin/env python3
"""
build_kit.py — generate all OrangeCheck § mark variants, pixel-perfect.

Pipeline:
  1. Extract the § glyph from DejaVu Sans Mono Bold as real SVG path data.
     The resulting SVGs do NOT depend on any installed font at render time.
  2. For each variant, render a high-resolution master PNG (2048px square,
     or 2400x1260 for the OG format) via cairosvg.
  3. Downsample to every target size with PIL's LANCZOS filter.
     This gives clean, anti-aliased edges at every size including 16x16.

Run:
    pip install cairosvg Pillow fonttools
    python3 build_kit.py
"""
import os
import io
import cairosvg
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

OUT = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

ORANGE = "#f97316"
BLACK  = "#0a0a0a"
WHITE  = "#fafafa"

SQUARE = 1024                                    # native svg canvas size
SQUARE_PNG_SIZES = [16, 32, 48, 64, 128, 180, 192, 256, 512, 1024]
OG_W, OG_H = 1200, 630

# supersample master size — render once, downsample to all targets
MASTER_SQUARE = 2048
MASTER_OG     = (2400, 1260)


# ---- glyph extraction ------------------------------------------------------

def extract_section_glyph(font_path):
    """Pull § from a TTF and return the path + bounding box in font units."""
    font = TTFont(font_path)
    cmap = font.getBestCmap()
    glyph_name = cmap[ord("§")]
    glyph_set = font.getGlyphSet()

    pen = SVGPathPen(glyph_set)
    glyph_set[glyph_name].draw(pen)
    path_d = pen.getCommands()

    g = font["glyf"][glyph_name]
    bbox = (g.xMin, g.yMin, g.xMax, g.yMax)
    return path_d, bbox

GLYPH_D, GLYPH_BBOX = extract_section_glyph(FONT_PATH)


def section_path(canvas_w, canvas_h, fg, target_frac):
    """Return SVG <path> for § scaled to `target_frac` of canvas, centered."""
    x_min, y_min, x_max, y_max = GLYPH_BBOX
    glyph_w = x_max - x_min
    glyph_h = y_max - y_min

    smaller = min(canvas_w, canvas_h)
    scale = (smaller * target_frac) / max(glyph_w, glyph_h)

    # SVG y-down; font y-up. Flip y in the scale, then center.
    tx = (canvas_w - scale * (x_max + x_min)) / 2
    ty = (canvas_h + scale * (y_max + y_min)) / 2

    return (f'<path d="{GLYPH_D}" fill="{fg}" '
            f'transform="translate({tx:.4f} {ty:.4f}) '
            f'scale({scale:.6f} -{scale:.6f})"/>')


# ---- svg templates ---------------------------------------------------------

def svg_square(fg, bg):
    return (f'<svg viewBox="0 0 {SQUARE} {SQUARE}" xmlns="http://www.w3.org/2000/svg" '
            f'role="img" aria-label="OrangeCheck mark">\n'
            f'  <rect width="{SQUARE}" height="{SQUARE}" fill="{bg}"/>\n'
            f'  {section_path(SQUARE, SQUARE, fg, 0.78)}\n'
            f'</svg>\n')


def svg_rounded(fg, bg, radius_pct=0.22):
    r = int(SQUARE * radius_pct)
    return (f'<svg viewBox="0 0 {SQUARE} {SQUARE}" xmlns="http://www.w3.org/2000/svg" '
            f'role="img" aria-label="OrangeCheck mark">\n'
            f'  <rect width="{SQUARE}" height="{SQUARE}" rx="{r}" ry="{r}" fill="{bg}"/>\n'
            f'  {section_path(SQUARE, SQUARE, fg, 0.78)}\n'
            f'</svg>\n')


def svg_safearea(fg, bg):
    return (f'<svg viewBox="0 0 {SQUARE} {SQUARE}" xmlns="http://www.w3.org/2000/svg" '
            f'role="img" aria-label="OrangeCheck mark, safe area">\n'
            f'  <rect width="{SQUARE}" height="{SQUARE}" fill="{bg}"/>\n'
            f'  {section_path(SQUARE, SQUARE, fg, 0.55)}\n'
            f'</svg>\n')


def svg_circle(fg, bg):
    return (f'<svg viewBox="0 0 {SQUARE} {SQUARE}" xmlns="http://www.w3.org/2000/svg" '
            f'role="img" aria-label="OrangeCheck mark, circular">\n'
            f'  <circle cx="{SQUARE//2}" cy="{SQUARE//2}" r="{SQUARE//2}" fill="{bg}"/>\n'
            f'  {section_path(SQUARE, SQUARE, fg, 0.55)}\n'
            f'</svg>\n')


def svg_transparent(fg):
    return (f'<svg viewBox="0 0 {SQUARE} {SQUARE}" xmlns="http://www.w3.org/2000/svg" '
            f'role="img" aria-label="OrangeCheck mark">\n'
            f'  {section_path(SQUARE, SQUARE, fg, 0.86)}\n'
            f'</svg>\n')


def svg_og(fg, bg):
    return (f'<svg viewBox="0 0 {OG_W} {OG_H}" xmlns="http://www.w3.org/2000/svg" '
            f'role="img" aria-label="OrangeCheck mark">\n'
            f'  <rect width="{OG_W}" height="{OG_H}" fill="{bg}"/>\n'
            f'  {section_path(OG_W, OG_H, fg, 0.65)}\n'
            f'</svg>\n')


# ---- variant manifest ------------------------------------------------------

SQUARE_VARIANTS = [
    ("01-square-orange-on-dark",    svg_square(ORANGE, BLACK)),
    ("02-square-orange-on-light",   svg_square(ORANGE, WHITE)),
    ("03-square-white-on-orange",   svg_square(WHITE,  ORANGE)),
    ("04-square-black-on-orange",   svg_square(BLACK,  ORANGE)),
    ("05-rounded-orange-on-dark",   svg_rounded(ORANGE, BLACK)),
    ("06-rounded-orange-on-light",  svg_rounded(ORANGE, WHITE)),
    ("07-rounded-white-on-orange",  svg_rounded(WHITE,  ORANGE)),
    ("08-rounded-black-on-orange",  svg_rounded(BLACK,  ORANGE)),
    ("09-safearea-orange-on-dark",  svg_safearea(ORANGE, BLACK)),
    ("10-safearea-orange-on-light", svg_safearea(ORANGE, WHITE)),
    ("11-safearea-white-on-orange", svg_safearea(WHITE,  ORANGE)),
    ("12-safearea-black-on-orange", svg_safearea(BLACK,  ORANGE)),
    ("13-circle-orange-on-dark",    svg_circle(ORANGE, BLACK)),
    ("14-circle-white-on-orange",   svg_circle(WHITE,  ORANGE)),
    ("15-circle-black-on-orange",   svg_circle(BLACK,  ORANGE)),
    ("16-transparent-orange",       svg_transparent(ORANGE)),
    ("17-transparent-black",        svg_transparent(BLACK)),
    ("18-transparent-white",        svg_transparent(WHITE)),
]

OG_VARIANTS = [
    ("19-og-orange-on-dark",        svg_og(ORANGE, BLACK)),
    ("20-og-white-on-orange",       svg_og(WHITE,  ORANGE)),
    ("21-og-black-on-orange",       svg_og(BLACK,  ORANGE)),
]


# ---- rendering -------------------------------------------------------------

def render_master(svg_text, master_w, master_h):
    """Render SVG to a high-res PIL image (the supersampling master)."""
    png_bytes = cairosvg.svg2png(
        bytestring=svg_text.encode("utf-8"),
        output_width=master_w,
        output_height=master_h,
    )
    return Image.open(io.BytesIO(png_bytes)).convert("RGBA")


def downsample(master_img, target_w, target_h):
    """Resize master to target with LANCZOS for clean small-size output."""
    if master_img.size == (target_w, target_h):
        return master_img.copy()
    return master_img.resize((target_w, target_h), Image.LANCZOS)


def main():
    svgs = pngs = 0

    # write all 21 svgs
    for stem, svg_text in SQUARE_VARIANTS + OG_VARIANTS:
        with open(os.path.join(OUT, f"{stem}.svg"), "w") as f:
            f.write(svg_text)
        svgs += 1

    # square variants: render once at 2048, downsample to each target
    for stem, svg_text in SQUARE_VARIANTS:
        master = render_master(svg_text, MASTER_SQUARE, MASTER_SQUARE)
        for s in SQUARE_PNG_SIZES:
            img = downsample(master, s, s)
            img.save(os.path.join(OUT, f"{stem}-{s}x{s}.png"), optimize=True)
            pngs += 1
        print(f"  {stem}: 1 svg + {len(SQUARE_PNG_SIZES)} pngs")

    # og variants: 2400x1260 master, downsample to 1200x630
    for stem, svg_text in OG_VARIANTS:
        master = render_master(svg_text, *MASTER_OG)
        img = downsample(master, OG_W, OG_H)
        img.save(os.path.join(OUT, f"{stem}-{OG_W}x{OG_H}.png"), optimize=True)
        pngs += 1
        print(f"  {stem}: 1 svg + 1 png ({OG_W}x{OG_H})")

    print(f"\ndone. {svgs} svgs + {pngs} pngs.")


if __name__ == "__main__":
    main()
