# BuyLess introduction website

A dependency-free static website with an animated editorial layout, accessible motion control, fictional research walkthrough, evidence disclosures, and real installation commands.

Public URL: <https://alfahricireng12.github.io/buyless/>. The `Deploy BuyLess website` workflow publishes `website/dist` when those files change on `main`, or when manually dispatched. GitHub Pages must use GitHub Actions as its source.

From the repository root, preview with Python 3:

```sh
python -m http.server 4173 --bind 127.0.0.1 --directory website/dist
```

Open `http://127.0.0.1:4173`. Any static host can serve `website/dist` directly; there is no build step or backend. Font loading uses Google Fonts and falls back to system fonts. All essential content is available without JavaScript.

The demonstration uses fictional offers. It does not perform live shopping research or send visitor requests to an AI service. Actual BuyLess use requires installation in an AI host with web tools.
