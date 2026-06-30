"""YouTube channel kit — the three image surfaces a channel actually consumes,
which are NOT the same shapes as the og/x/linkedin/github banners:

  channel-art  2048×1152, with a CENTER-anchored lockup confined to YouTube's
               1546×423 "text & logo safe area" (the only region visible across
               every device, incl. TV). The og/x banners left-align their
               lockup — that copy is cropped off on phone/tablet/desktop here,
               so YouTube needs its own centered layout.
  thumbnail    1280×720 — true 16:9 video thumbnail (the github banner is
               1280×640, the wrong ratio for a thumbnail).
  avatar       800×800 circle — the channel profile picture at YouTube's
               recommended upload size. Legibility-first (the icon also renders
               at 98px), so a clean accent glyph on a solid circle — no aurora,
               which turns to mud small.

Aurora field + text→path baking are shared with aurorabanner so the field
recolours per skin exactly like the social banners and the live <OcAurora/>.
"""

from __future__ import annotations

from aurorabanner import DARK_BG, INK, LIGHT_BG, _clouds_svg
from textpath import text_to_path, text_width

# Landscape surfaces that carry the full aurora lockup (platform → (w, h)).
YOUTUBE_SIZES: dict[str, tuple[int, int]] = {
    "channel-art": (2048, 1152),
    "thumbnail": (1280, 720),
}

# YouTube's text-&-logo safe area, centered in the 2048×1152 channel banner.
# Everything outside this box is cropped on at least one device class; only the
# TV layout shows the full canvas. Keep the lockup inside it.
CHANNEL_SAFE_W, CHANNEL_SAFE_H = 1546, 423

# Thumbnails aren't cropped, but YouTube overlays the duration pill bottom-right
# and the UI dims the edges — keep the lockup off the rim with a plain inset.
THUMB_INSET = 0.10

AVATAR_PX = 800

# Native lockup metrics (arbitrary units; the whole group is measured then
# uniformly scaled to fit the target safe box, so these only set proportions).
_G = 300.0          # glyph side
_GAP_GT = 78.0      # glyph → text column gap
_WM = 150.0         # wordmark size
_TL = 64.0          # tagline size
_HN = 52.0          # hostname size
_G1 = 46.0          # wordmark → tagline gap
_G2 = 38.0          # tagline → hostname gap


def _field(w: int, h: int, accent: str, mode: str) -> str:
    """The blurred, edge-faded aurora field filling the whole canvas — same
    filter + mask wiring banner_svg uses, so _clouds_svg resolves its refs."""
    blur = h * 0.12
    bg = DARK_BG if mode == "dark" else LIGHT_BG
    return (
        f'  <rect width="{w}" height="{h}" fill="{bg}"/>\n'
        f'  <filter id="aublur" x="-20%" y="-20%" width="140%" height="140%">'
        f'<feGaussianBlur stdDeviation="{blur:.1f}"/></filter>\n'
        f'  <mask id="aumask"><rect width="{w}" height="{h}" fill="url(#aufade)"/></mask>\n'
        f"  {_clouds_svg(w, h, accent, mode)}\n"
    )


def _lockup(*, accent: str, mode: str, glyph_body: str, glyph_native: int,
            wordmark: str, tagline: str, hostname: str) -> tuple[str, float, float]:
    """Build the center lockup at native size in lockup-local coordinates and
    return (inner_svg, native_w, native_h). Caller wraps it in a translate+scale
    group to drop it into a safe box. Horizontal lockup: accent glyph at left,
    a three-line text column (wordmark / tagline / hostname) to its right."""
    ink = INK[mode]

    wm_w = text_width(wordmark, "inter-semibold", _WM)
    tl_w = text_width(tagline, "inter", _TL)
    hn_w = text_width(hostname, "mono-medium", _HN)
    col_w = max(wm_w, tl_w, hn_w)
    text_h = _WM + _G1 + _TL + _G2 + _HN

    lock_w = _G + _GAP_GT + col_w
    lock_h = max(_G, text_h)

    # Vertically center glyph + text block within the lockup band.
    gy = (lock_h - _G) / 2
    ty0 = (lock_h - text_h) / 2
    tx = _G + _GAP_GT

    gs = _G / glyph_native
    wm_y = ty0 + _WM
    wm_d, _ = text_to_path(wordmark, "inter-semibold", _WM, x=tx, y=wm_y)
    tl_y = wm_y + _G1 + _TL
    tl_d, _ = text_to_path(tagline, "inter", _TL, x=tx, y=tl_y)
    hn_y = tl_y + _G2 + _HN
    hn_d, _ = text_to_path(hostname, "mono-medium", _HN, x=tx, y=hn_y)

    inner = (
        f'<g transform="translate(0 {gy:.2f}) scale({gs:.5f})" fill="{ink["fg"]}">{glyph_body}</g>'
        f'<g fill="{ink["fg"]}">{wm_d}</g>'
        f'<g fill="{ink["muted"]}">{tl_d}</g>'
        f'<g fill="{accent}">{hn_d}</g>'
    )
    return inner, lock_w, lock_h


def landscape_svg(*, w: int, h: int, safe_w: float, safe_h: float, fill: float,
                  mode: str, accent: str, glyph_body: str, glyph_native: int,
                  wordmark: str, tagline: str, hostname: str, label: str) -> str:
    """Aurora field + a center lockup fit uniformly into a centered safe box."""
    inner, lock_w, lock_h = _lockup(
        accent=accent, mode=mode, glyph_body=glyph_body,
        glyph_native=glyph_native, wordmark=wordmark, tagline=tagline,
        hostname=hostname,
    )
    scale = min(safe_w / lock_w, safe_h / lock_h) * fill
    ox = (w - lock_w * scale) / 2
    oy = (h - lock_h * scale) / 2
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{label}">\n'
        f"{_field(w, h, accent, mode)}"
        f'  <g transform="translate({ox:.2f} {oy:.2f}) scale({scale:.5f})">{inner}</g>\n'
        f"</svg>\n"
    )


def avatar_svg(*, mode: str, glyph_body: str, glyph_native: int,
               label: str) -> str:
    """800×800 circle profile picture — solid backdrop + accent glyph, no
    aurora (the icon also renders at 98px). bg is the family neutral per mode."""
    bg = DARK_BG if mode == "dark" else LIGHT_BG
    c = AVATAR_PX / 2
    # Glyph inset inside the circle so it doesn't kiss the cropped rim.
    g = int(AVATAR_PX * 0.62)
    gs = g / glyph_native
    off = (AVATAR_PX - g) / 2
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{AVATAR_PX}" '
        f'height="{AVATAR_PX}" viewBox="0 0 {AVATAR_PX} {AVATAR_PX}" '
        f'role="img" aria-label="{label}">\n'
        f'  <circle cx="{c}" cy="{c}" r="{c}" fill="{bg}"/>\n'
        f'  <g transform="translate({off:.1f} {off:.1f}) scale({gs:.5f})" '
        f'fill="{INK[mode]["fg"]}">{glyph_body}</g>\n'
        f"</svg>\n"
    )
