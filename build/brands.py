"""
brands.py — the single source of truth for every OrangeCheck-family mark.

Each entry is a Brand: slug + colors + a function that returns the SVG
INNER content (no <svg> wrapper) for a given (fg, bg, ink) palette.

`fg` is the colored mark surface (the "orange square" on most brand
marks, or the glyph itself on transparent variants). `bg` is the
backdrop fill rendered behind the mark. `ink` is the contrasting
detail / cutout color (the dark inner shapes on most brand marks).

The build pipeline (build.py) wires these into the standard variant
matrix (square / rounded / safe-area / circle / transparent / og)
and renders to every required size.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

# --- canonical palette ------------------------------------------------------

ORANGE = "#f97316"   # primary brand orange (tailwind orange-500)
ORANGE_DEEP = "#ea580c"
DARK = "#0a0a0a"     # canonical dark backdrop (matches the family sites)
LIGHT = "#fafafa"
MUTED = "#737373"

# --- skins ------------------------------------------------------------------
#
# A "skin" re-colors the family accent. These hexes are the sRGB renderings of
# each skin's dark-mode `--brand` token in @orangecheck/design
# (oc-packages/design/src/styles/themes/<skin>.css) — the single source of
# truth. The DARK / LIGHT backdrops + ink stay neutral across skins so the mark
# stays recognizable and the *hue* carries the skin signal (matching how the
# sites read: same chrome, different accent).
#
#   orangecheck  oklch(0.72 0.22 55)  → #f97316 (kept exactly == ORANGE so the
#                                        default brand dirs are byte-identical)
#   phosphor     oklch(0.78 0.18 148) → #55d671 (node green)
#   lightning    oklch(0.72 0.20 305) → #c27dff (network violet)
#   gold         oklch(0.80 0.15 90)  → #e3b831 (sound-money gold)
#
# build.py emits the DEFAULT_SKIN to dist/<brand>/ (unchanged) and every other
# skin to dist/<brand>/skins/<skin>/. Runtime favicon/theme-color swapping is
# handled by @orangecheck/design's init script keyed on the oc_skin cookie.
DEFAULT_SKIN = "orangecheck"
SKINS: dict[str, str] = {
    "orangecheck": ORANGE,
    "phosphor": "#55d671",
    "lightning": "#c27dff",
    "gold": "#e3b831",
}

# Some sub-site favicons currently use #0b0909 as the dark backdrop.
# We normalize to #0a0a0a here — the difference is imperceptible and the
# kit acts as the new source of truth.

GlyphFn = Callable[..., str]
# (fg, bg, ink, canvas=1024) -> svg inner content. Glyphs are authored
# against a 24x24 viewBox; the build script scales them into 1024x1024
# canvases by setting a transform on a wrapping <g>. The `bg` and `ink`
# parameters are part of the uniform contract; some glyphs ignore them
# (e.g. orangecheck, vote — single-color shapes).

# ---------------------------------------------------------------------------
# orangecheck (root umbrella, ochk.io)
# ---------------------------------------------------------------------------
# The § (section sign) glyph extracted from DejaVu Sans Mono Bold as raw
# SVG path data — no font dependency at render time. Same path as the
# 2026-05 §-mark experiment under archive/. The path is authored in font
# coordinates; the build pipeline handles centering and scaling.

ORANGECHECK_GLYPH_D = (
    "M518 856Q463 820 438.5 785.5Q414 751 414 711Q414 657 462.5 613.0Q511 569 711 473Q766 509 790.5 543.5Q815 578 815 621Q815 702 550 840"
    "ZM930 1460V1235Q845 1265 779.0 1279.5Q713 1294 659 1294Q583 1294 540.5 1265.0Q498 1236 498 1184Q498 1109 701 1004Q720 994 729 989"
    "Q943 879 1002.0 808.5Q1061 738 1061 637Q1061 548 1013.5 484.0Q966 420 864 373Q934 323 966.5 261.5Q999 200 999 119Q999 -28 894.5 -111.5"
    "Q790 -195 604 -195Q515 -195 429.0 -180.5Q343 -166 258 -137V92Q343 62 424.0 46.5Q505 31 578 31Q655 31 696.0 59.5"
    "Q737 88 737 141Q737 211 523 326L512 332L486 346Q170 516 170 688Q170 782 222.0 851.5Q274 921 371 954Q300 1004 268.0 1064.0"
    "Q236 1124 236 1206Q236 1348 340.0 1434.0Q444 1520 616 1520Q690 1520 768.5 1505.0Q847 1490 930 1460Z"
)
# The DejaVu glyph bounding box: xMin=170 yMin=-195 xMax=1061 yMax=1520
ORANGECHECK_BBOX = (170.0, -195.0, 1061.0, 1520.0)


def orangecheck_glyph_svg(fg: str, bg: str, ink: str, canvas: int = 1024,
                           glyph_frac: float = 0.78) -> str:
    """Render the § glyph centered in a `canvas`-square viewBox.
    fg=glyph color, bg=ignored here (handled by variant wrapper), ink=ignored.
    """
    x_min, y_min, x_max, y_max = ORANGECHECK_BBOX
    gw = x_max - x_min
    gh = y_max - y_min
    scale = (canvas * glyph_frac) / max(gw, gh)
    tx = (canvas - scale * (x_max + x_min)) / 2
    ty = (canvas + scale * (y_max + y_min)) / 2
    return (
        f'<path d="{ORANGECHECK_GLYPH_D}" fill="{fg}" '
        f'transform="translate({tx:.4f} {ty:.4f}) scale({scale:.6f} -{scale:.6f})"/>'
    )


# ---------------------------------------------------------------------------
# btc (bitcoin market desk, btc.ochk.io)
# ---------------------------------------------------------------------------
# The ₿ (BITCOIN SIGN, U+20BF) glyph extracted from Inter-SemiBold as raw SVG
# path data — no font dependency at render time, same approach as the § mark.
# The path is authored in font coordinates (y-up); the render function below
# handles centering + the Y-flip, exactly like orangecheck_glyph_svg. A single
# filled path, so it reads as a glyph-only mark (orange-dominant, white-on-
# orange favicon) and its silhouette doubles as the aurora-aperture clip.

BTC_GLYPH_D = (
    "M373 1414V1676H531V1414ZM670 1414V1676H829V1414ZM373 -186V76H531V-186ZM670 -186V76H829V-186Z"
    "M129 0V1490H705Q863 1490 972.50 1441Q1082 1392 1139 1305.50Q1196 1219 1196 1103Q1196 1016 1164 951"
    "Q1132 886 1074 843Q1016 800 937 779V774Q1024 765 1095.50 721Q1167 677 1210 600.50Q1253 524 1253 416"
    "Q1253 293 1194.50 199Q1136 105 1020 52.50Q904 0 731 0ZM391 217H700Q838 217 910.50 272.50"
    "Q983 328 983 428Q983 497 950 547.50Q917 598 855.50 626Q794 654 707 654H391ZM391 858H688"
    "Q762 858 817 883.50Q872 909 902 956Q932 1003 932 1068Q932 1161 868 1217.50Q804 1274 689 1274H391Z"
)
# Inter-SemiBold U+20BF bounding box: xMin=129 yMin=-186 xMax=1253 yMax=1676
BTC_BBOX = (129.0, -186.0, 1253.0, 1676.0)


def btc_glyph_svg(fg: str, bg: str, ink: str, canvas: int = 1024,
                  glyph_frac: float = 0.72) -> str:
    """Render the ₿ glyph centered in a `canvas`-square viewBox.
    fg=glyph color, bg=ignored (handled by variant wrapper), ink=ignored.
    Same centering/Y-flip contract as orangecheck_glyph_svg."""
    x_min, y_min, x_max, y_max = BTC_BBOX
    gw = x_max - x_min
    gh = y_max - y_min
    scale = (canvas * glyph_frac) / max(gw, gh)
    tx = (canvas - scale * (x_max + x_min)) / 2
    ty = (canvas + scale * (y_max + y_min)) / 2
    return (
        f'<path d="{BTC_GLYPH_D}" fill="{fg}" '
        f'transform="translate({tx:.4f} {ty:.4f}) scale({scale:.6f} -{scale:.6f})"/>'
    )


# ---------------------------------------------------------------------------
# Sub-brand glyphs (24×24 viewBox authored, scaled by wrapper)
#
# Each function returns the inner SVG body. The full mark (the "filled
# orange square" framing common to the family) is included so each glyph
# is a complete brand mark in its own right. The build pipeline composes
# variants (rounded corners, circle, safe-area padding, etc.) by wrapping.
# ---------------------------------------------------------------------------

def attest_glyph(fg: str, bg: str, ink: str, canvas: int = 1024) -> str:  # noqa: ARG001  # noqa: D205
    # attest.ochk.io — BadgeCheck (orange scalloped badge + checkmark).
    # Outline mode (fg="none"): the scalloped badge becomes a stroke
    # outline in `ink`, the check stroke stays. Preserves the scalloped
    # silhouette so the mark stays recognizable.
    """Lifted from lucide-react BadgeCheck. The hexagonal scalloped
    silhouette IS the OrangeCheck-protocol identity (an orange check
    badge)."""
    s = canvas / 24.0
    body_fill = fg if fg != "none" else "none"
    body_stroke = fg if fg != "none" else ink
    return (
        f'<g transform="scale({s:.6f} {s:.6f})">'
        f'<path d="M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76Z" '
        f'fill="{body_fill}" stroke="{body_stroke}" stroke-width="0.5"/>'
        f'<path d="M9 12 l2 2 l4 -4" fill="none" stroke="{ink}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        f'</g>'
    )


def docs_glyph(fg: str, bg: str, ink: str, canvas: int = 1024) -> str:
    """docs.ochk.io — page with three text-lines inside a frame."""
    s = canvas / 24.0
    return (
        f'<g transform="scale({s:.6f} {s:.6f})">'
        f'<rect x="3" y="3" width="18" height="18" fill="{fg}"/>'
        f'<rect x="6" y="6" width="12" height="12" fill="none" stroke="{ink}" stroke-width="1.5"/>'
        f'<rect x="8" y="9" width="8" height="1.25" fill="{ink}"/>'
        f'<rect x="8" y="11.5" width="8" height="1.25" fill="{ink}"/>'
        f'<rect x="8" y="14" width="5" height="1.25" fill="{ink}"/>'
        f'</g>'
    )


def me_glyph(fg: str, bg: str, ink: str, canvas: int = 1024) -> str:
    """me.ochk.io — person silhouette inside a stamp frame."""
    s = canvas / 24.0
    return (
        f'<g transform="scale({s:.6f} {s:.6f})">'
        f'<rect x="3" y="3" width="18" height="18" fill="{fg}"/>'
        f'<rect x="6" y="6" width="12" height="12" fill="none" stroke="{ink}" stroke-width="1.5"/>'
        f'<circle cx="12" cy="11" r="2" fill="{ink}"/>'
        f'<path d="M8 16.5 C 8 14.5, 9.5 13.5, 12 13.5 C 14.5 13.5, 16 14.5, 16 16.5" '
        f'fill="none" stroke="{ink}" stroke-width="1.5" stroke-linecap="square"/>'
        f'</g>'
    )


def vault_glyph(fg: str, bg: str, ink: str, canvas: int = 1024) -> str:  # noqa: ARG001
    """vault.ochk.io — shackle over safe body with dial + feet.

    When `fg="none"` (outline mode), the safe body would otherwise vanish.
    We swap to a stroke-only treatment: shackle and body outlined in `ink`,
    dial + feet rendered as before. Preserves the safe silhouette."""
    s = canvas / 24.0
    body_fill = fg if fg != "none" else "none"
    body_stroke = fg if fg != "none" else ink
    return (
        f'<g transform="scale({s:.6f} {s:.6f})">'
        f'<path d="M8 9 L8 6.5 Q8 3.5 12 3.5 Q16 3.5 16 6.5 L16 9" '
        f'fill="none" stroke="{body_stroke}" stroke-width="2" stroke-linecap="square"/>'
        f'<rect x="4" y="9" width="16" height="12" fill="{body_fill}" stroke="{body_stroke}" stroke-width="0.75"/>'
        f'<circle cx="12" cy="14.5" r="2.75" fill="none" stroke="{ink}" stroke-width="1.5"/>'
        f'<rect x="11.4" y="14.5" width="1.2" height="3.25" fill="{ink}"/>'
        f'<rect x="5.5" y="19" width="2.25" height="1.5" fill="{ink}"/>'
        f'<rect x="16.25" y="19" width="2.25" height="1.5" fill="{ink}"/>'
        f'</g>'
    )


def fleet_glyph(fg: str, bg: str, ink: str, canvas: int = 1024) -> str:
    """fleet.ochk.io — terminal prompt (chevron + cursor line)."""
    s = canvas / 24.0
    return (
        f'<g transform="scale({s:.6f} {s:.6f})">'
        f'<rect x="3" y="3" width="18" height="18" fill="{fg}"/>'
        f'<rect x="6" y="6" width="12" height="12" fill="none" stroke="{ink}" stroke-width="1.5"/>'
        f'<path d="M8.5 9.5 L11 12 L8.5 14.5" fill="none" stroke="{ink}" stroke-width="1.6" '
        f'stroke-linejoin="miter" stroke-linecap="square"/>'
        f'<rect x="12" y="14" width="4" height="1.4" fill="{ink}"/>'
        f'</g>'
    )


def lock_glyph(fg: str, bg: str, ink: str, canvas: int = 1024) -> str:  # noqa: ARG001
    """lock.ochk.io — padlock (shackle + body + keyhole).

    Outline mode (fg="none"): shackle + body become stroke-only in `ink`,
    keyhole rendered as before. The padlock silhouette stays intact."""
    s = canvas / 24.0
    body_fill = fg if fg != "none" else "none"
    body_stroke = fg if fg != "none" else ink
    return (
        f'<g transform="scale({s:.6f} {s:.6f})">'
        f'<path d="M7 11V7.5a5 5 0 0 1 10 0V11" fill="none" stroke="{body_stroke}" stroke-width="2" stroke-linecap="square"/>'
        f'<rect x="4" y="11" width="16" height="10" fill="{body_fill}" stroke="{body_stroke}" stroke-width="0.75"/>'
        f'<rect x="11" y="14" width="2" height="4" fill="{ink}"/>'
        f'<rect x="10.25" y="14" width="3.5" height="1.5" fill="{ink}"/>'
        f'</g>'
    )


def vote_glyph(fg: str, bg: str, ink: str, canvas: int = 1024) -> str:
    """vote.ochk.io — three ascending tally bars. Transparent by design."""
    s = canvas / 24.0
    return (
        f'<g transform="scale({s:.6f} {s:.6f})">'
        f'<rect x="2" y="14" width="4" height="8" fill="{fg}"/>'
        f'<rect x="10" y="8" width="4" height="14" fill="{fg}"/>'
        f'<rect x="18" y="2" width="4" height="20" fill="{fg}"/>'
        f'</g>'
    )


def stamp_glyph(fg: str, bg: str, ink: str, canvas: int = 1024) -> str:
    """stamp.ochk.io — notary-stamp square with anchor glyph."""
    s = canvas / 24.0
    return (
        f'<g transform="scale({s:.6f} {s:.6f})">'
        f'<rect x="3" y="3" width="18" height="18" fill="{fg}"/>'
        f'<rect x="6" y="6" width="12" height="12" fill="none" stroke="{ink}" stroke-width="1.5"/>'
        f'<rect x="11.25" y="8.5" width="1.5" height="7" fill="{ink}"/>'
        f'<rect x="9.5" y="10" width="5" height="1.5" fill="{ink}"/>'
        f'<path d="M9 14.5 L12 15.75 L15 14.5" fill="none" stroke="{ink}" stroke-width="1.5" '
        f'stroke-linejoin="miter" stroke-linecap="square"/>'
        f'</g>'
    )


def agent_glyph(fg: str, bg: str, ink: str, canvas: int = 1024) -> str:  # noqa: ARG001
    """agent.ochk.io — "A" pennant with crossbar + authority seal.

    Outline mode (fg="none"): the "A" body becomes a stroke triangle in
    `ink`, crossbar + dot rendered as before. Keeps the triangle outline
    so the brand still reads."""
    s = canvas / 24.0
    body_fill = fg if fg != "none" else "none"
    body_stroke = fg if fg != "none" else ink
    return (
        f'<g transform="scale({s:.6f} {s:.6f})">'
        f'<path d="M4 20 L12 4 L20 20 Z" fill="{body_fill}" stroke="{body_stroke}" stroke-width="1.5" stroke-linejoin="miter"/>'
        f'<rect x="7.5" y="13.5" width="9" height="2" fill="{ink}"/>'
        f'<rect x="11" y="9" width="2" height="2" fill="{ink}"/>'
        f'</g>'
    )


def pledge_glyph(fg: str, bg: str, ink: str, canvas: int = 1024) -> str:
    """pledge.ochk.io — stylized "P" inside an envelope frame."""
    s = canvas / 24.0
    return (
        f'<g transform="scale({s:.6f} {s:.6f})">'
        f'<rect x="3" y="3" width="18" height="18" fill="{fg}"/>'
        f'<rect x="6" y="6" width="12" height="12" fill="none" stroke="{ink}" stroke-width="1.5"/>'
        f'<rect x="9.25" y="8.5" width="1.75" height="7" fill="{ink}"/>'
        f'<rect x="9.25" y="8.5" width="4.5" height="1.5" fill="{ink}"/>'
        f'<rect x="12.25" y="8.5" width="1.5" height="3.5" fill="{ink}"/>'
        f'<rect x="9.25" y="10.5" width="4.5" height="1.5" fill="{ink}"/>'
        f'</g>'
    )


def analytics_glyph(fg: str, bg: str, ink: str, canvas: int = 1024) -> str:
    """analytics.ochk.io — sharpened line chart climbing into corner."""
    s = canvas / 24.0
    return (
        f'<g transform="scale({s:.6f} {s:.6f})">'
        f'<rect x="3" y="3" width="18" height="18" fill="{fg}"/>'
        f'<path d="M6 17 L10 12 L14 15 L18 8" fill="none" stroke="{ink}" stroke-width="1.8" '
        f'stroke-linecap="square" stroke-linejoin="miter"/>'
        f'<rect x="16.6" y="6.6" width="2.8" height="2.8" fill="{ink}"/>'
        f'</g>'
    )


def chat_glyph(fg: str, bg: str, ink: str, canvas: int = 1024) -> str:  # noqa: ARG001
    """chat.ochk.io — speech bubble (rounded body + tail) with three dots.

    Outline mode (fg="none"): the bubble becomes a stroke-only silhouette
    in `ink`; the three message dots render as before. Mirrors the
    lock/vault silhouette treatment — the mark is a shape, not a filled
    square — so it reads the same way the encryption-family marks do."""
    s = canvas / 24.0
    body_fill = fg if fg != "none" else "none"
    body_stroke = fg if fg != "none" else ink
    return (
        f'<g transform="scale({s:.6f} {s:.6f})">'
        f'<path d="M5 4 H19 A2 2 0 0 1 21 6 V13 A2 2 0 0 1 19 15 H11 L7 19 V15 H5 '
        f'A2 2 0 0 1 3 13 V6 A2 2 0 0 1 5 4 Z" '
        f'fill="{body_fill}" stroke="{body_stroke}" stroke-width="1.6" stroke-linejoin="round"/>'
        f'<circle cx="8" cy="9.5" r="1.15" fill="{ink}"/>'
        f'<circle cx="12" cy="9.5" r="1.15" fill="{ink}"/>'
        f'<circle cx="16" cy="9.5" r="1.15" fill="{ink}"/>'
        f'</g>'
    )


def cosign_glyph(fg: str, bg: str, ink: str, canvas: int = 1024) -> str:  # noqa: ARG001
    """cosign.ochk.io — two people side by side inside the stamp frame: a
    co-founder pair / a builder + a backer getting behind one thing. The
    deliberate two-up of oc·me's single-person mark (one identity → two
    building together)."""
    s = canvas / 24.0
    return (
        f'<g transform="scale({s:.6f} {s:.6f})">'
        f'<rect x="3" y="3" width="18" height="18" fill="{fg}"/>'
        f'<rect x="6" y="6" width="12" height="12" fill="none" stroke="{ink}" stroke-width="1.5"/>'
        f'<circle cx="9.2" cy="10.4" r="1.65" fill="{ink}"/>'
        f'<circle cx="14.8" cy="10.4" r="1.65" fill="{ink}"/>'
        f'<path d="M6.5 16.6 C 6.5 14.9, 7.6 14.1, 9.2 14.1 C 10.8 14.1, 11.9 14.9, 11.9 16.6" '
        f'fill="none" stroke="{ink}" stroke-width="1.5" stroke-linecap="square"/>'
        f'<path d="M12.1 16.6 C 12.1 14.9, 13.2 14.1, 14.8 14.1 C 16.4 14.1, 17.5 14.9, 17.5 16.6" '
        f'fill="none" stroke="{ink}" stroke-width="1.5" stroke-linecap="square"/>'
        f'</g>'
    )


# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Brand:
    slug: str                # 'orangecheck', 'stamp', etc.
    label: str               # short display label
    hostname: str            # bare hostname for OG cards / docs
    tagline: str             # one-line tagline for OG
    glyph: GlyphFn           # (fg, bg, ink, canvas) -> svg inner content
    glyph_frac: float = 0.78
    # If True, the glyph naturally lives "on transparent" (e.g. a § character
    # or three vote bars). The standard sub-brand glyphs ARE the full mark
    # (filled square + frame + detail) and ignore this flag.
    is_glyph_only: bool = False
    # Which variant to use as the canonical favicon source. Defaults to
    # the dark-bg square mark, but brands whose identity is orange-dominant
    # (orangecheck §, vote bars) override to a rounded white-on-orange tile
    # so the family color reads at favicon scale.
    favicon_variant: str = "square-on-dark"
    apple_touch_variant: str = "rounded-on-dark"


BRANDS: list[Brand] = [
    Brand(
        slug="orangecheck",
        label="orangecheck",
        hostname="ochk.io",
        tagline="identity, on bitcoin",
        glyph=lambda fg, bg, ink, canvas=1024: orangecheck_glyph_svg(fg, bg, ink, canvas, 0.78),
        glyph_frac=0.78,
        is_glyph_only=True,
        # The brand IS the orange tile. § rendered in white on an orange
        # rounded square reads at favicon scale and matches the family-
        # wide identity color — same look as the existing attest BadgeCheck
        # but with the canonical § glyph instead of a check.
        favicon_variant="rounded-white-on-orange",
        apple_touch_variant="rounded-white-on-orange",
    ),
    Brand(
        slug="attest",
        label="oc·attest",
        hostname="attest.ochk.io",
        tagline="sybil-resistant attestations, anchored to bitcoin",
        glyph=attest_glyph,
    ),
    Brand(
        slug="docs",
        label="oc·docs",
        hostname="docs.ochk.io",
        tagline="unified reference for the orangecheck family",
        glyph=docs_glyph,
    ),
    Brand(
        slug="me",
        label="oc·me",
        hostname="me.ochk.io",
        tagline="consumer bitcoin-backed identity",
        glyph=me_glyph,
    ),
    Brand(
        slug="vault",
        label="oc·vault",
        hostname="vault.ochk.io",
        tagline="encrypted personal secret storage",
        glyph=vault_glyph,
    ),
    Brand(
        slug="fleet",
        label="oc·fleet",
        hostname="fleet.ochk.io",
        tagline="managed agent + pledge for teams",
        glyph=fleet_glyph,
    ),
    Brand(
        slug="chat",
        label="oc·chat",
        hostname="chat.ochk.io",
        tagline="bitcoin-native end-to-end encrypted messaging",
        glyph=chat_glyph,
    ),
    Brand(
        slug="cosign",
        label="oc·cosign",
        hostname="cosign.ochk.io",
        tagline="get behind builders — join it, or back it",
        glyph=cosign_glyph,
    ),
    Brand(
        slug="lock",
        label="oc·lock",
        hostname="lock.ochk.io",
        tagline="device-anchored end-to-end encryption",
        glyph=lock_glyph,
    ),
    Brand(
        slug="vote",
        label="oc·vote",
        hostname="vote.ochk.io",
        tagline="sat-weighted polls, anchored to bitcoin",
        glyph=vote_glyph,
        is_glyph_only=True,
        # Same reasoning as orangecheck: three bars on a dark backdrop
        # disappear at 16×16. White bars on rounded orange tile pops.
        favicon_variant="rounded-white-on-orange",
        apple_touch_variant="rounded-white-on-orange",
    ),
    Brand(
        slug="stamp",
        label="oc·stamp",
        hostname="stamp.ochk.io",
        tagline="block-anchored declarations over any hash",
        glyph=stamp_glyph,
    ),
    Brand(
        slug="agent",
        label="oc·agent",
        hostname="agent.ochk.io",
        tagline="scoped, signed authority for autonomous agents",
        glyph=agent_glyph,
    ),
    Brand(
        slug="pledge",
        label="oc·pledge",
        hostname="pledge.ochk.io",
        tagline="bonded commitments with provable consequences",
        glyph=pledge_glyph,
    ),
    Brand(
        slug="analytics",
        label="oc·analytics",
        hostname="analytics.ochk.io",
        tagline="owner cockpit for the orangecheck family",
        glyph=analytics_glyph,
    ),
    Brand(
        slug="btc",
        label="oc·btc",
        hostname="btc.ochk.io",
        tagline="read the bitcoin market",
        glyph=lambda fg, bg, ink, canvas=1024: btc_glyph_svg(fg, bg, ink, canvas, 0.72),
        glyph_frac=0.72,
        is_glyph_only=True,
        # The mark IS the orange tile: ₿ rendered white on a rounded orange
        # square reads at favicon scale and leads with the family color, same
        # treatment as the orangecheck § and vote bars (a glyph-only mark on a
        # dark backdrop disappears at 16×16).
        favicon_variant="rounded-white-on-orange",
        apple_touch_variant="rounded-white-on-orange",
    ),
]


# ---------------------------------------------------------------------------
# Variant matrix — applied uniformly across every brand.
#
#   stem               shape       fg-on-bg combo            radius     pad
#   --------------------------------------------------------------------------
#   square-on-dark     sharp       orange-square / dark-bg   0          0
#   square-on-light    sharp       orange-square / light-bg  0          0
#   rounded-on-dark    rounded     orange-square / dark-bg   22%        0
#   rounded-on-light   rounded     orange-square / light-bg  22%        0
#   safearea-on-dark   sharp+pad   orange-square / dark-bg   0          ~28%
#   safearea-on-light  sharp+pad   orange-square / light-bg  0          ~28%
#   circle-on-dark     circle      orange-square / dark-bg   50%        0
#   circle-on-light    circle      orange-square / light-bg  50%        0
#   transparent        none        mark / none               -          0
#   og-on-dark         og card     dark-bg, big mark         -          -
#   og-on-orange       og card     orange-bg, white mark     -          -
#
# For `is_glyph_only` brands (orangecheck §, vote bars), additional
# inverted variants (white-on-orange, black-on-orange) are emitted too —
# those make sense for a single-color glyph. For full-stack glyphs that
# already include the orange square (stamp/lock/etc.), inverted
# "white-on-orange" variants would just be the mark with orange/orange
# bleed and don't read; we skip them.
# ---------------------------------------------------------------------------

# Square PNG ladder — covers every common surface:
#   16/32        — favicon
#   48           — chrome extension toolbar
#   64           — small icon
#   128          — chrome extension main
#   180          — apple-touch-icon
#   192          — pwa / android-chrome
#   256          — oauth tile
#   512          — pwa / app-store / npm-avatar / store header
#   1024         — print / future-proof
SQUARE_PNG_SIZES = [16, 32, 48, 64, 128, 180, 192, 256, 512, 1024]

# OG share card
OG_W, OG_H = 1200, 630

# Supersample masters — render once, downsample to all targets.
MASTER_SQUARE = 2048
MASTER_OG = (2400, 1260)

# Native SVG canvas size — what every variant SVG's viewBox uses.
CANVAS = 1024
