# BuyLess website design

## Direction

An exhibition of shopping research, inspired by the graphic composition of Obys Format. The defining devices are a full-width custom geometric BuyLess masthead, a continuous charcoal canvas, isolated monochrome photographic posters, and four geometric chapters. The reference informs scale, negative space, micro captions, and spatial motion; its artwork, logos, and content are not reused.

The BuyLess identity stays visible through the original green icon, green LESS lettering and accents, location-led requests, real-cost comparisons, coupon checks, evidence, and links to the real skill. This is an introduction to an existing AI skill, not a shopping backend. Demo prices are fictional and explicitly labeled.

## Tokens and ownership

`website/dist/styles.css` owns the runtime tokens: ink `#222222`, paper `#f5f5f2`, green `#08b95a`, line `#555553`, and secondary text `#b7b7b0`. The native masthead SVG uses the same paper and green. Header glyphs are a custom vector display treatment; body uses DM Sans, utility captions use IBM Plex Mono, with system fallbacks.

Desktop exterior margins are 16px and chapter gutters 4%. Mobile uses 12px exterior and 20px chapter gutters. Breakpoints: 680px and 1000px. Square controls and fine rules replace pill CTAs. On light panels, focus outlines use ink for contrast; on charcoal, green.

## Chapter grammar

1. Vertical: a narrow request poster, a secondary image strip, and a green location stamp. A product and city start the workflow; country is requested when needed. Budget, condition, and pickup radius remain optional.
2. Horizontal: a wide comparison sheet. Presets update explicitly fictional offers; the walkthrough exposes product match, known shipping, coupons, and evidence.
3. Circle: discovery radiates from the destination. Circle text and the arc rotate with native scroll while essential labels stay upright.
4. Triangle: product, seller, and purchase terms meet in evidence. Native disclosures explain limitations.
5. Grid: the original icon and real host-specific installation commands. Web access remains the host's responsibility.

## Motion and interaction

The home entrance presents the BuyLess wordmark at the center for 1.7 seconds, including a gentle fade, then moves and scales that same lettering to the measured header position over 1.8 seconds. Only after it arrives do the menu, page, poster, and copy fade in; the page reveal takes 1.2 seconds. The landing SVG matches the intro SVG to avoid a visible swap. Scroll, pointer, touch, keyboard input, or resizing skips the entrance immediately. Deep links, browser history returns, and reduced-motion preferences bypass the opening; without JavaScript the content stays visible.

Header glyphs enter in sequence. The poster reveals and responds subtly to a fine-pointer hover. Native scroll drives bounded `--phase` and viewport passage `--view` values, interpolated with time-based damping. Geometry is read in a batch only after scroll or layout changes; animation frames stop when values settle. Layered posters, photo parallax, a rotating circle and arc, subtle perspective, green chapter rules, and a moving light wash form one continuous exhibition. Installation and footer lettering also respond to scroll. Text and annotations reveal once on entry, with focus always revealing interactive content. Prices transition on preset changes. No scroll interception, automatic purchases, fake live research, or invented testimonials.

Annotations remain visible without a Notes toggle. The Triangle annotation sits below the evidence composition and its footer in normal document flow, so it cannot cover the graphic when disclosures expand. Essential claims, location requirements, example disclaimers, and installation requirements are always visible. Chapter links remain available throughout the page.

The device's reduced-motion preference disables decorative motion, exposes all text, and sets geometry to a readable midpoint. The brief ambient entrance pauses offscreen or when the tab is hidden; ongoing geometric motion follows user scrolling. Phone layouts stack the compositions, reduce motion distance and perspective, and avoid pinning. Short landscape viewports also disable pinning to avoid overlapping chapters. Notes and motion toggles remain absent.

## Assets and truthfulness

`assets/buyless-icon.png` is the existing brand asset. `assets/masthead.svg` is original code-native exhibition lettering, not a replacement for the plugin icon. `assets/editorial-headphones.png` is an original generated, unbranded monochrome still-life used decoratively; it is not an actual listing or evidence of a specific product.

All content remains in English for this international introduction. Real shopping reports follow destination language and currency unless explicitly overridden. Keep the lowest comparable cost objective qualified by checked offers, and never guarantee physical authenticity from web pages.
