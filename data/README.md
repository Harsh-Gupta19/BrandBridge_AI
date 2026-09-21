# Data Guide

This directory contains development-only sample and synthetic data.

Do not put real user data here.

## Folder Structure

```text
data/
|-- samples/
|-- synthetic/
```

## `samples/`

Small hand-written JSON files for UI development and early backend testing.

Current examples:

- `creator.sample.json`
- `campaign.sample.json`
- `transformed_creator.sample.json`

`transformed_creator.sample.json` is the reference output for social-media
transformers. It separates shared creator identity, normalized platform metrics,
platform-specific fields, audience and commercial data, matching features,
quality checks, and source provenance. Keep unavailable values as `null`; use
zero only when the source explicitly reports zero.

These files help the team build screens and understand expected data shapes before real APIs are implemented.

## `synthetic/`

Generated fake datasets for experiments.

Use this for:

- ML experiments
- Feature engineering tests
- Demo data that does not contain real user information

## Important Rules

- Do not mix sample JSON with production database code.
- Do not commit secrets.
- Do not commit private user information.
- Keep sample files small enough to review in pull requests.

Production data should be loaded through migrations, seed scripts, or application services when those workflows exist.
