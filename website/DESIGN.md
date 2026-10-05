# BuyLess website design

## Direction

A kinetic editorial introduction: enormous condensed typography, numbered chapters, an oversized green asterisk, and a price receipt that explains the research. The visual reference is the typographic scale, geometric rhythm, and spacious composition of Obys Format; no reference images or page content are reused.

The site introduces an existing AI skill. It does not search shops itself. Every sample price is fictional and explicitly marked. Calls to action lead to the real repository, release, and installation documentation.

## Tokens

- Ink: `#1b211c`; paper: `#eff2e9`; accent: `#b2f675`; brand emerald: `#079c47`.
- Display: Barlow Condensed 600–700; body: DM Sans 400–700; utility: IBM Plex Mono 400–500. System fallbacks preserve readability if Google Fonts is unavailable.
- Desktop margins: 3.3vw; mobile: 20px. Single 680px mobile and 1000px tablet breakpoint.
- Display headings use fluid sizes and short lines. Narrative text stays around 400px wide.
- Rounded controls contrast with sharp editorial sections and the physical receipt layout.

## Motion and interaction

Native scroll, headline entrance, reveal transitions, rotating brand punctuation, moving typographic ribbon, animated search-radius diagram, and an opt-in walkthrough. No scroll interception or hidden navigation.

Reduced-motion preference disables animation and shows all content. A persistent motion control also stops animations. Ambient animations pause offscreen and in hidden tabs. The full story and installation commands remain readable without JavaScript.

Location examples use buttons with `aria-pressed`; the walkthrough has a live status. Evidence disclosures use native `details`. Installation commands can be copied; clipboard refusal selects the text and explains manual copying.

## Content and responsive contract

English introduction for an international project. Explain destination currency and language rather than silently translating the entire marketing site. Keep product claims aligned with the repository: lowest comparable cost among checked offers, visible unknown fees, evidence-based trust, and no physical-authenticity guarantee.

At narrow widths the receipt and research path stack, the radar scales to its column, and secondary nav links disappear while the installation link remains. All primary controls have at least 44px targets. Maintain visible keyboard focus, native reading order, a skip link, and no horizontal document overflow.
