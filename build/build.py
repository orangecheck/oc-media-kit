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
    LIGHT,
    MASTER_OG,
    MASTER_SQUARE,
    OG_H,
    OG_W,
    ORANGE,
    SQUARE_PNG_SIZES,
)

REPO = Path(__file__).resolve().parent.parent
DIST = REPO / "dist"


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
# Per-brand variant manifest
# ---------------------------------------------------------------------------

def variants_for(brand: Brand) -> list[tuple[str, str, tuple[int, int]]]:
    """Return [(stem, svg_text, (w, h))]. Square variants render to
    1024x1024; OG variants render to 1200x630."""
    out: list[tuple[str, str, tuple[int, int]]] = []
    label = f"{brand.label} mark"

    # ---- standard variants present on every brand ----
    out.append((
        "square-on-dark",
        variant_square(brand, ORANGE, DARK, DARK, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "square-on-light",
        variant_square(brand, ORANGE, LIGHT, DARK, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "rounded-on-dark",
        variant_rounded(brand, ORANGE, DARK, DARK, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "rounded-on-light",
        variant_rounded(brand, ORANGE, LIGHT, DARK, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "safearea-on-dark",
        variant_safearea(brand, ORANGE, DARK, DARK, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "safearea-on-light",
        variant_safearea(brand, ORANGE, LIGHT, DARK, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "circle-on-dark",
        variant_circle(brand, ORANGE, DARK, DARK, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "circle-on-light",
        variant_circle(brand, ORANGE, LIGHT, DARK, label),
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
        variant_square(brand, LIGHT, ORANGE, LIGHT, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "square-black-on-orange",
        variant_square(brand, DARK, ORANGE, DARK, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "rounded-white-on-orange",
        variant_rounded(brand, LIGHT, ORANGE, LIGHT, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "rounded-black-on-orange",
        variant_rounded(brand, DARK, ORANGE, DARK, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "circle-white-on-orange",
        variant_circle(brand, LIGHT, ORANGE, LIGHT, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "circle-black-on-orange",
        variant_circle(brand, DARK, ORANGE, DARK, label),
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
        variant_transparent(brand, ORANGE, DARK, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "transparent-light-ink",
        variant_transparent(brand, ORANGE, LIGHT, label),
        (CANVAS, CANVAS),
    ))
    out.append((
        "transparent-mono-orange",
        variant_transparent(brand, ORANGE, ORANGE, label),
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
    outline_fg_orange = ORANGE if brand.is_glyph_only else "none"
    outline_fg_dark = DARK if brand.is_glyph_only else "none"
    outline_fg_light = LIGHT if brand.is_glyph_only else "none"
    out.append((
        "transparent-outline-orange",
        variant_transparent(brand, outline_fg_orange, ORANGE, label),
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
        variant_og(brand, ORANGE, DARK, DARK, label),
        (OG_W, OG_H),
    ))
    out.append((
        "og-on-light",
        variant_og(brand, ORANGE, LIGHT, DARK, label),
        (OG_W, OG_H),
    ))
    out.append((
        "og-white-on-orange",
        variant_og(brand, LIGHT, ORANGE, LIGHT, label),
        (OG_W, OG_H),
    ))
    out.append((
        "og-black-on-orange",
        variant_og(brand, DARK, ORANGE, DARK, label),
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

def build_brand(brand: Brand) -> dict:
    """Build every variant for one brand. Returns a manifest entry."""
    bdir = DIST / brand.slug
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

    for stem, svg_text, (w, h) in variants_for(brand):
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
            # square variant — ladder of sizes
            master = render_master(svg_text, MASTER_SQUARE, MASTER_SQUARE)
            v = entry["variants"].setdefault(
                stem,
                {"svg": str(svg_path.relative_to(REPO)), "png": {}},
            )
            for s in SQUARE_PNG_SIZES:
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

    # site.webmanifest
    wm = fav_dir / "site.webmanifest"
    wm.write_text(json.dumps({
        "name": brand.label,
        "short_name": brand.label.replace("oc·", "oc-"),
        "icons": [
            {"src": "android-chrome-192x192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "android-chrome-512x512.png", "sizes": "512x512", "type": "image/png"},
        ],
        "theme_color": ORANGE,
        "background_color": DARK,
        "display": "standalone",
    }, indent=2) + "\n")
    entry["favicon"]["webmanifest"] = str(wm.relative_to(REPO))

    return entry


# ---------------------------------------------------------------------------
# Top-level
# ---------------------------------------------------------------------------

def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    manifest = {
        "$schema": "https://ochk.io/schemas/media-kit-manifest.v1.json",
        "version": "1.0.0",
        "palette": {
            "orange": ORANGE,
            "orange_deep": "#ea580c",
            "dark": DARK,
            "light": LIGHT,
            "muted": "#737373",
        },
        "brands": [],
    }

    for brand in BRANDS:
        print(f"  building {brand.slug:14s} ({brand.hostname}) …")
        entry = build_brand(brand)
        n_svg = sum(1 for v in entry["variants"].values())
        n_png = sum(len(v["png"]) for v in entry["variants"].values())
        n_fav = sum(1 for k in entry["favicon"])
        print(f"    {n_svg:3d} svgs · {n_png:4d} pngs · {n_fav} favicon files")
        manifest["brands"].append(entry)

    (REPO / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    total_svg = sum(len(b["variants"]) for b in manifest["brands"])
    total_png = sum(
        sum(len(v["png"]) for v in b["variants"].values())
        for b in manifest["brands"]
    )
    print(f"\ndone. {len(manifest['brands'])} brands · "
          f"{total_svg} svgs · {total_png} pngs.")
    print(f"manifest: {REPO / 'manifest.json'}")


if __name__ == "__main__":
    main()
