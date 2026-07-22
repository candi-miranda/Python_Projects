# Decision Trees for Heart Disease Diagnosis

Analysis of how decision tree hyperparameters affect a model's ability to generalize, applied to clinical diagnosis data.

## What was done

- **Preprocessing**: checked for missing values and verified that categorical variables were already numerically encoded.
- **Initial training**: stratified 80-20 split (fixed seed), varying `min_samples_leaf` over `{1, 3, 5, 10, 25, 50, 100}` to observe the overfitting/underfitting trade-off.
- **Structured validation**: 60-20-20 split (train/validation/test), with a grid search over `max_depth ∈ [2, 4]` and `min_samples_leaf ∈ [2, 100]` to select the model with the best validation performance, subject to a minimum test-accuracy threshold.
- **Clinical interpretability**: analysis of the leaf nodes associated with the positive class (heart disease) to identify decision paths and posterior probabilities — i.e., which combinations of clinical variables are most associated with a positive diagnosis.

## Key results

- Low values of `min_samples_leaf` lead to clear overfitting: high training accuracy but unstable test performance.
- The model selected via validation achieved ~77% test accuracy, close to the 78.5% target threshold.
- The leaf-node analysis identified which clinical variables contribute most to a positive diagnosis, giving the model an interpretable — not just predictive — reading.

## Stack

`pandas` · `scikit-learn` (`DecisionTreeClassifier`) · `matplotlib`

## How to run

```bash
pip install pandas scikit-learn matplotlib
jupyter notebook decision_trees.ipynb
```

> Note: the notebook expects the `hungarian_heart_diseases.csv` file in the same folder.
