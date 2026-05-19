# §orangecheck — mark kit

21 mark variants, every common size, pixel-perfect.

## What's in this kit

- **21 SVGs** — one per variant. The § is real SVG path data (not text), so the file renders identically regardless of which fonts are installed on the viewing machine.
- **183 PNGs** — every square-shaped variant at 10 sizes, OG variants at 1200×630.
- **`build_kit.py`** — regenerate everything from a single Python file.
- **`preview.html`** — visual contact sheet of all variants at multiple sizes.
- **`BRAND.md`** — this file.

## How the PNGs were rendered

Every PNG is supersampled. The pipeline:

1. SVG is rendered at a high-resolution master (2048×2048 for squares, 2400×1260 for OG) with cairosvg.
2. PIL downsamples the master to each target size with the LANCZOS filter.

Going from a 2048 master to a 16×16 favicon is 128× supersampling; to 128×128 is 16× supersampling; to 1024×1024 is 2× supersampling. The result is clean anti-aliased edges at every size, no font-hinting fuzz.

## Naming convention

```
<##>-<shape>-<glyph>-on-<background>[-<W>x<H>].<ext>

01-square-orange-on-dark.svg               # vector, scales to anything
01-square-orange-on-dark-16x16.png         # raster, 16×16
01-square-orange-on-dark-128x128.png       # raster, 128×128
05-rounded-orange-on-dark-180x180.png      # apple-touch-icon size
09-safearea-orange-on-dark-128x128.png     # chrome extension main icon
19-og-orange-on-dark-1200x630.png          # og share card
```

SVGs have no size suffix (vector). PNGs always carry `WIDTHxHEIGHT`.

## PNG sizes per variant

Square-shaped variants (01–18): `16, 32, 48, 64, 128, 180, 192, 256, 512, 1024`
OG variants (19–21): `1200x630`

## Color tokens

| Token | Hex |
|---|---|
| orange | `#f97316` |
| orange-deep | `#ea580c` |
| black | `#0a0a0a` |
| white | `#fafafa` |
| muted | `#737373` |

## The 21 variants

| # | Stem | Shape | Color combo |
|---|---|---|---|
| 01 | `01-square-orange-on-dark` | sharp square | orange on black |
| 02 | `02-square-orange-on-light` | sharp square | orange on white |
| 03 | `03-square-white-on-orange` | sharp square | white on orange |
| 04 | `04-square-black-on-orange` | sharp square | black on orange |
| 05 | `05-rounded-orange-on-dark` | rounded square | orange on black |
| 06 | `06-rounded-orange-on-light` | rounded square | orange on white |
| 07 | `07-rounded-white-on-orange` | rounded square | white on orange |
| 08 | `08-rounded-black-on-orange` | rounded square | black on orange |
| 09 | `09-safearea-orange-on-dark` | safe-area (~45% padding) | orange on black |
| 10 | `10-safearea-orange-on-light` | safe-area | orange on white |
| 11 | `11-safearea-white-on-orange` | safe-area | white on orange |
| 12 | `12-safearea-black-on-orange` | safe-area | black on orange |
| 13 | `13-circle-orange-on-dark` | circle | orange on black |
| 14 | `14-circle-white-on-orange` | circle | white on orange |
| 15 | `15-circle-black-on-orange` | circle | black on orange |
| 16 | `16-transparent-orange` | transparent | orange glyph |
| 17 | `17-transparent-black` | transparent | black glyph |
| 18 | `18-transparent-white` | transparent | white glyph |
| 19 | `19-og-orange-on-dark` | og 1200×630 | orange on black |
| 20 | `20-og-white-on-orange` | og 1200×630 | white on orange |
| 21 | `21-og-black-on-orange` | og 1200×630 | black on orange |

## Quick-pick: which file for which surface

| Platform / surface | File |
|---|---|
| Browser favicon, modern | `01-square-orange-on-dark.svg` |
| Browser favicon, fallback 32 | `01-square-orange-on-dark-32x32.png` |
| Browser favicon, fallback 16 | `01-square-orange-on-dark-16x16.png` |
| Apple touch icon | `05-rounded-orange-on-dark-180x180.png` |
| PWA manifest, 192 | `05-rounded-orange-on-dark-192x192.png` |
| PWA manifest, 512 | `05-rounded-orange-on-dark-512x512.png` |
| Google OAuth tile | `09-safearea-orange-on-dark-256x256.png` |
| GitHub OAuth app | `09-safearea-orange-on-dark-256x256.png` |
| Chrome extension, toolbar | `09-safearea-orange-on-dark-48x48.png` |
| Chrome extension, main | `09-safearea-orange-on-dark-128x128.png` |
| Firefox extension, store | `09-safearea-orange-on-dark-512x512.png` |
| X / Twitter avatar | `14-circle-white-on-orange-512x512.png` |
| GitHub avatar | `14-circle-white-on-orange-512x512.png` |
| npm avatar | `14-circle-white-on-orange-256x256.png` |
| OG / Twitter card | `19-og-orange-on-dark-1200x630.png` |
| GitHub repo social | `19-og-orange-on-dark-1200x630.png` |
| README header | `16-transparent-orange.svg` |
| Print, monochrome | `17-transparent-black.svg` |
| Photo / video overlay | `18-transparent-white.svg` |

## HTML wiring

```html
<!-- favicon -->
<link rel="icon" type="image/svg+xml" href="/01-square-orange-on-dark.svg">
<link rel="alternate icon" type="image/png" sizes="32x32"
      href="/01-square-orange-on-dark-32x32.png">
<link rel="alternate icon" type="image/png" sizes="16x16"
      href="/01-square-orange-on-dark-16x16.png">

<!-- apple-touch -->
<link rel="apple-touch-icon" sizes="180x180"
      href="/05-rounded-orange-on-dark-180x180.png">

<!-- theme -->
<meta name="theme-color" content="#f97316">

<!-- og + twitter -->
<meta property="og:image" content="https://ochk.io/19-og-orange-on-dark-1200x630.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://ochk.io/19-og-orange-on-dark-1200x630.png">
```

`manifest.webmanifest`:

```json
{
  "name": "OrangeCheck",
  "short_name": "OC",
  "icons": [
    { "src": "/05-rounded-orange-on-dark-192x192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/05-rounded-orange-on-dark-512x512.png", "sizes": "512x512", "type": "image/png" }
  ],
  "theme_color": "#f97316",
  "background_color": "#0a0a0a"
}
```

## Regenerating

If you change a color, add a size, or want to swap to a different font's § glyph (e.g., SF Mono extracted from a Mac):

```bash
pip install cairosvg Pillow fonttools
python3 build_kit.py
```

Knobs at the top of `build_kit.py`:
- `FONT_PATH` — which TTF to extract the § from
- `SQUARE_PNG_SIZES` — list of square PNG sizes
- `MASTER_SQUARE` / `MASTER_OG` — supersample resolution (higher = sharper, slower)
- color constants `ORANGE`, `BLACK`, `WHITE`

The `VARIANTS` lists at the bottom control which combinations are built.

## License

CC-BY-4.0. Attribute to `ochk.io` if you reuse.
