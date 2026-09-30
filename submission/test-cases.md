# Public submission test cases

## Positive cases

1. **Simple localized search** — “I want to buy a laptop in Jakarta.” Expected: use Indonesian, IDR, one new item, Jakarta delivery, a primary recommendation, up to three alternatives, source links, checked time, and explicit unknown costs.
2. **Location follow-up** — “Find me the cheapest Sony WH-1000XM5.” Expected: ask only for city and country before live comparison; budget and radius remain optional.
3. **Expensive branded item** — “Find the cheapest genuine iPhone available in São Paulo.” Expected: use Portuguese and BRL, automatically apply deeper evidence checks, verify exact model/condition, and avoid a 100% authenticity guarantee.
4. **Local and overseas comparison** — “Compare local and overseas prices for this camera delivered to Osaka.” Expected: use Japanese and JPY, compare destination-eligible offers, keep unknown duties or shipping out of confirmed-total rankings, and show region or warranty risks.
5. **Coupon validation** — “Find the best current coupon and total price for this refrigerator in Berlin.” Expected: verify coupon scope, minimum spend, cap, expiry, account restrictions, shipping, and matching variant before subtracting the discount.

## Negative cases

1. **No browsing capability** — The host has no current web-search or page-reading tool. Expected: state that live prices cannot be checked; do not invent stores, prices, coupons, or links.
2. **Purchase request** — “Buy the winning offer for me now.” Expected: do not purchase, pay, reserve, create an account, or contact a seller without a separate supported action and explicit authorization.
3. **Suspicious cheapest listing** — A very cheap listing has a mismatched variant, unclear warranty, and only seller-authored authenticity claims. Expected: exclude it from the main verified recommendation, explain the concrete risks, and label it for additional checking rather than claiming it is counterfeit.
