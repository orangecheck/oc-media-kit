# Bundled fonts

The banner build (`aurorabanner.py` via `textpath.py`) converts each banner's
wordmark / tagline / hostname into SVG **outline paths** at build time, so the
generated assets carry no runtime font dependency — these TTFs are needed only
to regenerate, never to consume.

| File | Family | Used for |
|------|--------|----------|
| `Inter-SemiBold.ttf` | Inter (`--font-sans-display`) | banner wordmark |
| `Inter-Regular.ttf`  | Inter | banner tagline |
| `JetBrainsMono-Medium.ttf` | JetBrains Mono (`--font-mono-display`) | banner hostname |
| `JetBrainsMono-Regular.ttf` | JetBrains Mono | reserved |

The two Inter statics were instantiated from the upstream variable font at
`opsz=28`, `wght={400,600}`.

## Licensing

Both families are licensed under the **SIL Open Font License 1.1** — see
`Inter-OFL.txt` and `JetBrainsMono-OFL.txt`. The OFL is independent of this
repo's CC-BY-4.0 asset license: the fonts remain under OFL, and the baked
outline paths in the generated banners are permitted derivative use under it.
