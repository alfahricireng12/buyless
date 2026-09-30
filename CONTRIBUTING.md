# Contributing to BuyLess

BuyLess is an AI skill, not an API service or shopping application. Contributions should improve what a user's existing assistant searches, checks, calculates, and explains.

## Useful contributions

- Local-language discovery methods and regional research pitfalls with dated examples; do not add retailer lists or country allowlists.
- Product-equivalence cases: variants, condition, warranty, quantity, and regional compatibility.
- Promotion rules and counterexamples where a headline discount is misleading.
- Evidence-quality improvements and realistic behavioral evaluation cases.
- Deterministic helper fixes with tests demonstrating the error.

Keep repository prose, comments, and issue discussions in English. Multilingual query examples are welcome with an English explanation.

## Before a pull request

1. Keep the change focused on an observed problem.
2. Read the relevant section of `SKILL.md`; avoid repeating it in references.
3. Provide a sanitized example and an expected observable outcome.
4. Run `python scripts/validate_repo.py`.
5. Run `python -m unittest discover -s tests -v` when helper behavior changes.
6. State whether any evidence is synthetic, recorded, or observed live.

Do not require a particular paid search provider, embed API keys, add unnecessary dependencies, or introduce a static store registry. Discover stores at research time from the user's location.

## Skill quality

Keep the entrypoint short and load detailed references only when needed. Avoid tool names specific to a single host unless isolated in optional host metadata. Preserve the user's product, location, budget, language, and authorization scope.

The cheapest comparable cost remains the primary objective. Missing charges stay unknown; cashback stays separate; map listings do not become stock evidence; online research does not become a guarantee of authenticity.

## Tests and evaluations

Helper unit tests check arithmetic and validation. Behavioral scenarios require actually running a host AI and observing its output. Do not report scenario definitions as passed model evaluations.

Do not use private addresses, session cookies, credentials, or unlicensed bulk catalogs in fixtures. Respectful, specific reviews and maintained regional knowledge are more useful than a large unverified retailer list.

\n