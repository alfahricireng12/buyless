# Comprehensive search with a stopping rule

Use this protocol for every live search. Comprehensive means covering relevant channels and following competitive leads, not claiming access to every store.

## Build a small search plan

Keep the product, destination, condition, currency, delivery/pickup preference, and explicit constraints in working context. When unspecified, assume one new item delivered to the supplied city, with currency and report language based on the destination. Do not infer an exact address or invent shipping charges. Do not make users choose a mode before searching.

Choose search depth internally. Start with a quick pass across relevant source families for ordinary low-risk goods, then expand while plausible cheaper or safer leads remain. Automatically use a deeper pass for expensive goods, electronics, branded or often-counterfeited products, suspiciously low prices, ambiguous variants, or contradictory seller evidence. A quick pass still opens and checks the leading listing, payable costs, coupon conditions, and basic seller protections. A deep pass follows more independent seller and manufacturer evidence and verifies the strongest competing offers. Neither mode promises exhaustive coverage; disclose gaps and stop reasons.

Plan these source families, marking irrelevant families with a specific reason:

| Family | Discovery and follow-up |
|---|---|
| Nearby | Product + district/city + local words for shop, stock, pickup. Find multiple relevant outlets; check their own product pages. |
| Domestic marketplaces | Exact model and meaningful variants across relevant competing marketplaces, including local-language queries. |
| Domestic retailers | Brand storefronts, specialist retailers, independent shops found outside marketplaces. |
| International | Exact model + sellers serving the destination; verify the listing's shipping destination, compatibility, warranty and landed costs. |
| Promotions | Official platform/store campaigns, eligible payment offers, shipping discounts and brand promotions for the leading candidates. |
| Manufacturer | Canonical model specifications, dealer directory, warranty territory and relevant verification guidance. |

Use [store-discovery.md](store-discovery.md) for dynamic location-based discovery. Do not maintain a retailer registry or query irrelevant stores just to inflate numbers. Find sources through current research.

## Search in rounds

1. **Discover:** batch independent queries across applicable families. Search model aliases, manufacturer part numbers, local language, and exact quoted identifiers. Separate interpretations of ambiguous requests. Open promising listings rather than treating snippets as current quotes.
2. **Expand:** follow new sellers and alternate distribution channels. Search exact model + city, exact model + price/promotion terms, and brand + authorized dealer + country. Investigate unusually cheap candidates for accessory prices, deposits, old stock, wrong variants and used condition before discarding them.
3. **Verify:** inspect the best price candidates in each comparable group and any stronger-evidence alternative. Recheck the selected variant, stock, seller identity, destination, payable total and coupon conditions. Apply [authenticity.md](authenticity.md).

Deduplicate by marketplace + seller + listing + variant + condition; mirrors, tracking URLs and syndicated search hits are not independent evidence. A checked store may produce zero matching offers. Record that outcome instead of inventing inventory.

## Efficient expansion and honest stopping

Prioritize new channels and competitive leads. Reuse a manufacturer's specification across identical models, but never reuse one seller's authorization or one listing's stock for another seller. Within a session, reuse already-read pages unless a variant, destination, price or account condition changes. Recheck volatile winner information before the final answer when tools allow it.

Continue while unresolved leads could change the recommendation. After applicable families have been attempted, two successive expansion rounds with no new plausible competitor are a useful saturation signal. It is not proof of the global minimum. If a lower observed item price has unknown shipping, retain it as an unresolved competitor; do not assume it loses.

Stop when the user/host budget is reached, access is exhausted, the user stops the task, or useful expansion saturates. Never bypass access restrictions or start background monitoring. If budget forces a stop, deliver the partial comparison and list the high-impact remaining checks. No need to request a longer prompt.

## Coverage ledger

Record families and source attempts as `checked`, `blocked`, or `lead_only`, with URL, outcome, and time. Mark excluded families `not_applicable` only with a reason, for example "user explicitly requires local pickup". A default international shipping destination is not evidence for the user's destination.

Report source counts as sources checked, not every store in a marketplace. Mention blocked families, unseen prices, unresolved product interpretations, and the stop reason. Optional [audit_research.py](../scripts/audit_research.py) checks a structured [research ledger](research-format.md) for missing coverage and evidence; it performs no browsing.
