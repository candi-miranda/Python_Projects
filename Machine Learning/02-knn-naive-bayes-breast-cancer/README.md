# kNN vs. Naïve Bayes — Breast Cancer Diagnosis

A statistically rigorous comparison between two classic classifiers applied to breast cancer diagnosis, focused on the statistical validity of the conclusions — not just on which model "wins".

## What was done

- **Baseline**: accuracy comparison between kNN (k=5) and Gaussian Naïve Bayes using stratified cross-validation, also evaluating the stability (standard deviation) of each model.
- **Impact of preprocessing**: re-evaluated kNN after Min-Max normalization, to isolate the effect of feature scale on a distance-based classifier.
- **Statistical significance**: statistical test (via `scipy`) to determine whether the observed improvement in scaled kNN is statistically significant compared to Naïve Bayes, avoiding conclusions based on what could be sampling noise.
- **Sensitivity study**: varied `k ∈ {1, 5, 10, 15, 20, 25}` with uniform vs. distance-weighted voting, analyzing the bias-variance trade-off.
- **Applied discussion**: critical analysis of which classifier would be more appropriate in a real clinical context, considering not just accuracy but also interpretability and the cost of errors.

## Key results

- After normalization, kNN accuracy rose from ~93.5% to ~96.3%, confirming this method's sensitivity to feature scale.
- Despite the improvement, the statistical test (p ≈ 0.068) did not confirm a statistically significant superiority of scaled kNN over Naïve Bayes — a meaningful conclusion that only cross-validation + a statistical test can provide (comparing means alone would be misleading).

## Stack

`pandas` · `scikit-learn` (`KNeighborsClassifier`, `GaussianNB`) · `scipy`

## How to run

```bash
pip install pandas scikit-learn scipy
jupyter notebook knn_vs_naive_bayes.ipynb
```

> Note: the notebook expects the `Breast_cancer_dataset.csv` file in the same folder.
