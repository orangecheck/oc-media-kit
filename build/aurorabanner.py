"""Aurora social banners — the ambient bitcoin-aurora baked into static
landscape share art (og / x / linkedin / github), composed with the brand
glyph + wordmark + tagline + hostname.

The live aurora (oc-packages/design/src/styles/aurora.css) is animated CSS using
oklch + mix-blend-mode:screen + a radial mask. cairosvg renders none of those,
so this is a faithful *static* reconstruction: blurred radial-gradient clouds in
the same hue roles (brand / success / info / primary) over the family backdrop,
with a soft edge-fade mask. Hues recolour per skin exactly like the runtime —
the skin accent drives the brand/primary clouds; success/info stay stable.
"""

from __future__ import annotations

from textpath import text_to_path, text_width

# Stable aurora hues (sRGB of --success / --info dark-mode tokens). The brand /
# primary clouds use the per-skin accent passed in, so the field recolours.
AURORA_GREEN = "#34c98a"   # --success  oklch(0.72 0.16 150)
AURORA_BLUE = "#3f9fd1"    # --info     oklch(0.66 0.10 235)

DARK_BG = "#0a0a0a"
LIGHT_BG = "#fafafa"

# Foreground / muted text per mode.
INK = {
    "dark": {"fg": "#fafafa", "muted": "#a3a3a3"},
    "light": {"fg": "#0a0a0a", "muted": "#525252"},
}

# Banner sizes (platform → (w, h)).
BANNER_SIZES: dict[str, tuple[int, int]] = {
    "og": (1200, 630),
    "x-post": (1600, 900),  # 16:9 in-feed photo — X shows landscape uncropped here
    "x-header": (1500, 500),
    "linkedin": (1584, 396),
    "github": (1280, 640),
}

# Cloud layout as fractions of the canvas: (cx, cy, rx, ry, hue-role).
# Roles: a=accent(brand), g=green, b=blue, p=accent(primary≈brand). Positions
# echo aurora.css (clouds spread across the field, drifting off the edges).
_CLOUDS = [
    (-0.05, -0.10, 0.46, 0.95, "a"),
    (0.34, -0.05, 0.42, 0.90, "g"),
    (0.98, -0.08, 0.46, 0.95, "b"),
    (0.62, 0.95, 0.40, 0.85, "p"),
    (0.12, 1.02, 0.42, 0.85, "a"),
]


def _clouds_svg(w: int, h: int, accent: str, mode: str) -> str:
    role_hue = {"a": accent, "g": AURORA_GREEN, "b": AURORA_BLUE, "p": accent}
    # Dark rides brighter (screen-ish luminosity faked via higher alpha);
    # light rides quieter and composites normally.
    cloud_op = 0.62 if mode == "dark" else 0.40
    defs: list[str] = []
    blobs: list[str] = []
    for i, (fx, fy, frx, fry, role) in enumerate(_CLOUDS):
        hue = role_hue[role]
        cx, cy, rx, ry = fx * w, fy * h, frx * w, fry * h
        defs.append(
            f'<radialGradient id="au{i}" cx="50%" cy="50%" r="50%">'
            f'<stop offset="0%" stop-color="{hue}" stop-opacity="0.95"/>'
            f'<stop offset="62%" stop-color="{hue}" stop-opacity="0.18"/>'
            f'<stop offset="100%" stop-color="{hue}" stop-opacity="0"/>'
            f"</radialGradient>"
        )
        blobs.append(
            f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="url(#au{i})"/>'
        )
    # Soft edge-fade mask (the radial mask-image in aurora.css).
    defs.append(
        f'<radialGradient id="aufade" cx="50%" cy="38%" r="78%">'
        f'<stop offset="55%" stop-color="#fff" stop-opacity="1"/>'
        f'<stop offset="100%" stop-color="#fff" stop-opacity="0"/>'
        f"</radialGradient>"
    )
    return (
        f"<defs>{''.join(defs)}</defs>"
        f'<g opacity="{cloud_op}" filter="url(#aublur)" mask="url(#aumask)">'
        f"{''.join(blobs)}</g>"
    )


def banner_svg(
    *,
    w: int,
    h: int,
    mode: str,
    accent: str,
    glyph_body: str,
    glyph_px: int,
    glyph_native: int,
    wordmark: str,
    tagline: str,
    hostname: str,
    label: str,
) -> str:
    """Compose one aurora banner. `glyph_body` is brand.glyph(fg,bg,ink,native)
    inner SVG sized to a `glyph_native`-px canvas; we scale it to `glyph_px`."""
    bg = DARK_BG if mode == "dark" else LIGHT_BG
    ink = INK[mode]
    blur = h * 0.12

    # ---- left-aligned content block, vertically centred ----
    pad = w * 0.06
    g = glyph_px
    gscale = g / glyph_native
    gx = pad
    gy = (h - g) / 2

    # Text column to the right of the glyph. Cap each line's size so it can't
    # overrun the canvas edge — long taglines (e.g. oc·attest) would otherwise
    # bleed off the right, clipped on any platform.
    tx = gx + g + w * 0.035
    avail = w - tx - pad  # mirror the left pad on the right

    def _fit(text: str, font: str, size: float) -> float:
        wpx = text_width(text, font, size)
        return size * avail / wpx if wpx > avail else size

    wm_size = _fit(wordmark, "inter-semibold", h * 0.150)
    tl_size = _fit(tagline, "inter", h * 0.066)
    hn_size = _fit(hostname, "mono-medium", h * 0.054)
    gap1 = h * 0.052
    gap2 = h * 0.044
    block_h = wm_size + gap1 + tl_size + gap2 + hn_size
    top = (h - block_h) / 2

    wm_y = top + wm_size
    wm_d, _ = text_to_path(wordmark, "inter-semibold", wm_size, x=tx, y=wm_y)
    tl_y = wm_y + gap1 + tl_size
    tl_d, _ = text_to_path(tagline, "inter", tl_size, x=tx, y=tl_y)
    hn_y = tl_y + gap2 + hn_size
    hn_d, _ = text_to_path(hostname, "mono-medium", hn_size, x=tx, y=hn_y)

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{label}">\n'
        f'  <rect width="{w}" height="{h}" fill="{bg}"/>\n'
        f'  <filter id="aublur" x="-20%" y="-20%" width="140%" height="140%">'
        f'<feGaussianBlur stdDeviation="{blur:.1f}"/></filter>\n'
        f'  <mask id="aumask"><rect width="{w}" height="{h}" fill="url(#aufade)"/></mask>\n'
        f"  {_clouds_svg(w, h, accent, mode)}\n"
        f'  <g transform="translate({gx:.1f} {gy:.1f}) scale({gscale:.4f})" '
        f'fill="{ink["fg"]}">{glyph_body}</g>\n'
        f'  <g fill="{ink["fg"]}">{wm_d}</g>\n'
        f'  <g fill="{ink["muted"]}">{tl_d}</g>\n'
        f'  <g fill="{accent}">{hn_d}</g>\n'
        f"</svg>\n"
    )
