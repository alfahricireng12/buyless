# Offline examples

Every product, seller, price, coupon, and source in [offers.synthetic.json](offers.synthetic.json) is fictional. Reserved `.invalid` source addresses intentionally do not resolve.

Run from the skill root:

```sh
python scripts/compare_offers.py examples/offers.synthetic.json --format markdown
python scripts/compare_offers.py examples/offers.synthetic.json --format json
```

The example includes two comparable delivered offers, one nearby pickup payment, an overseas estimate, a quote with missing charges, and a rejected variant. Read the [generated comparison](comparison.synthetic.md) without running Python.

Expected complete delivered comparison:

- Fictional Domestic A: 4,200,000 − 300,000 capped coupon + 25,000 shipping = **IDR 3,925,000**.
- Fictional Domestic B: 3,980,000 + 20,000 shipping = **IDR 4,000,000**.

IDR 100,000 cashback is separate. The nearby pickup payment is IDR 3,850,000 before travel. The overseas USD subtotal is not converted or declared cheapest because currency and missing fees require further evidence. The IDR 3,700,000 incomplete quote cannot displace the complete delivered winner.

This example validates the calculation/reporting path only. It is not a shopping recommendation, live demonstration, or evidence of any seller's authenticity.

## Research record audit

[research.synthetic.json](research.synthetic.json) contains fictional source attempts and evidence records, using reserved `.invalid` addresses. Run:

```sh
python scripts/audit_research.py examples/research.synthetic.json
```

Expected: `domestic-a` has `documented_checks`, `shipping-unknown` has `insufficient_evidence`, and international coverage has a gap because its source is blocked. These are record-completeness results, not verification of facts or genuine products. Candidate ids link to the price example, but evidence status does not override missing charges, availability or comparison groups.

\n