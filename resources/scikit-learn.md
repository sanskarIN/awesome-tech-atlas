# scikit-learn documentation

**Official source:** https://scikit-learn.org/stable/  
**Type:** official docs  
**Category:** [AI & machine learning](../categories/artificial-intelligence-machine-learning.md) · Classical machine learning  
**Last official-page inspection:** 2026-11-08

## Why it matters

Documentation for Python estimators, preprocessing, model selection, and evaluation utilities.

## Good fit

Regression, classification, and evaluation with conventional machine-learning algorithms.

## Strength and trade-off

- **Strength:** Consistent estimator APIs support comparison across many conventional models.
- **Limitation:** Not a replacement for all deep-learning training stacks; evaluation quality depends on data splits and leakage controls.

These are contextual selection notes, **not** independent speed, reliability, or security benchmarks.

## Try it

Follow the getting-started example and evaluate a simple estimator on a held-out test set.


## Worked example: classify flowers without preprocessing leakage

### Prerequisites

- Python 3.10+ and a compatible scikit-learn installation in a virtual environment (follow the [official installation guide](https://scikit-learn.org/stable/install.html)).
- Save the original script below as \`iris_split.py\`. It uses a dataset bundled with scikit-learn; no downloaded dataset is needed.

### Steps

Run \`python iris_split.py\`:

~~~python
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500))
model.fit(X_train, y_train)
predictions = model.predict(X_test)

print(f"train: {len(y_train)}, test: {len(y_test)}")
print("confusion matrix shape:", confusion_matrix(y_test, predictions).shape)
~~~

Notice that \`StandardScaler\` is fitted **inside** the pipeline using training data only. The held-out test set is used for prediction after fitting.

### Expected result

~~~text
train: 120, test: 30
confusion matrix shape: (3, 3)
~~~

These are dataset sizes and matrix dimensions—not an accuracy guarantee or benchmark.

### Troubleshooting

- If \`sklearn\` cannot be imported, install it in the same Python environment used to run the script.
- If a solver or numerical dependency fails, compare your Python and scikit-learn versions with the supported versions in the upstream installation guide.
- For real data, handle missing values, class imbalance, repeated entities, and leakage before interpreting metrics.

### Evidence and execution status

- **Primary references:** [train/test splitting](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html), [pipelines](https://scikit-learn.org/stable/modules/compose.html), and [common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html).
- **Reviewed:** 2026-11-09 (example-specific documentation). **Executed locally:** scikit-learn 1.8.0 and Python 3.13.5; the displayed shape and counts matched.
- This exercise does not establish predictive validity for any real-world domain. The catalog's earlier official-source inspection date remains unchanged.

## Where to go next

- Read the [upstream documentation](https://scikit-learn.org/stable/) for setup, compatible versions, and API details.
- **Alternative:** [PyTorch documentation](pytorch.md). Use a tensor-based framework when defining and optimizing neural-network architectures.

**Verification scope:** The linked upstream documentation was inspected on 2026-11-08. Runtime behavior, licensing details for specific distributions, and installation on every platform were not independently tested. Check the project's official terms and release information before reuse or deployment.
