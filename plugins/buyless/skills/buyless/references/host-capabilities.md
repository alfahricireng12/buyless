# Host capabilities

BuyLess is instructions and optional local arithmetic. It supplies no network service, model, browser, credentials, or marketplace API access.

| Available capability | Useful behavior | Limitation to state |
|---|---|---|
| Web search and page reading | Discover sellers and inspect current listings | Some prices or variants may still require interactive access |
| Interactive browser | Inspect visible variants, delivery estimates, and promotion terms | Follow host rules for login and account actions |
| Authorized shopping connector | Use fields within its actual permission scope | Seller APIs do not automatically search all sellers |
| Search snippets only | Build candidate links and a clearly provisional comparison | Prices, inventory, and authenticity are not verified |
| User-provided links or observations only | Compare the supplied material and explain gaps | No claim of current or broad market coverage |
| Code execution with Python 3.11+ | Run the exact-money helper locally | The helper cannot validate factual inputs |

Never make a tool call based on an assumed universal tool name. The host owns discovery, browser selection, user approvals, network access, and execution permissions.

Do not ask for marketplace or model API keys as a prerequisite for using BuyLess. If the user's existing tools need their own setup, explain that host limitation and continue with available sources. Do not sign up for paid services or install tools as a side effect of a shopping request.

If a page requires sign-in, use the host's approved login flow or ask the user to take over as required. Public alternatives may provide useful but less complete information; do not describe them as access to the user's private checkout.

No search tools means no live shopping research. Do not create plausible stores, prices, coupons, citations, or maps to fill the gap.
