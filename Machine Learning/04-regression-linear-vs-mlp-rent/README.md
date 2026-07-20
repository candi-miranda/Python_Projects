# Linear Regression vs. MLP — Rent Prediction

Manual implementation of a training and cross-validation pipeline to compare a linear model against neural networks of increasing complexity for rent price prediction.

## What was done

- **Manual training and cross-validation function**, not relying solely on ready-made scikit-learn utilities, for greater control over the evaluation process (`KFold`, `cross_val_score`).
- Comparison between three models:
  - Linear Regression (baseline)
  - MLP Regressor (2 hidden layers, 5 neurons each, no activation function — effectively a "disguised" linear model)
  - MLP Regressor (2 hidden layers, 5 neurons each, ReLU activation)
- Analysis of **loss curves** for the ReLU-based MLP across epochs, to diagnose overfitting vs. underfitting.
- Critical discussion of error magnitude (MAE/MSE), not just the shape of the curve — avoiding premature, overly optimistic conclusions.

## Key results

- Manual training performed slightly better than the automatic pipeline, with no notable differences between the MLP and linear regression — a sign of limitations in the data (noise, uninformative features, or weak non-linearities) rather than in model capacity.
- The ReLU-based MLP's loss curve improves over epochs, but the final error magnitude reveals that the visual "improvement" doesn't necessarily translate into practical predictive quality.

## Stack

`pandas` · `numpy` · `scikit-learn` (`LinearRegression`, `Ridge`, `MLPRegressor`) · `matplotlib`

## How to run

```bash
pip install pandas numpy scikit-learn matplotlib
jupyter notebook regression_models.ipynb
```

> Note: the notebook expects the `rent.csv` file in the same folder.
