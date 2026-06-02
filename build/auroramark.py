"""auroramark — the "aurora aperture" logo treatment.

The mark becomes a window into the bitcoin-aurora: the brand glyph's surface
silhouette is used as a mask, and the same blurred radial-gradient cloud field
that powers @orangecheck/design's <OcAurora/> (and the static banners in
aurorabanner.py) is painted *inside* the glyph. The engraving (inner frame /
detail) is then laid back over the field in dark ink so the mark stays legible.

Design constraints (locked with the owner, 2026-06-02):
  - Treatment A "aperture": the glyph IS the aurora, not a backdrop behind it.
  - Accent-dominant, subtle bleed: the per-skin accent clearly leads; green and
    blue read as restrained wisps so each brand colour is instantly recognisable.

Hue roles mirror the runtime exactly — the per-skin accent drives the warm
clouds; success-green (#34c98a) and info-blue (#3f9fd1) stay stable so the field
keeps its family flavour while recolouring across skins (orange / phosphor /
lightning / gold) and modes (dark / light).

Everything here is plain SVG (radial gradients + feGaussianBlur + a luminance
mask) so cairosvg renders it to the full PNG ladder with no JS/runtime.
"""
from __future__ import annotations

# Stable aurora hues (sRGB of --success / --info dark-mode tokens). The accent
# clouds recolour per skin; these two stay put — same contract as the banners.
AURORA_GREEN = "#34c98a"   # --success  oklch(0.72 0.16 150)
AURORA_BLUE = "#3f9fd1"    # --info     oklch(0.66 0.10 235)

# Aperture base tint sitting under the clouds, so the glyph keeps its shape even
# where the field is sparse (a faint lift off the backdrop, never a hard fill).
BASE = {"dark": "#141414", "light": "#ffffff"}

# Cloud layout as fractions of the (square) canvas: (cx, cy, r, role, strength).
# role: "a" = accent (per-skin), "g" = green, "b" = blue.
# strength scales the cloud's inner alpha — accent clouds lead; green/blue bleed.
# Positions echo aurora.css: warm core through the centre, cool wisps to the
# top-right / bottom-right corners.
_CLOUDS = [
    (0.20, 0.16, 0.66, "a", 1.00),   # accent — top-left, broad
    (0.52, 0.55, 0.58, "a", 1.00),   # accent — warm centre core
    (0.18, 0.88, 0.56, "a", 0.85),   # accent — bottom-left
    (0.86, 0.15, 0.50, "g", 0.62),   # green  — top-right wisp
    (0.88, 0.84, 0.52, "b", 0.62),   # blue   — bottom-right wisp
]


def _field(accent: str, uid: str, canvas: int) -> tuple[str, str]:
    """Return (defs, blobs) for the cloud field on a `canvas`-square viewBox."""
    role = {"a": accent, "g": AURORA_GREEN, "b": AURORA_BLUE}
    defs, blobs = [], []
    for i, (fx, fy, fr, r, strength) in enumerate(_CLOUDS):
        hue = role[r]
        gid = f"{uid}f{i}"
        cx, cy, rr = fx * canvas, fy * canvas, fr * canvas
        inner = 0.96 * strength
        mid = 0.30 * strength
        defs.append(
            f'<radialGradient id="{gid}" cx="50%" cy="50%" r="50%">'
            f'<stop offset="0%" stop-color="{hue}" stop-opacity="{inner:.2f}"/>'
            f'<stop offset="52%" stop-color="{hue}" stop-opacity="{mid:.2f}"/>'
            f'<stop offset="100%" stop-color="{hue}" stop-opacity="0"/>'
            f"</radialGradient>"
        )
        blobs.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rr:.1f}" fill="url(#{gid})"/>'
        )
    return "".join(defs), "".join(blobs)


def aurora_glyph(brand, accent: str, ink: str, mode: str, canvas: int,
                 uid: str) -> str:
    """Inner SVG body: the brand glyph filled with the aurora field + engraving.

    Composes against a `canvas`-square coordinate space with NO backdrop — the
    caller (build.py variant wrapper) supplies the square / rounded / circle /
    transparent backdrop, exactly like the standard variants.

    Uniform across all 12 brands via two glyph calls:
      - glyph(fg="#fff", ink="#fff") → solid surface silhouette → the clip path
      - glyph(fg="none", ink=<ink>)  → engraving only (+ outline) → laid on top

    Clipping (not masking): cairosvg silently ignores <mask>, but honours
    <clipPath> — including a glyph body wrapped in a transformed <g> — so the
    field is hard-clipped to the glyph and the mark keeps crisp edges.
    """
    clip_body = brand.glyph("#ffffff", "none", "#ffffff", canvas)
    ink_body = brand.glyph("none", "none", ink, canvas)
    defs, blobs = _field(accent, uid, canvas)
    base = BASE[mode]
    blur = canvas * 0.085
    # Dark rides a touch brighter; light composites quieter.
    field_op = 1.0 if mode == "dark" else 0.95

    return (
        f"<defs>{defs}"
        f'<filter id="{uid}b" x="-30%" y="-30%" width="160%" height="160%">'
        f'<feGaussianBlur stdDeviation="{blur:.1f}"/></filter>'
        f'<clipPath id="{uid}c">{clip_body}</clipPath>'
        f"</defs>"
        f'<g clip-path="url(#{uid}c)">'
        f'<rect width="{canvas}" height="{canvas}" fill="{base}"/>'
        f'<g opacity="{field_op}" filter="url(#{uid}b)">{blobs}</g>'
        f"</g>"
        f"{ink_body}"
    )
