"""Train the model ladder: Logistic Regression -> Random Forest -> XGBoost.

Planned contents:
- split by campaign
- train and evaluate
- save versioned joblib artifact

Layer rule (Build Manual §3.1): takes a DataFrame; never queries the database or imports a service.
"""
