# OrangeCheck brand guidelines

## Voice

- `orangecheck` lowercase in prose — the root umbrella.
- `OC <Verb>` capitalised in prose (e.g. `OC Stamp`); `oc·<verb>` in
  headings, nav, and the wordmark (e.g. `oc·stamp`).
- The middle-dot (`·`, U+00B7) — not a hyphen — between `oc` and verb.
- Rule-of-three taglines.
- Name trust anchors plainly. ("Bitcoin", not "the chain.")

## Marks

Icon-only. No wordmarks baked into the SVG itself — the wordmark is
always a separate text element next to the mark in headers (see
`@orangecheck/ui`'s `<OcLogoDropdown>`).

The 12 marks are siblings in one family, drawn in a shared sharp,
boxy cypherpunk language. Most sub-brand marks share a common chrome
— a filled orange square with an outlined inner frame — and vary by
the inner glyph (anchor / padlock / "P" / chevron / person / etc.).
Two glyphs break the chrome on purpose: `orangecheck` is the §
section sign on a backdrop, and `vote` is three ascending bars on
transparency.

### When to use which variant

- **favicon** → `square-on-dark` (or `favicon.svg` from the bundle).
- **iOS / Android home-screen** → `rounded-on-dark` (apple-touch-icon
  bundled, 180×180).
- **OAuth provider tiles, Chrome / Firefox extension store** →
  `safearea-on-dark` at 256 or 512 (the 28% padding satisfies the
  store-side cropping rules).
- **Social avatar** (X / GitHub / npm) → `circle-on-dark` at 512.
- **README header / docs hero / photo overlay** → `transparent`.
- **OpenGraph / Twitter card** → `og-on-dark` 1200×630.
- **Print, monochrome contexts** → `transparent-dark` (glyph-only
  brands only).

### Colors

Always one of:

- orange `#f97316` on dark `#0a0a0a` (canonical)
- orange `#f97316` on light `#fafafa`
- white `#fafafa` on orange `#f97316` (only for glyph-only brands)
- dark `#0a0a0a` on orange `#f97316` (only for glyph-only brands)

Do not recolor. Do not gradient. Do not drop-shadow.

### Clear space

Reserve at minimum `1/8` of the mark's longest edge as clear space on
every side. The `safearea-*` variants pre-bake this padding and
should be used wherever an external surface (an OAuth tile, an
extension-store thumbnail) will crop the mark from the edges in.

### Don'ts

- Don't add a wordmark inside the SVG itself.
- Don't rotate, skew, or recolor.
- Don't put the mark on a colored background that isn't `dark`,
  `light`, or `orange`.
- Don't crop into the mark (the safe-area variants give you the
  cropping budget you need).
- Don't substitute a different check / lock / stamp icon for the
  canonical marks here.

## Trademark

`OrangeCheck` and the family marks are trademarks of OrangeCheck.
Use is permitted under CC-BY-4.0 with attribution to `ochk.io`.

See the family `TRADEMARK.md` in `oc-packages` for the legal
trademark notice that ships with every package.
