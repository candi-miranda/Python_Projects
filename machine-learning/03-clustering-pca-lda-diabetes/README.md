# Clustering, PCA & LDA — Diabetes Risk Analysis

Unsupervised exploration and dimensionality reduction applied to clinical data, comparing clustering and projection approaches for class separation.

## What was done

**Part A — Clustering**
- K-Means with `k ∈ {2, ..., 11}`, SSE analysis (elbow curve) to choose the number of clusters.
- Majority-class labeling for each cluster (k=6), evaluating accuracy, precision, and other indirect classification metrics.
- Identification of the most discriminative clusters and clinical interpretation of their centers (what kind of patient profile each cluster represents).

**Part B — Dimensionality reduction**
- PCA with analysis of cumulative explained variance, to decide how many components to retain.
- Visualization of class distribution along the 1st principal component.
- LDA as a supervised alternative, optimized directly for class separation.
- Critical comparison between PCA and LDA regarding their suitability for building a discriminant rule.

## Key results

- K-Means clustering (k=6) achieved ~70% indirect accuracy in distinguishing diabetic/non-diabetic patients, with clusters clearly dominated by one class (e.g., one cluster with 254 non-diabetic vs. 26 diabetic patients).
- PCA's PC1 showed considerable class overlap — expected, since PCA optimizes total variance rather than class separation.
- LDA, despite being optimized for separation, still revealed significant overlap, suggesting the available features don't perfectly separate the classes — an important conclusion about the limits of the dataset, not the method.

## Stack

`pandas` · `scikit-learn` (`KMeans`, `PCA`, `LDA`) · `matplotlib`

## How to run

```bash
pip install pandas scikit-learn matplotlib
jupyter notebook clustering_pca_lda.ipynb
```

> Note: the notebook expects the `diabetes.csv` file in the same folder.
