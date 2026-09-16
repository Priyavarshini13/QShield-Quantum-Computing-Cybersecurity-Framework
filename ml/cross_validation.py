import os

import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import GroupKFold


# ---------------------------------------------------------
# PATH
# ---------------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATASET_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "qshield_dataset.csv"
)

RESULTS_DIR = os.path.join(
    PROJECT_ROOT,
    "experiments"
)

RESULTS_PATH = os.path.join(
    RESULTS_DIR,
    "cross_validation_results.csv"
)


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

df = pd.read_csv(DATASET_PATH)

print("=== QShield 5-Fold Circuit-Level Validation ===")

print("\nDataset shape:")
print(df.shape)


# ---------------------------------------------------------
# FEATURES
# ---------------------------------------------------------

features = [
    "num_qubits",
    "depth",
    "total_gates",
    "h_gates",
    "x_gates",
    "y_gates",
    "z_gates",
    "cx_gates",
    "cz_gates",
    "rx_gates",
    "ry_gates",
    "rz_gates",
    "measurement_gates",
    "barriers",
    "tvd",
    "noise_rate"
]

X = df[features]

y = df["label"]

groups = df["circuit_name"]


# ---------------------------------------------------------
# GROUP K-FOLD
# ---------------------------------------------------------

n_groups = groups.nunique()

n_splits = min(5, n_groups)

group_kfold = GroupKFold(
    n_splits=n_splits
)


accuracies = []
f1_scores = []


# ---------------------------------------------------------
# CROSS VALIDATION
# ---------------------------------------------------------

for fold, (train_idx, test_idx) in enumerate(
    group_kfold.split(
        X,
        y,
        groups
    ),
    start=1
):

    X_train = X.iloc[train_idx]
    X_test = X.iloc[test_idx]

    y_train = y.iloc[train_idx]
    y_test = y.iloc[test_idx]

    train_circuits = groups.iloc[
        train_idx
    ].nunique()

    test_circuits = groups.iloc[
        test_idx
    ].nunique()

    print(
        f"\n========== FOLD {fold} =========="
    )

    print(
        f"Training samples: {len(X_train)}"
    )

    print(
        f"Testing samples: {len(X_test)}"
    )

    print(
        f"Training circuits: {train_circuits}"
    )

    print(
        f"Testing circuits: {test_circuits}"
    )


    # -----------------------------------------------------
    # MODEL
    # -----------------------------------------------------

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    )


    # -----------------------------------------------------
    # TRAIN
    # -----------------------------------------------------

    model.fit(
        X_train,
        y_train
    )


    # -----------------------------------------------------
    # PREDICT
    # -----------------------------------------------------

    y_pred = model.predict(
        X_test
    )


    # -----------------------------------------------------
    # METRICS
    # -----------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    f1 = f1_score(
        y_test,
        y_pred
    )

    accuracies.append(
        accuracy
    )

    f1_scores.append(
        f1
    )


    print(
        f"Accuracy: {accuracy:.4f}"
    )

    print(
        f"F1 Score: {f1:.4f}"
    )


# ---------------------------------------------------------
# FINAL RESULTS
# ---------------------------------------------------------

accuracy_mean = sum(
    accuracies
) / len(accuracies)

accuracy_std = (
    pd.Series(accuracies).std(
        ddof=0
    )
)

f1_mean = sum(
    f1_scores
) / len(f1_scores)

f1_std = (
    pd.Series(f1_scores).std(
        ddof=0
    )
)


print(
    "\n========================================"
)

print(
    "FINAL CROSS-VALIDATION RESULTS"
)

print(
    "========================================"
)

print(
    "\nFold Accuracies:"
)

for i, score in enumerate(
    accuracies,
    start=1
):
    print(
        f"Fold {i}: {score:.4f}"
    )

print(
    "\nFold F1 Scores:"
)

for i, score in enumerate(
    f1_scores,
    start=1
):
    print(
        f"Fold {i}: {score:.4f}"
    )

print(
    f"\nMean Accuracy: "
    f"{accuracy_mean:.4f}"
)

print(
    f"Accuracy Std: "
    f"{accuracy_std:.4f}"
)

print(
    f"\nMean F1 Score: "
    f"{f1_mean:.4f}"
)

print(
    f"F1 Std: "
    f"{f1_std:.4f}"
)


# ---------------------------------------------------------
# SAVE RESULTS FOR DASHBOARD
# ---------------------------------------------------------

os.makedirs(
    RESULTS_DIR,
    exist_ok=True
)


results = []

for i in range(
    len(accuracies)
):

    results.append(
        {
            "fold": i + 1,
            "accuracy": accuracies[i],
            "f1_score": f1_scores[i]
        }
    )


# Add overall summary row

results.append(
    {
        "fold": "mean",
        "accuracy": accuracy_mean,
        "f1_score": f1_mean
    }
)


results_df = pd.DataFrame(
    results
)


results_df.to_csv(
    RESULTS_PATH,
    index=False
)


print(
    "\n========================================"
)

print(
    "RESULTS SAVED"
)

print(
    "========================================"
)

print(
    f"\nCross-validation results saved to:"
)

print(
    RESULTS_PATH
)