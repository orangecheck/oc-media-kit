# build/

Regenerator for the OrangeCheck media kit.

```bash
pip install -r build/requirements.txt
python3 build/build.py
```

`brands.py` is the single source of truth for every mark. To add a new
brand, append one `Brand(...)` entry — the build pipeline takes care of
every variant, every size, every favicon flavor, and the manifest entry.

`build.py` writes everything under `dist/<brand>/` and rewrites
`manifest.json` at the repo root.
