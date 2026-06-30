# oc-media-kit

The single-source-of-truth media kit for the OrangeCheck family —
every brand mark, every variant, every size, in SVG and PNG.

Fifteen brands. 570 SVGs. 4,890 PNGs. 750 aurora social banners. 450
YouTube channel assets. One machine-readable manifest.
No words inside the marks, ever — icon-only.

```
ochk.io       attest.ochk.io   docs.ochk.io   me.ochk.io
vault.ochk.io fleet.ochk.io    lock.ochk.io   vote.ochk.io
stamp.ochk.io agent.ochk.io    pledge.ochk.io analytics.ochk.io
btc.ochk.io   chat.ochk.io     cosign.ochk.io
```

## How to use

Each consumer site (`oc-*-web`) pulls the favicon bundle straight out of
`dist/<slug>/favicon/` into its own `public/` directory. There is no
build dependency on this repo — files are static and ship as-is.

```bash
# from inside oc-stamp-web:
cp -r ../oc-media-kit/dist/stamp/favicon/* ./public/
```

For programmatic consumers, `manifest.json` at the repo root indexes
every output by `brand → variant → size`.

```jsonc
// manifest.json (truncated)
{
  "palette": { "orange": "#f97316", "dark": "#0a0a0a", ... },
  "brands": [{
    "slug": "stamp",
    "label": "oc·stamp",
    "hostname": "stamp.ochk.io",
    "variants": {
      "square-on-dark": {
        "svg": "dist/stamp/svg/square-on-dark.svg",
        "png": {
          "16x16":  "dist/stamp/png/square-on-dark-16x16.png",
          "32x32":  "dist/stamp/png/square-on-dark-32x32.png",
          ...
        }
      },
      ...
    },
    "favicon": {
      "svg":              "dist/stamp/favicon/favicon.svg",
      "ico":              "dist/stamp/favicon/favicon.ico",
      "apple_touch":      "dist/stamp/favicon/apple-touch-icon.png",
      "android_chrome_192":"dist/stamp/favicon/android-chrome-192x192.png",
      "android_chrome_512":"dist/stamp/favicon/android-chrome-512x512.png",
      "webmanifest":      "dist/stamp/favicon/site.webmanifest"
    }
  }]
}
```

## What's in each brand directory

```
dist/<slug>/
├── svg/             # vector variants (square-on-dark.svg, aurora-on-dark.svg, …)
├── png/             # raster ladder · 16/32/48/64/128/180/192/256/512/1024
├── favicon/         # web-ready bundle (favicon.ico, apple-touch-icon.png, …)
├── og/              # open-graph cards · 1200×630 (flat-color + aurora)
├── banners/         # aurora social banners · <size>-<skin>-<mode>.{svg,png}
├── youtube/         # youtube channel kit · <asset>-<skin>-<mode>.{svg,png}
└── skins/<skin>/    # phosphor / lightning / gold recolours (favicon, og, aurora)
```

## Variants

Every brand ships the same 26-variant set:

| Variant                       | Use                                            |
|-------------------------------|------------------------------------------------|
| `square-on-dark`              | canonical mark · dark surface                  |
| `square-on-light`             | mark on light surface                          |
| `square-white-on-orange`      | white silhouette on orange tile                |
| `square-black-on-orange`      | dark silhouette on orange tile                 |
| `rounded-on-dark`             | iOS home-screen · apple-touch source           |
| `rounded-on-light`            | rounded, light surface                         |
| `rounded-white-on-orange`     | rounded orange tile · canonical favicon for §/vote |
| `rounded-black-on-orange`     | rounded orange tile · dark glyph               |
| `safearea-on-dark`            | OAuth tiles · ext store (28% pad)              |
| `safearea-on-light`           | safe-area, light surface                       |
| `circle-on-dark`              | social avatars (X / GitHub / npm)              |
| `circle-on-light`             | circular, light surface                        |
| `circle-white-on-orange`      | orange avatar tile · white mark                |
| `circle-black-on-orange`      | orange avatar tile · dark mark                 |
| `transparent`                 | natural bicolor on no bg · light surfaces      |
| `transparent-light-ink`       | bicolor with light ink · dark surfaces         |
| `transparent-mono-orange`     | full filled silhouette in orange · masks       |
| `transparent-mono-dark`       | full filled silhouette in dark                 |
| `transparent-mono-light`      | full filled silhouette in light                |
| `transparent-outline-orange`  | outline only · drops the orange chrome         |
| `transparent-outline-dark`    | outline only in dark                           |
| `transparent-outline-light`   | outline only in light                          |
| `og-on-dark`                  | OpenGraph share card · 1200×630                |
| `og-on-light`                 | OG, light backdrop                             |
| `og-white-on-orange`          | OG, orange backdrop · white mark               |
| `og-black-on-orange`          | OG, orange backdrop · dark mark                |

Plus the **aurora aperture** family (12 variants) — see below.

### Aurora aperture marks

The mark *as* the bitcoin-aurora: each glyph's surface is a window into the same
blurred radial-gradient field that powers the live sites' `<OcAurora/>`
(`@orangecheck/design`), with the dark engraving laid back over it. The per-skin
accent leads; success-green and info-blue bleed at the edges — so the whole set
**recolours per theme** (orange / phosphor / lightning / gold) exactly like the
runtime. Showcase/marketing art, not favicons (the field turns to mud at 16px).

| Variant                          | Use                                          |
|----------------------------------|----------------------------------------------|
| `aurora-on-dark`                 | aurora mark · dark surface                   |
| `aurora-on-light`                | aurora mark · light surface                  |
| `aurora-rounded-on-{dark,light}` | rounded tile                                 |
| `aurora-circle-on-{dark,light}`  | circular avatar                              |
| `aurora-safearea-on-{dark,light}`| padded tile (OAuth / store)                  |
| `aurora-transparent`             | aurora-filled mark, no bg · light surfaces   |
| `aurora-transparent-light-ink`   | …light engraving · dark surfaces             |
| `aurora-og-on-{dark,light}`      | OG share card · 1200×630                     |

The default-skin (orange) set ships the full PNG ladder; alternate skins ship
SVG + `256`/`512` PNGs under `dist/<slug>/skins/<skin>/` and are indexed in the
manifest at `brands[].skins.<skin>.aurora`.

### Pick by intent

- **favicon** — the favicon bundle ships ready. Just `cp` `dist/<brand>/favicon/*`.
- **mark for a dark surface** — `transparent-light-ink` (bicolor) or
  `transparent-mono-light` (silhouette).
- **mark for a light surface** — `transparent` (bicolor) or
  `transparent-mono-dark` (silhouette).
- **mark on photo / colored backdrop** — `transparent-outline-{orange|dark|light}`
  (the family chrome drops away; only the distinguishing inner detail remains).
- **social avatar (X, GitHub, npm)** — `circle-on-dark` 512px (most contexts)
  or `circle-white-on-orange` 512px (orange-dominant).
- **OG share card** — `og-on-dark` 1200×630 (most contexts) or
  `og-white-on-orange` for posts where the family color should lead.

## PNG size ladder

`16` `32` `48` `64` `128` `180` `192` `256` `512` `1024`

Each square variant ships every size. OG variants ship `1200×630`.

| Size  | Surface                                       |
|-------|-----------------------------------------------|
| 16    | browser favicon (legacy)                      |
| 32    | browser favicon                               |
| 48    | chrome-extension toolbar · `favicon.ico`      |
| 64    | small icon                                    |
| 128   | chrome-extension main · medium icon           |
| 180   | apple-touch-icon                              |
| 192   | PWA manifest · android-chrome                 |
| 256   | OAuth tile · GitHub avatar (npm)              |
| 512   | PWA splash · app-store · social avatar        |
| 1024  | print · future-proof                          |

## Aurora social banners

Every brand ships a full set of landscape share banners with the family's
**bitcoin-aurora** baked in — the same theme-reactive field as the live sites
(`@orangecheck/design`), statically reconstructed (blurred radial-gradient
clouds in the brand/success/info hue roles + a soft edge-fade). Each banner is a
lockup: glyph + wordmark + tagline + accent hostname. Text is baked to outline
paths, so the assets carry no font dependency.

`dist/<slug>/banners/<size>-<skin>-<mode>.{svg,png}`

| Size       | Dimensions | Surface                          |
|------------|------------|----------------------------------|
| `og`       | 1200×630   | Open Graph / general share card  |
| `x-post`   | 1600×900   | X / Twitter in-feed landscape    |
| `x-header` | 1500×500   | X / Twitter profile header       |
| `linkedin` | 1584×396   | LinkedIn personal / company banner |
| `github`   | 1280×640   | GitHub repo social-preview       |

Each size renders for all **5 skins** (`orangecheck` · `phosphor` · `lightning`
· `gold` · `ember`) × **2 modes** (`dark` · `light`) = 50 per brand, 750 total.
The skin accent recolours the brand/primary aurora clouds exactly like the
runtime; green/blue stay stable. Index under each brand's `banners` key in
`manifest.json` (`size → skins → skin → mode → {svg, png}`).

```
# X header for stamp, dark, default skin:
dist/stamp/banners/x-header-orangecheck-dark.png
```

## YouTube channel kit

The three image surfaces a YouTube channel consumes — which are **not** the same
shapes as the social banners above, so they get their own set. Same baked-aurora
field + outline-path text, recoloured per skin.

`dist/<slug>/youtube/<asset>-<skin>-<mode>.{svg,png}`

| Asset         | Dimensions | Surface                                            |
|---------------|------------|----------------------------------------------------|
| `channel-art` | 2048×1152  | Channel banner. Lockup is **center-anchored inside YouTube's 1546×423 text-&-logo safe area** — the only region visible across every device (incl. TV), where the left-aligned social banners would be cropped off. |
| `thumbnail`   | 1280×720   | Video thumbnail · true 16:9                         |
| `avatar`      | 800×800    | Channel profile picture · circle, accent glyph, no aurora (the icon also renders at 98px, so legibility-first) |

Each renders for all **5 skins** × **2 modes** = 30 per brand, 450 total. Index
under each brand's `youtube` key in `manifest.json`
(`asset → skin → mode → {svg, png}`).

```
# Channel banner for stamp, dark, default skin:
dist/stamp/youtube/channel-art-orangecheck-dark.png
```

## Favicon bundle (per brand)

Every `dist/<slug>/favicon/` carries:

| File                          | Use                                                |
|-------------------------------|----------------------------------------------------|
| `favicon.svg`                 | modern browsers (vector — scales perfectly)        |
| `favicon.ico`                 | legacy Windows / fallback (multi-res 16+32+48)     |
| `favicon-16x16.png`           | favicon at 16×16                                   |
| `favicon-32x32.png`           | favicon at 32×32                                   |
| `favicon-48x48.png`           | chrome-extension toolbar                           |
| `apple-touch-icon.png`        | 180×180 · iOS home-screen                          |
| `android-chrome-192x192.png`  | PWA manifest · android home-screen                 |
| `android-chrome-512x512.png`  | PWA splash · large android home-screen             |
| `site.webmanifest`            | PWA manifest                                       |

### HTML wiring

```html
<!-- modern favicon -->
<link rel="icon" type="image/svg+xml" href="/favicon.svg">

<!-- legacy fallbacks -->
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="shortcut icon" href="/favicon.ico">

<!-- ios -->
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">

<!-- pwa -->
<link rel="manifest" href="/site.webmanifest">

<!-- theme -->
<meta name="theme-color" content="#f97316">

<!-- og -->
<meta property="og:image" content="https://<host>/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
```

## Palette

| Token         | Hex       | Use                            |
|---------------|-----------|--------------------------------|
| `orange`      | `#f97316` | primary brand orange           |
| `orange-deep` | `#ea580c` | hover / accent                 |
| `dark`        | `#0a0a0a` | canonical dark backdrop        |
| `light`       | `#fafafa` | canonical light backdrop       |
| `muted`       | `#737373` | secondary text on either bg    |

`dark` is `#0a0a0a` everywhere. Some legacy per-site favicon SVGs used
`#0b0909`; the kit normalizes to `#0a0a0a` and acts as the new SoT.

## The 13 brand marks

| Slug          | Host                | Mark                                                                |
|---------------|---------------------|---------------------------------------------------------------------|
| `orangecheck` | `ochk.io`           | `§` (section sign) — root umbrella                                  |
| `attest`      | `attest.ochk.io`    | scalloped badge + check (the original OrangeCheck protocol)         |
| `docs`        | `docs.ochk.io`      | page with three text-lines                                          |
| `me`          | `me.ochk.io`        | person silhouette in a stamp frame                                  |
| `vault`       | `vault.ochk.io`     | shackle + safe body + dial                                          |
| `fleet`       | `fleet.ochk.io`     | terminal prompt — chevron + cursor                                  |
| `chat`        | `chat.ochk.io`      | speech bubble + three message dots                                 |
| `lock`        | `lock.ochk.io`      | padlock                                                             |
| `vote`        | `vote.ochk.io`      | three ascending tally bars                                          |
| `stamp`       | `stamp.ochk.io`     | notary stamp + anchor glyph                                         |
| `agent`       | `agent.ochk.io`     | "A" pennant + crossbar                                              |
| `pledge`      | `pledge.ochk.io`    | stylized "P" in an envelope frame                                   |
| `analytics`   | `analytics.ochk.io` | rising line chart                                                   |

No wordmarks. Marks are icon-only.

## Regenerating

```bash
pip install -r build/requirements.txt
python3 build/build.py
```

Edits land in `build/brands.py` (the brand catalog) — adding a new brand
is one `Brand(...)` entry. The pipeline regenerates every variant,
every size, and rewrites `manifest.json`.

## Preview

Open `preview.html` in a browser for a visual contact sheet of every
mark and every variant.

## License

CC-BY-4.0 · attribute to `ochk.io`.

The `archive/` directory preserves the 2026-05 §-mark generation
experiment that seeded this repo.
