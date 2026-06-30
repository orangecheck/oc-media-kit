#!/usr/bin/env python3
"""
build.py — regenerate the entire OrangeCheck media kit from brands.py.

Pipeline per brand:

  1.  Compose a variant SVG by wrapping the brand's glyph in a backdrop
      (sharp square, rounded square, safe-area, circle, transparent, or
      og 1200x630 panel).
  2.  Write the SVG to dist/<brand>/svg/<variant>.svg.
  3.  Render a high-resolution master PNG via cairosvg, then downsample
      with PIL's LANCZOS filter to every target size in SQUARE_PNG_SIZES.
  4.  Emit:
        - dist/<brand>/png/<variant>-<W>x<H>.png  (all sizes, all variants)
        - dist/<brand>/og/<variant>-1200x630.png  (OG cards)
        - dist/<brand>/favicon/favicon.ico        (multi-resolution)
        - dist/<brand>/favicon/favicon-{16,32}x{16,32}.png
        - dist/<brand>/favicon/favicon-48x48.png  (toolbar)
        - dist/<brand>/favicon/apple-touch-icon.png (180x180)
        - dist/<brand>/favicon/android-chrome-{192,512}x{192,512}.png
        - dist/<brand>/favicon/favicon.svg        (canonical svg)
        - dist/<brand>/favicon/site.webmanifest
  5.  Finally, emit manifest.json at the repo root, indexing every output.

Run:
    pip install -r build/requirements.txt
    python3 build/build.py
"""
from __future__ import annotations
import io
import json
import shutil
from pathlib import Path

import cairosvg
from PIL import Image

# Pillow ≥9 routes resampling filters through Image.Resampling; older
# code paths still expose Image.LANCZOS as a deprecation alias. We pin
# to the new namespace.
LANCZOS = Image.Resampling.LANCZOS

from brands import (
    BRANDS,
    Brand,
    CANVAS,
    DARK,
    DEFAULT_SKIN,
    LIGHT,
    MASTER_OG,
    MASTER_SQUARE,
    OG_H,
    OG_W,
    ORANGE,
    SKINS,
    SQUARE_PNG_SIZES,
)

import aurorabanner as banner
import auroramark as au
import youtube as yt

REPO = Path(__file__).resolve().parent.parent
DIST = REPO / "dist"

# Aurora aperture marks are showcase/marketing assets (never favicons — the
# field turns to mud at 16px), so alternate skins render them at a couple of
# display sizes rather than the full 16–1024 favicon ladder. The default skin
# still rides the standard ladder via full_png.
AURORA_SHOWCASE_SIZES = [256, 512]


# ---------------------------------------------------------------------------
# SVG variant wrappers — compose a glyph + backdrop into a full mark SVG.
# ---------------------------------------------------------------------------

def _svg(body: str, w: int = CANVAS, h: int = CANVAS, label: str = "") -> str:
    return (
        f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="{label}">\n  {body}\n</svg>\n'
    )


def variant_square(brand: Brand, fg: str, bg: str, ink: str,
                   label: str) -> str:
    """Sharp-cornered square: backdrop + glyph at full size."""
    return _svg(
        f'<rect width="{CANVAS}" height="{CANVAS}" fill="{bg}"/>\n  '
        + brand.glyph(fg, bg, ink, CANVAS),
        label=label,
    )


def variant_rounded(brand: Brand, fg: str, bg: str, ink: str,
                    label: str, radius_pct: float = 0.22) -> str:
    """Rounded square (iOS home-screen vibe)."""
    r = int(CANVAS * radius_pct)
    return _svg(
        f'<rect width="{CANVAS}" height="{CANVAS}" rx="{r}" ry="{r}" fill="{bg}"/>\n  '
        + brand.glyph(fg, bg, ink, CANVAS),
        label=label,
    )


def variant_circle(brand: Brand, fg: str, bg: str, ink: str,
                   label: str) -> str:
    """Circular backdrop (social avatars)."""
    return _svg(
        f'<circle cx="{CANVAS // 2}" cy="{CANVAS // 2}" r="{CANVAS // 2}" fill="{bg}"/>\n  '
        + brand.glyph(fg, bg, ink, CANVAS),
        label=label,
    )


def variant_safearea(brand: Brand, fg: str, bg: str, ink: str,
                     label: str, inset_pct: float = 0.20) -> str:
    """Padded square — used for OAuth tiles and extension store assets.
    Inner glyph is rendered at (CANVAS - 2*inset) and translated."""
    inset = int(CANVAS * inset_pct)
    inner = CANVAS - 2 * inset
    # We render the glyph against a temporary CANVAS=`inner` and translate.
    inner_body = brand.glyph(fg, bg, ink, inner)
    return _svg(
        f'<rect width="{CANVAS}" height="{CANVAS}" fill="{bg}"/>\n  '
        f'<g transform="translate({inset} {inset})">\n    {inner_body}\n  </g>',
        label=label,
    )


def variant_transparent(brand: Brand, fg: str, ink: str, label: str) -> str:
    """No backdrop — just the mark on transparency."""
    return _svg(brand.glyph(fg, "none", ink, CANVAS), label=label)


def variant_og(brand: Brand, fg: str, bg: str, ink: str, label: str) -> str:
    """1200×630 share card — backdrop fills full panel, glyph centered."""
    glyph_size = int(min(OG_W, OG_H) * 0.55)
    tx = (OG_W - glyph_size) // 2
    ty = (OG_H - glyph_size) // 2
    glyph_body = brand.glyph(fg, bg, ink, glyph_size)
    return (
        f'<svg viewBox="0 0 {OG_W} {OG_H}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="{label}">\n'
        f'  <rect width="{OG_W}" height="{OG_H}" fill="{bg}"/>\n'
        f'  <g transform="translate({tx} {ty})">\n    {glyph_body}\n  </g>\n'
        f'</svg>\n'
    )


# ---------------------------------------------------------------------------
# Aurora aperture variants — the brand glyph filled with the bitcoin-aurora
# field (auroramark.py). `mode` drives the aperture base tint + field opacity
# (the surface the mark sits on); `ink` drives the engraving contrast, set
# independently so a light-ink mark can still ride a dark base.
# ---------------------------------------------------------------------------

def _au_uid(stem: str) -> str:
    return "x" + stem.replace("-", "")


def variant_aurora_square(brand: Brand, accent: str, bg: str, ink: str,
                          mode: str, label: str) -> str:
    return _svg(
        f'<rect width="{CANVAS}" height="{CANVAS}" fill="{bg}"/>\n  '
        + au.aurora_glyph(brand, accent, ink, mode, CANVAS, _au_uid(label)),
        label=label,
    )


def variant_aurora_rounded(brand: Brand, accent: str, bg: str, ink: str,
                           mode: str, label: str, radius_pct: float = 0.22) -> str:
    r = int(CANVAS * radius_pct)
    return _svg(
        f'<rect width="{CANVAS}" height="{CANVAS}" rx="{r}" ry="{r}" fill="{bg}"/>\n  '
        + au.aurora_glyph(brand, accent, ink, mode, CANVAS, _au_uid(label)),
        label=label,
    )


def variant_aurora_circle(brand: Brand, accent: str, bg: str, ink: str,
                          mode: str, label: str) -> str:
    return _svg(
        f'<circle cx="{CANVAS // 2}" cy="{CANVAS // 2}" r="{CANVAS // 2}" fill="{bg}"/>\n  '
        + au.aurora_glyph(brand, accent, ink, mode, CANVAS, _au_uid(label)),
        label=label,
    )


def variant_aurora_safearea(brand: Brand, accent: str, bg: str, ink: str,
                            mode: str, label: str, inset_pct: float = 0.20) -> str:
    inset = int(CANVAS * inset_pct)
    inner = CANVAS - 2 * inset
    inner_body = au.aurora_glyph(brand, accent, ink, mode, inner, _au_uid(label))
    return _svg(
        f'<rect width="{CANVAS}" height="{CANVAS}" fill="{bg}"/>\n  '
        f'<g transform="translate({inset} {inset})">\n    {inner_body}\n  </g>',
        label=label,
    )


def variant_aurora_transparent(brand: Brand, accent: str, ink: str,
                               mode: str, label: str) -> str:
    return _svg(
        au.aurora_glyph(brand, accent, ink, mode, CANVAS, _au_uid(label)),
        label=label,
    )


def variant_aurora_og(brand: Brand, accent: str, bg: str, ink: str,
                      mode: str, label: str) -> str:
    glyph_size = int(min(OG_W, OG_H) * 0.55)
    tx = (OG_W - glyph_size) // 2
    ty = (OG_H - glyph_size) // 2
    glyph_body = au.aurora_glyph(brand, accent, ink, mode, glyph_size, _au_uid(label))
    return (
        f'<svg viewBox="0 0 {OG_W} {OG_H}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="{label}">\n'
        f'  <rect width="{OG_W}" height="{OG_H}" fill="{bg}"/>\n'
        f'  <g transform="translate({tx} {ty})">\n    {glyph_body}\n  </g>\n'
        f'</svg>\n'
    )


# ---------------------------------------------------------------------------
# Per-brand variant manifest
# ---------------------------------------------------------------------------

def variants_for(brand: Brand, primary: str) -> list[tuple[str, str, tuple[int, int]]]:
    """Return [(stem, svg_text, (w, h))]. Square variants render to
    1024x1024; OG variants render to 1200x630."""
    out: list[tuple[str, str, tuple[int, int]]] = []
    label = f"{brand.label} mark"

    # ---- standard variants present on every brand ----
    out.append((
        "square-on-dark",
        variant_square(brand, primary, DARK, DARK, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "square-on-light",
        variant_square(brand, primary, LIGHT, DARK, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "rounded-on-dark",
        variant_rounded(brand, primary, DARK, DARK, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "rounded-on-light",
        variant_rounded(brand, primary, LIGHT, DARK, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "safearea-on-dark",
        variant_safearea(brand, primary, DARK, DARK, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "safearea-on-light",
        variant_safearea(brand, primary, LIGHT, DARK, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "circle-on-dark",
        variant_circle(brand, primary, DARK, DARK, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "circle-on-light",
        variant_circle(brand, primary, LIGHT, DARK, label),
        (CANVAS, CANVAS),
    ))
    # ---- white/black on orange (every brand) ----
    # For glyph-only brands (single-color shape) this is "white glyph on orange"
    # or "black glyph on orange" — the natural inversion.
    # For full-mark brands (which already have an orange surface) we render the
    # whole mark as a single-color silhouette on the orange backdrop, accepting
    # the loss of inner detail as a deliberate stylization. The orange-on-orange
    # blend it would otherwise produce is unusable.
    out.append((
        "square-white-on-orange",
        variant_square(brand, LIGHT, primary, LIGHT, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "square-black-on-orange",
        variant_square(brand, DARK, primary, DARK, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "rounded-white-on-orange",
        variant_rounded(brand, LIGHT, primary, LIGHT, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "rounded-black-on-orange",
        variant_rounded(brand, DARK, primary, DARK, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "circle-white-on-orange",
        variant_circle(brand, LIGHT, primary, LIGHT, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "circle-black-on-orange",
        variant_circle(brand, DARK, primary, DARK, label),
        (CANVAS, CANVAS),
    ))

    # ---- transparent matrix (every brand) ----
    #
    # Eight flavors. The naming is uniform across every brand even when two
    # entries technically render identically (e.g. for glyph-only brands the
    # mono and outline variants are the same since there's no outer surface
    # to drop). The duplication is deliberate — consumers can pick by
    # semantic intent without per-brand lookup tables.
    #
    #   transparent           — natural bicolor (orange surface + dark detail).
    #                            Default · use on light surfaces.
    #   transparent-light-ink — bicolor with light detail (orange + light).
    #                            Use on dark surfaces where dark ink would die.
    #   transparent-mono-orange — full silhouette in orange (filled). Useful
    #                              as a watermark / mask layer.
    #   transparent-mono-dark   — full silhouette in dark.
    #   transparent-mono-light  — full silhouette in light.
    #   transparent-outline-orange — outer surface dropped, only the distinct
    #                                inner detail in orange. Useful when the
    #                                family chrome (orange square) would
    #                                duplicate a chrome the host already provides.
    #   transparent-outline-dark
    #   transparent-outline-light
    #
    # For glyph-only brands (orangecheck §, vote bars) the "outline" rendering
    # collapses to the same as "mono" (there's no outer surface to drop) —
    # but we still emit the file so every brand has identical surface.
    out.append((
        "transparent",
        variant_transparent(brand, primary, DARK, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "transparent-light-ink",
        variant_transparent(brand, primary, LIGHT, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "transparent-mono-orange",
        variant_transparent(brand, primary, primary, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "transparent-mono-dark",
        variant_transparent(brand, DARK, DARK, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "transparent-mono-light",
        variant_transparent(brand, LIGHT, LIGHT, label),
        (CANVAS, CANVAS),
    ))
    # Outline variants drop the outer "surface" by passing fg="none" to the
    # glyph. For most brands this strips the filled orange square and leaves
    # only the distinctive inner detail (frame + glyph). For glyph-only
    # brands the glyph IS the surface, so fg="none" would erase everything
    # — we fall back to mono rendering in that case.
    outline_fg_orange = primary if brand.is_glyph_only else "none"
    outline_fg_dark = DARK if brand.is_glyph_only else "none"
    outline_fg_light = LIGHT if brand.is_glyph_only else "none"
    out.append((
        "transparent-outline-orange",
        variant_transparent(brand, outline_fg_orange, primary, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "transparent-outline-dark",
        variant_transparent(brand, outline_fg_dark, DARK, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "transparent-outline-light",
        variant_transparent(brand, outline_fg_light, LIGHT, label),
        (CANVAS, CANVAS),
    ))

    # ---- OG cards (every brand) ----
    # Bicolor on dark and light backdrops, plus a mono white-on-orange OG
    # for the share surface where you want the family color to fill-bleed.
    out.append((
        "og-on-dark",
        variant_og(brand, primary, DARK, DARK, label),
        (OG_W, OG_H),
    ))
    out.append((
        "og-on-light",
        variant_og(brand, primary, LIGHT, DARK, label),
        (OG_W, OG_H),
    ))
    out.append((
        "og-white-on-orange",
        variant_og(brand, LIGHT, primary, LIGHT, label),
        (OG_W, OG_H),
    ))
    out.append((
        "og-black-on-orange",
        variant_og(brand, DARK, primary, DARK, label),
        (OG_W, OG_H),
    ))

    # ---- aurora aperture matrix (every brand, recolours per skin) ----
    #
    # The mark filled with the bitcoin-aurora field — the per-skin accent leads,
    # green/blue bleed (auroramark.py). `mode` is the surface tone (base tint +
    # field opacity); `ink` is the engraving, decoupled so a light-ink mark can
    # ride a dark base. The accent is the skin `primary`, so this whole block
    # recolours orange → phosphor → lightning → gold exactly like <OcAurora/>.
    al = f"{brand.label} aurora mark"
    out.append((
        "aurora-on-dark",
        variant_aurora_square(brand, primary, DARK, DARK, "dark", al),
        (CANVAS, CANVAS),
    ))
    out.append((
        "aurora-on-light",
        variant_aurora_square(brand, primary, LIGHT, DARK, "light", al),
        (CANVAS, CANVAS),
    ))
    out.append((
        "aurora-rounded-on-dark",
        variant_aurora_rounded(brand, primary, DARK, DARK, "dark", al),
        (CANVAS, CANVAS),
    ))
    out.append((
        "aurora-rounded-on-light",
        variant_aurora_rounded(brand, primary, LIGHT, DARK, "light", al),
        (CANVAS, CANVAS),
    ))
    out.append((
        "aurora-circle-on-dark",
        variant_aurora_circle(brand, primary, DARK, DARK, "dark", al),
        (CANVAS, CANVAS),
    ))
    out.append((
        "aurora-circle-on-light",
        variant_aurora_circle(brand, primary, LIGHT, DARK, "light", al),
        (CANVAS, CANVAS),
    ))
    out.append((
        "aurora-safearea-on-dark",
        variant_aurora_safearea(brand, primary, DARK, DARK, "dark", al),
        (CANVAS, CANVAS),
    ))
    out.append((
        "aurora-safearea-on-light",
        variant_aurora_safearea(brand, primary, LIGHT, DARK, "light", al),
        (CANVAS, CANVAS),
    ))
    # Transparent aurora marks: the glyph filled with the field on no backdrop.
    # `transparent` rides a light base (drop on light surfaces); the `-light-ink`
    # twin rides a dark base with light engraving (drop on dark surfaces).
    out.append((
        "aurora-transparent",
        variant_aurora_transparent(brand, primary, DARK, "light", al),
        (CANVAS, CANVAS),
    ))
    out.append((
        "aurora-transparent-light-ink",
        variant_aurora_transparent(brand, primary, LIGHT, "dark", al),
        (CANVAS, CANVAS),
    ))
    out.append((
        "aurora-og-on-dark",
        variant_aurora_og(brand, primary, DARK, DARK, "dark", al),
        (OG_W, OG_H),
    ))
    out.append((
        "aurora-og-on-light",
        variant_aurora_og(brand, primary, LIGHT, DARK, "light", al),
        (OG_W, OG_H),
    ))

    return out


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render_master(svg_text: str, master_w: int, master_h: int) -> Image.Image:
    png = cairosvg.svg2png(
        bytestring=svg_text.encode("utf-8"),
        output_width=master_w,
        output_height=master_h,
    )
    assert png is not None, "cairosvg returned no bytes"
    return Image.open(io.BytesIO(png)).convert("RGBA")


def downsample(master: Image.Image, w: int, h: int) -> Image.Image:
    if master.size == (w, h):
        return master.copy()
    return master.resize((w, h), LANCZOS)


# ---------------------------------------------------------------------------
# Per-brand build
# ---------------------------------------------------------------------------

def build_brand(brand: Brand, primary: str, bdir: Path, full_png: bool = True) -> dict:
    """Build every variant for one brand into `bdir`, using `primary` as the
    accent color. Returns a manifest entry. `bdir` is dist/<brand>/ for the
    default skin and dist/<brand>/skins/<skin>/ for alternates.

    `full_png=False` (used for alternate skins) writes all 26 vector SVGs + the
    favicon bundle + the OG card PNGs, but skips the 10-size square PNG raster
    ladder — the favicon/OG are the consumable theme-aware assets, and the
    marketing SVGs scale losslessly, so 4×-ing ~2.7k PNGs into git is avoided."""
    svg_dir = bdir / "svg"
    png_dir = bdir / "png"
    og_dir = bdir / "og"
    fav_dir = bdir / "favicon"
    for d in (svg_dir, png_dir, og_dir, fav_dir):
        d.mkdir(parents=True, exist_ok=True)

    entry = {
        "slug": brand.slug,
        "label": brand.label,
        "hostname": brand.hostname,
        "tagline": brand.tagline,
        "variants": {},
        "favicon": {},
        "og": {},
    }
    svg_paths: dict[str, Path] = {}

    for stem, svg_text, (w, h) in variants_for(brand, primary):
        # 1. write the source SVG (vector, scales to anything)
        svg_path = svg_dir / f"{stem}.svg"
        svg_path.write_text(svg_text)
        svg_paths[stem] = svg_path

        # 2. render a master + downsample
        if (w, h) == (OG_W, OG_H):
            # OG card — single output at 1200×630
            master = render_master(svg_text, *MASTER_OG)
            out = og_dir / f"{stem}-{OG_W}x{OG_H}.png"
            downsample(master, OG_W, OG_H).save(out, optimize=True)
            entry["og"][stem] = str(out.relative_to(REPO))
            entry["variants"].setdefault(stem, {"svg": str(svg_path.relative_to(REPO)), "png": {}})
            entry["variants"][stem]["png"][f"{OG_W}x{OG_H}"] = str(out.relative_to(REPO))
        else:
            # square variant — vector always; raster ladder only for full builds
            v = entry["variants"].setdefault(
                stem,
                {"svg": str(svg_path.relative_to(REPO)), "png": {}},
            )
            # Full builds (default skin) raster the whole ladder. Alternate
            # skins skip it — except aurora marks, whose per-skin recolour is
            # the whole point, so those get a showcase pair on every skin.
            sizes = (SQUARE_PNG_SIZES if full_png
                     else AURORA_SHOWCASE_SIZES if stem.startswith("aurora")
                     else [])
            if sizes:
                master = render_master(svg_text, MASTER_SQUARE, MASTER_SQUARE)
                for s in sizes:
                    p = png_dir / f"{stem}-{s}x{s}.png"
                    downsample(master, s, s).save(p, optimize=True)
                    v["png"][f"{s}x{s}"] = str(p.relative_to(REPO))

    # ---- favicon bundle ----
    # Brand.favicon_variant / Brand.apple_touch_variant override the default.
    # The family default is square-on-dark (orange detail on dark) but
    # glyph-only brands (orangecheck §, vote bars) override to
    # rounded-white-on-orange — at 16×16 the orange tile reads as the family
    # color where a tiny orange glyph on dark backdrop disappears.
    canonical_svg = svg_paths[brand.favicon_variant]
    rounded_svg = svg_paths[brand.apple_touch_variant]

    # favicon.svg (canonical, modern browsers)
    fav_svg = fav_dir / "favicon.svg"
    shutil.copyfile(canonical_svg, fav_svg)
    entry["favicon"]["svg"] = str(fav_svg.relative_to(REPO))

    # PNG favicons in legacy sizes (16, 32, 48)
    fav_master = render_master(canonical_svg.read_text(), MASTER_SQUARE, MASTER_SQUARE)
    for s in (16, 32, 48):
        p = fav_dir / f"favicon-{s}x{s}.png"
        downsample(fav_master, s, s).save(p, optimize=True)
        entry["favicon"][f"png_{s}"] = str(p.relative_to(REPO))

    # favicon.ico — multi-resolution (16, 32, 48)
    ico_path = fav_dir / "favicon.ico"
    ico_imgs = [downsample(fav_master, s, s) for s in (16, 32, 48)]
    ico_imgs[0].save(
        ico_path,
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)],
        append_images=ico_imgs[1:],
    )
    entry["favicon"]["ico"] = str(ico_path.relative_to(REPO))

    # apple-touch-icon — 180×180 (uses rounded variant; iOS rounds it again
    # but a rounded source still looks better in some legacy iOS versions)
    rounded_master = render_master(rounded_svg.read_text(), MASTER_SQUARE, MASTER_SQUARE)
    apple = fav_dir / "apple-touch-icon.png"
    downsample(rounded_master, 180, 180).save(apple, optimize=True)
    entry["favicon"]["apple_touch"] = str(apple.relative_to(REPO))

    # android-chrome — 192 and 512 (PWA / android home-screen)
    for s in (192, 512):
        p = fav_dir / f"android-chrome-{s}x{s}.png"
        downsample(rounded_master, s, s).save(p, optimize=True)
        entry["favicon"][f"android_chrome_{s}"] = str(p.relative_to(REPO))

    # site.webmanifest — 4-space indent matches the family prettier config
    # (consumer site CI runs `prettier --check public/favicons/*`).
    wm = fav_dir / "site.webmanifest"
    wm.write_text(json.dumps({
        "name": brand.label,
        "short_name": brand.label.replace("oc·", "oc-"),
        "icons": [
            {"src": "android-chrome-192x192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "android-chrome-512x512.png", "sizes": "512x512", "type": "image/png"},
        ],
        "theme_color": primary,
        "background_color": DARK,
        "display": "standalone",
    }, indent=4) + "\n")
    entry["favicon"]["webmanifest"] = str(wm.relative_to(REPO))

    return entry


# ---------------------------------------------------------------------------
# Aurora social banners
# ---------------------------------------------------------------------------

BANNER_MODES = ("dark", "light")


def build_banners(brand: Brand) -> dict:
    """Render the aurora social-banner set for one brand: every platform size ×
    every skin × {dark, light}. Banners encode their skin+mode in the filename
    so the whole set lives in one flat dist/<brand>/banners/ dir (no per-skin
    subdir indirection). Returns a manifest section keyed size → skin → mode."""
    bdir = DIST / brand.slug / "banners"
    bdir.mkdir(parents=True, exist_ok=True)
    section: dict[str, dict] = {}

    for size, (w, h) in banner.BANNER_SIZES.items():
        section[size] = {"w": w, "h": h, "skins": {}}
        for skin, accent in SKINS.items():
            section[size]["skins"][skin] = {}
            for mode in BANNER_MODES:
                bg = banner.DARK_BG if mode == "dark" else banner.LIGHT_BG
                # Lockup glyph: accent body, engraving in the backdrop tone —
                # the same treatment the favicon marks use.
                glyph_body = brand.glyph(accent, "none", bg, CANVAS)
                svg_text = banner.banner_svg(
                    w=w, h=h, mode=mode, accent=accent,
                    glyph_body=glyph_body, glyph_px=int(h * 0.42),
                    glyph_native=CANVAS, wordmark=brand.label,
                    tagline=brand.tagline, hostname=brand.hostname,
                    label=f"{brand.label} — {size} banner ({skin}/{mode})",
                )
                stem = f"{size}-{skin}-{mode}"
                svg_path = bdir / f"{stem}.svg"
                svg_path.write_text(svg_text)
                png_path = bdir / f"{stem}.png"
                render_master(svg_text, w, h).save(png_path, optimize=True)
                section[size]["skins"][skin][mode] = {
                    "svg": str(svg_path.relative_to(REPO)),
                    "png": str(png_path.relative_to(REPO)),
                }
    return section


# ---------------------------------------------------------------------------
# YouTube channel kit
# ---------------------------------------------------------------------------

def build_youtube(brand: Brand) -> dict:
    """Render the YouTube channel kit for one brand: channel-art (2048×1152,
    safe-area-aware) + thumbnail (1280×720) + avatar (800×800 circle), each ×
    every skin × {dark, light}. Files encode skin+mode in the name so the whole
    kit lives flat in dist/<brand>/youtube/. Returns a manifest section keyed
    asset → skin → mode."""
    ydir = DIST / brand.slug / "youtube"
    ydir.mkdir(parents=True, exist_ok=True)
    section: dict[str, dict] = {"channel-art": {}, "thumbnail": {}, "avatar": {}}

    for skin, accent in SKINS.items():
        for s in section.values():
            s[skin] = {}
        for mode in BANNER_MODES:
            bg = banner.DARK_BG if mode == "dark" else banner.LIGHT_BG
            # Lockup glyph: accent body, engraving in the backdrop tone — same
            # treatment as the favicon marks and social banners.
            glyph_body = brand.glyph(accent, "none", bg, CANVAS)

            def _emit(asset: str, svg_text: str) -> None:
                stem = f"{asset}-{skin}-{mode}"
                svg_path = ydir / f"{stem}.svg"
                svg_path.write_text(svg_text)
                w, h = (
                    (yt.AVATAR_PX, yt.AVATAR_PX) if asset == "avatar"
                    else yt.YOUTUBE_SIZES[asset]
                )
                png_path = ydir / f"{stem}.png"
                render_master(svg_text, w, h).save(png_path, optimize=True)
                section[asset][skin][mode] = {
                    "svg": str(svg_path.relative_to(REPO)),
                    "png": str(png_path.relative_to(REPO)),
                }

            ca_w, ca_h = yt.YOUTUBE_SIZES["channel-art"]
            _emit("channel-art", yt.landscape_svg(
                w=ca_w, h=ca_h, safe_w=yt.CHANNEL_SAFE_W, safe_h=yt.CHANNEL_SAFE_H,
                fill=0.88, mode=mode, accent=accent, glyph_body=glyph_body,
                glyph_native=CANVAS, wordmark=brand.label, tagline=brand.tagline,
                hostname=brand.hostname,
                label=f"{brand.label} — YouTube channel art ({skin}/{mode})",
            ))
            th_w, th_h = yt.YOUTUBE_SIZES["thumbnail"]
            _emit("thumbnail", yt.landscape_svg(
                w=th_w, h=th_h,
                safe_w=th_w * (1 - 2 * yt.THUMB_INSET),
                safe_h=th_h * (1 - 2 * yt.THUMB_INSET),
                fill=1.0, mode=mode, accent=accent, glyph_body=glyph_body,
                glyph_native=CANVAS, wordmark=brand.label, tagline=brand.tagline,
                hostname=brand.hostname,
                label=f"{brand.label} — YouTube thumbnail ({skin}/{mode})",
            ))
            _emit("avatar", yt.avatar_svg(
                mode=mode, glyph_body=glyph_body, glyph_native=CANVAS,
                label=f"{brand.label} — YouTube avatar ({skin}/{mode})",
            ))
    return section


# ---------------------------------------------------------------------------
# Top-level
# ---------------------------------------------------------------------------

def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    manifest = {
        "$schema": "https://ochk.io/schemas/media-kit-manifest.v1.json",
        "version": "1.5.0",
        "palette": {
            "orange": ORANGE,
            "orange_deep": "#ea580c",
            "dark": DARK,
            "light": LIGHT,
            "muted": "#737373",
        },
        # Skin accents (sRGB of each skin's dark-mode --brand in
        # @orangecheck/design). The default skin renders to dist/<brand>/;
        # every other skin to dist/<brand>/skins/<skin>/.
        "default_skin": DEFAULT_SKIN,
        "skins": SKINS,
        "brands": [],
    }

    for brand in BRANDS:
        print(f"  building {brand.slug:14s} ({brand.hostname}) …")
        entry: dict | None = None
        for skin, primary in SKINS.items():
            # Default skin → dist/<brand>/ (unchanged path consumers cp from).
            # Alternate skins → dist/<brand>/skins/<skin>/.
            is_default = skin == DEFAULT_SKIN
            bdir = DIST / brand.slug if is_default else DIST / brand.slug / "skins" / skin
            skin_entry = build_brand(brand, primary, bdir, full_png=is_default)
            if skin == DEFAULT_SKIN:
                entry = skin_entry
                entry["skins"] = {}
            else:
                # Index the alternate skin's favicon + og + aurora aperture set
                # under the brand entry so consumers / the runtime can resolve
                # per-skin assets. Aurora is indexed per skin because its whole
                # purpose is to recolour across themes (orange/phosphor/
                # lightning/gold).
                assert entry is not None
                entry["skins"][skin] = {
                    "favicon": skin_entry["favicon"],
                    "og": skin_entry["og"],
                    "aurora": {
                        stem: v for stem, v in skin_entry["variants"].items()
                        if stem.startswith("aurora")
                    },
                }
        assert entry is not None
        entry["banners"] = build_banners(brand)
        entry["youtube"] = build_youtube(brand)
        n_svg = sum(1 for v in entry["variants"].values())
        n_png = sum(len(v["png"]) for v in entry["variants"].values())
        n_fav = sum(1 for k in entry["favicon"])
        n_ban = len(banner.BANNER_SIZES) * len(SKINS) * len(BANNER_MODES)
        n_yt = 3 * len(SKINS) * len(BANNER_MODES)
        print(f"    {n_svg:3d} svgs · {n_png:4d} pngs · {n_fav} favicon files "
              f"· {n_ban} banners · {n_yt} youtube · ×{len(SKINS)} skins")
        manifest["brands"].append(entry)

    (REPO / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    total_svg = sum(len(b["variants"]) for b in manifest["brands"])
    total_png = sum(
        sum(len(v["png"]) for v in b["variants"].values())
        for b in manifest["brands"]
    )
    total_banners = sum(
        sum(len(sz["skins"]) * len(BANNER_MODES) for sz in b["banners"].values())
        for b in manifest["brands"]
    )
    total_youtube = sum(
        sum(len(skins) * len(BANNER_MODES) for skins in b["youtube"].values())
        for b in manifest["brands"]
    )
    print(f"\ndone. {len(manifest['brands'])} brands × {len(SKINS)} skins · "
          f"{total_svg} default-skin svgs · {total_png} default-skin pngs "
          f"(+ alternate-skin favicon/og bundles) · {total_banners} aurora banners "
          f"· {total_youtube} youtube assets.")
    print(f"manifest: {REPO / 'manifest.json'}")


if __name__ == "__main__":
    main()
