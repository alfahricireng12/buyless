# Local comparison input

The optional helper accepts a JSON observation document. It performs no browsing, AI calls, identity resolution, currency conversion, tax lookup, or coupon-code testing. It trusts the supplied facts and never labels the output factually verified.

Run from the skill directory with Python 3.11+:

```sh
python scripts/compare_offers.py examples/offers.synthetic.json --format markdown
python scripts/compare_offers.py examples/offers.synthetic.json --format json
```

## Document

- `schema_version`: `1`.
- `synthetic`: boolean. Use `true` only for fictional examples.
- `location`: object containing a nonempty `label` and optional `radius_km`.
- `checked_at`: ISO 8601 timestamp with timezone. Calculations and coupon validity are evaluated at this observation time, not asserted as current.
- `offers`: up to 200 offer objects. Empty is permitted.

## Offer

Required text: `id`, `product_group`, `title`, `seller`, `currency` (three uppercase letters), `fulfillment` (`delivery` or `pickup`), `condition`, `warranty`, and `url` (HTTP/HTTPS source).

`product_group` means an identity-equivalent model, variant, quantity, and regional specification, assigned by the researching AI. Condition and warranty are also included in the grouping key. The script cannot establish equivalence from names.

Required state: `match` (`confirmed`, `possible`, `rejected`), `eligible` and `available` (each `true`, `false`, or `null`), and `certainty` (`observed`, `estimated`, or `conditional`). A quote is a candidate only when match, availability, and destination/pickup eligibility are confirmed and certainty is not conditional.

Required amounts: `item_price`, `shipping`, `fees`, and `import_charges`. Use nonnegative decimal strings for known amounts and `null` for unknowns except that item price must be known. Amounts are totals for the chosen quantity and must not include the same charge twice. Boolean, negative, infinite, and excessively large amounts are rejected.

Optional fields:

- `travel_cost`: known amount or `null`; relevant to pickup only.
- `distance_km`: known nonnegative distance from the declared reference point. Unknown distance cannot establish compliance with a stated pickup radius.
- `cashback`: deferred benefit, excluded from payable totals.
- `notes`: an array of brief strings.
- `promotions`: up to 10 individual item coupons.

All monetary fields for an offer use that offer's currency. Mixed currencies stay in separate groups. Zero-decimal display currencies supported by the helper are IDR, JPY, and KRW; other currencies use two decimals. This is an explicit helper limitation: currencies requiring a different exponent should be handled separately.

## Promotion

Required fields: `code`, `kind` (`fixed` or `percent`), `value`, `minimum`, `eligibility` (`confirmed`, `unknown`, `ineligible`), and `validity_confirmed` (boolean). Percentage discounts require `cap`; set it explicitly to `null` for a confirmed uncapped offer.

Optional `starts_at` and `expires_at` require timezone-qualified timestamps. Validity is checked at the document's `checked_at`. `source_url` should identify terms. Unknown validity or eligibility is not applied.

The helper selects the largest eligible **single immediate item discount**, applied against the original item subtotal and capped at that subtotal. Stacking, shipping coupons, payment-specific rounding, installments, automatic discounts already included in the input price, and basket-level rules must be handled outside this helper with an explicit trace. Do not add a previously applied coupon again.

## Output

The helper returns grouped offers sorted by cost within comparable contexts, unqualified leads, excluded offers with reasons, calculation traces, unused coupon reasons, and the observation timestamp. Complete observed totals, estimated totals, pickup payments excluding travel, and incomplete quotes remain separate. `lowest_id` is only populated for complete observed or eligible pickup-payment groups; a pickup winner is explicitly payment-only.

The tool's grouping and arithmetic do not validate citations, stock, shipping, authenticity, or user eligibility. Include the narrative evidence and coverage described in [report-format.md](report-format.md).
