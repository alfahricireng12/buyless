# Public distribution

BuyLess supports two public distribution paths.

## Public Git marketplace

The repository marketplace is stored at `.agents/plugins/marketplace.json` and is named `buyless-community`. After this repository is hosted publicly, users can add it as a marketplace source with Codex using the repository URL or `owner/repository` shorthand, then install `buyless@buyless-community`.

The GitHub repository is [alfahricireng12/buyless](https://github.com/alfahricireng12/buyless). Install it as a community marketplace with `codex plugin marketplace add alfahricireng12/buyless`, then `codex plugin add buyless@buyless-community`.

## Universal ChatGPT and Codex Plugins Directory

BuyLess is a skills-only plugin. Submit `buyless-public-submission.zip` through the OpenAI plugin submission portal using the **Skills only** submission type.

Before submission, the publisher must provide:

- a verified individual or business identity for `devino.als` in the OpenAI Platform;
- Apps Management write permission in the publishing organization;
- public website, support, privacy-policy, and terms URLs;
- countries or regions where BuyLess will be available;
- five positive and three negative test cases;
- accurate policy attestations and release notes.

Submitting starts OpenAI review. Approval does not publish automatically; the verified publisher chooses **Publish** in the portal after approval. Only then may BuyLess claim to be available in the universal public Plugins Directory.

## Prepared materials

- `submission/listing.md`: public listing copy, starter prompts, availability, and release notes.
- `submission/test-cases.md`: five positive and three negative review cases.
- `PRIVACY.md`: data-handling statement for the skills-only package.
- `TERMS.md`: usage terms.
- `SUPPORT.md`: support process.
- `buyless-public-submission.zip`: upload package generated from `plugins/buyless`.

Verify that all four URLs in `submission/listing.md` are publicly accessible before submitting them to OpenAI.
