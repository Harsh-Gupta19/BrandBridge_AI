# Notebooks Guide

Exploratory analysis, feature engineering experiments, model experiments, and evaluation notebooks belong here.

Notebook code is for learning and experimentation. It is not production backend code.

## Folder Structure

```text
notebooks/
|-- data_analysis/
|-- feature_engineering/
|-- model_experiments/
|-- evaluation/
```

## `data_analysis/`

Use this folder to understand creator, campaign, proposal, or social metric data.

## `feature_engineering/`

Use this folder to test matching features such as:

- `category_similarity`
- `audience_match`
- `country_match`
- `platform_match`
- `budget_match`
- `engagement_rate`
- `follower_score`
- `semantic_similarity`
- `creator_reliability`

## `model_experiments/`

Use this folder to compare models such as:

- Logistic Regression
- Random Forest
- XGBoost

## `evaluation/`

Use this folder to evaluate whether recommendations are useful and explainable.

## Moving Notebook Code Into Production

When an experiment becomes useful:

1. Move reusable feature code to `backend/app/ml/features/`.
2. Move training code to `backend/app/ml/training/`.
3. Move model scoring code to `backend/app/ml/inference/`.
4. Add tests.
5. Update docs.

Do not directly import notebooks from FastAPI routes.
