# Research ledger v1

Optional machine-readable working notes for `python scripts/audit_research.py research.json`. No packages, API keys or network are used. The host can apply the same checks manually. See the [synthetic ledger](../examples/research.synthetic.json).

Top-level fields:

| Field | Meaning |
|---|---|
| `schema_version` | Integer `1` |
| `synthetic` | Boolean; fictional demonstrations must use `true` |
| `product`, `location` | Nonempty requested product and destination labels |
| `checked_at` | Report timestamp in timezone-aware ISO 8601 |
| `stop_reason` | `saturation`, `budget`, `access_exhausted`, or `user_stopped` |
| `families` | All six keys: `nearby`, `domestic_marketplaces`, `domestic_retailers`, `international`, `promotions`, `manufacturer` |
| `attempts` | Up to 500 consolidated source observations |
| `candidates` | Up to 200 candidates with evidence |

Each family contains `scope`: `applicable` or `not_applicable`; exclusions require a nonempty `reason`. An exclusion is the host's judgment, not a finding the audit independently verifies.

Each attempt contains `family`, stable `source_key`, HTTP(S) `url`, `checked_at`, `status` (`checked`, `blocked`, `lead_only`), and nonempty `outcome`. Consolidate repeated visits to a source in one family into one record. A source key identifies the actual store/platform source, not a tracking URL. One checked source does not establish exhaustive coverage. The audit reports any applicable family without a directly checked source.

Each candidate contains `id`, `product_key`, `seller_key`, and `evidence`. Use the same candidate id in the separate price ledger. Include variant, condition, region/category in the product key and exact seller entity/marketplace identity in the seller key as needed to prevent evidence transfer.

Each evidence row has a unique `id` within the candidate, `claim`, HTTP(S) `url`, `checked_at`, `product_key`, `seller_key`, `authority`, `finding`, `currency`, and nonempty `observation`.

- Claims: `product_identity`, `seller_authorization`, `warranty`, `returns`.
- Authorities: `manufacturer`, `platform`, `seller`, `independent`, `unknown`. Assign from inspected provenance, never just a domain name or seller assertion.
- Findings: `supports`, `contradicts`, `unknown`.
- Evidence currency: `current`, `stale`, `unknown` (freshness, not money). The host must determine validity from source scope and dates. A recently visited archived page is not automatically current.
- Record the actual observation and scope, including warranty issuer/territory, return conditions, authorization category and unresolved limitations. Never include private identifiers or exact home addresses.

The audit accepts supporting product identity and seller authorization only from manufacturer-attributed evidence, warranty from manufacturer/platform/seller evidence, and returns from platform/seller evidence. Evidence must match both candidate keys and be current. Any exact-subject contradiction blocks the candidate, even if stale: resolve it in research and document why it no longer applies before removing it from the active ledger. Evidence with different keys cannot qualify or disqualify that candidate.

Outputs: `documented_checks`, `insufficient_evidence`, or `unresolved_conflict`; missing claims; conflicts; coverage gaps; and `documented_candidate_ids`. No overall trust score is produced. Status means records satisfy this conservative documented-channel checklist; **it does not verify URLs, facts, manufacturer authority, freshness, genuine goods, or exhaustive research**. The helper cannot inspect the physical unit and does not evaluate the separate unit-inspection route.

For authenticity-constrained requests, use ids only as a host-reviewed shortlist, then apply the normal price comparison rules to comparable available offers. Keep excluded evidence records and cheaper unverified alternatives visible. A candidate can have complete evidence records yet unknown shipping, no stock, a different warranty or the wrong requested variant; the audit does not override the price helper or the user's constraints. See [offer format](offer-format.md).
