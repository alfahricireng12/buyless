# Price and promotion rules

Compare the chosen variant and quantity, not the lowest displayed variant, deposit, installment, or “from” price.

```text
Payable total = item subtotal
             - eligible immediate discounts
             + shipping after applicable shipping promotions
             + fees, taxes, and import charges not already included
```

Do not count an already applied discount twice. Unknown fees are not zero. Show original currency; conversion needs a rate source and observation time, and may still differ from the payment provider's charge. Import rates must come from current destination-relevant evidence or an observed quote, not model memory.

## Coupon checks

Record the actual code or automatic discount, source URL, observation time, eligible products/sellers, validity, minimum spend, cap, calculation base, payment method, account restrictions, and stacking rule. Search official platform, seller, and payment-provider pages. Coupon aggregators are leads until the terms are confirmed.

Use `confirmed` only when the relevant terms and user context are supported. New-user, membership, card, quota, and personalized conditions remain unknown when the account context is missing. Do not silently assume the user has a particular card or unused voucher.

Separate:

- Immediate price reduction.
- Shipping reduction.
- Cashback, points, or later credit.
- Financing/installments.

Evaluate stacking only when the source explicitly permits the combination and the calculation order/base is known. The bundled helper deliberately selects one eligible item coupon at a time; it does not optimize stacking or shipping vouchers. Compute more complex documented rules separately and include the trace.

## Comparison groups

Only compare equivalent products, condition, quantity, warranty/region, fulfillment method, and currency. Complete delivery totals belong together. Nearby pickup payments belong in a separate group if travel cost is unknown. Incomplete totals and unknown destination eligibility cannot win the cheapest complete comparison.

Current prices can change after observation. Use “observed at checkout” only for an actual checkout observation; browsing a listing does not verify every account-specific fee.

## Using the helper

Read [offer-format.md](offer-format.md) and write observations to a local JSON file. From the skill root:

```sh
python scripts/compare_offers.py observations.json --format markdown
python scripts/compare_offers.py observations.json --format json
```

The script does no network access. Output inherits the quality of input evidence. A mathematically complete quote is not a verified real-world price. Do not upgrade a source's certainty because the script produced a number.
