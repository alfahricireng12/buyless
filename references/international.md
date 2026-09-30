# Any country, local research

BuyLess has no country allowlist, retailer catalog, default destination or required marketplace. Every country uses the same dynamic discovery workflow. Availability of tools, accessible commerce data, delivery and promotions must be established per request; universal usability is not a claim of verified live coverage in every country.

## Build the locale from the request

- Use the user's country and city/region. Resolve ambiguous place names with a short clarification when needed. Respect privacy: a city or selected reference point is enough for discovery; an exact address is not required to start.
- Default the shopping report to the destination's local language, following the selection rules below. Search in locally used commerce languages as well as the brand's terminology, independently of the report language. Preserve model numbers, scripts, accents and transliterations; translate category terms rather than changing product identity.
- Use the destination currency with an explicit currency code. Preserve original amounts and local number formats in source notes; normalize decimal/thousands separators carefully. Do not assume that `$` means USD or that all currencies have two decimal places.
- Record timestamps with timezone/UTC offset. Check promotion dates in the seller's applicable timezone, including campaigns spanning midnight. Do not infer location from language, currency or the host clock.

## Select the report language

1. An explicit user language preference takes priority, including one established earlier in the conversation. Merely writing the shopping request in a language is not an explicit override of destination-based output.
2. Otherwise use the language normally used for commerce in the destination country, refined by the supplied city or region. Do not equate a country with exactly one language or infer the user's nationality.
3. In multilingual locations without a clear regional default, use the request language when it is locally used. If that does not resolve the choice, ask one short language question while continuing independent research. Do not interrupt for a language choice when a reasonable local default is clear.
4. For a multi-country comparison, use the primary delivery/pickup destination's language. Overseas seller locations do not change the report language. Keep source names and product identifiers intact and explain source observations in the report language.

Examples of defaults: Miami, United States → English; Jakarta, Indonesia → Indonesian; Osaka, Japan → Japanese; Montreal, Quebec → French. These illustrate selection, not a country/language allowlist. A request for an Indonesian answer about Miami overrides the English default. Spanish queries may still improve Miami discovery even when the report is in English.

Localize table headings, price explanations, dates and evidence labels consistently. Keep explicit currency codes and timezone offsets so localization does not make amounts or expiry times ambiguous. Repository documentation and helper field names remain in English; translate their meaning in the user-facing report.

## Discover shops from location

Search local-language equivalents of product + city + buy/store/pickup, product + country + price, and brand + country + authorized dealer. Discover domestic marketplaces, specialist retailers, brand distributors, store directories and local outlets. Validate the actual seller and destination before using a candidate. Cross-border regional platforms can be relevant even when the seller is in a neighboring country.

Classifieds, informal storefronts and social commerce may be leads where relevant, but do not invent inventory, authorization or buyer protection. Do not log in, contact sellers or move transactions off-platform without separate authorization. If public prices are scarce, report leads and missing quotes instead of pretending that the country is unsupported or producing fictional totals.

## Compare across borders responsibly

Check destination-specific shipping, remote-area fees, postal coverage, currency conversion charges, imports/taxes already included versus payable later, and return-shipping costs. Read current official customs or tax guidance when needed; do not generalize one country's thresholds to another. Retain unknown costs. Do not assume package forwarding, a payment method, membership or residency.

Check voltage, plug, keyboard, cellular bands, region locks, sizing standards, labels, warranty territory and service access where relevant to the category. Geographic proximity does not imply compatibility or legal availability. If an item cannot serve the destination, exclude it from purchasable comparisons and explain why.

Compare original-currency groups separately unless a timestamped exchange-rate source and conversion method are supplied. The optional calculator currently rounds IDR/JPY/KRW to whole units and other currencies to two decimals. For other precision rules (for example three-decimal currencies), use the host's precise calculator and current currency rules instead; do not silently lose precision through the helper.

## Expand through contributions

Regional contributions should explain discovery language, source categories, shipping scope and known access limitations with dated sources. A new country does not require a new code adapter or API subscription. Never label untested stores as integrations or display a blanket "all countries verified" badge.
