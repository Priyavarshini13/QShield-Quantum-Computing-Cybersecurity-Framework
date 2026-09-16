import os
import sys

import pandas as pd

from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
)

from sklearn.svm import SVC

from sklearn.model_selection import (
    GroupKFold,
    cross_validate,
)

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# FILE PATHS
# ============================================================

DATASET_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "qshield_dataset.csv"
)

OUTPUT_PATH = os.path.join(
    PROJECT_ROOT,
    "experiments",
    "model_comparison_results.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

FEATURES = [
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
    "noise_rate",
]

TARGET = "label"

# Circuit-level validation
N_SPLITS = 5


# ============================================================
# LOAD DATASET
# ============================================================

def load_data():
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(
            f"Dataset not found:\n{DATASET_PATH}"
        )

    df = pd.read_csv(DATASET_PATH)

    required_columns = FEATURES + [TARGET]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns:\n"
            + "\n".join(missing_columns)
        )

    return df


# ============================================================
# FIND CIRCUIT GROUP COLUMN
# ============================================================

def get_groups(df):
    """
    Find a circuit identifier column for
    circuit-level GroupKFold validation.

    This prevents rows belonging to the same
    circuit from being split across train/test folds.
    """

    possible_columns = [
        "circuit",
        "circuit_name",
        "circuit_file",
        "filename",
        "file",
    ]

    for column in possible_columns:
        if column in df.columns:
            return df[column]

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------
    #
    # If the dataset does not contain a circuit identifier,
    # use row indices as groups.
    #
    # This keeps the script executable, but the resulting
    # validation is not circuit-level.
    #

    print(
        "WARNING: No circuit identifier column found."
    )

    print(
        "Using row indices as groups."
    )

    return pd.Series(
        range(len(df)),
        index=df.index
    )


# ============================================================
# DEFINE MODELS
# ============================================================

def create_models():

    models = {

        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            n_jobs=-1,
            class_weight="balanced"
        ),

        "SVM": Pipeline(
            [
                (
                    "scaler",
                    StandardScaler()
                ),
                (
                    "classifier",
                    SVC(
                        kernel="rbf",
                        probability=True,
                        class_weight="balanced",
                        random_state=42
                    )
                )
            ]
        ),

        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=150,
            learning_rate=0.05,
            max_depth=3,
            random_state=42
        ),
    }

    return models


# ============================================================
# MODEL EVALUATION
# ============================================================

def evaluate_models(df):

    X = df[FEATURES]

    y = df[TARGET]

    groups = get_groups(df)

    models = create_models()

    unique_groups = groups.nunique()

    n_splits = min(
        N_SPLITS,
        unique_groups
    )

    if n_splits < 2:
        raise ValueError(
            "At least 2 groups are required "
            "for cross-validation."
        )

    cv = GroupKFold(
        n_splits=n_splits
    )

    scoring = [
        "accuracy",
        "precision",
        "recall",
        "f1",
    ]

    results = []

    print()
    print("=" * 70)
    print("QSHIELD ML MODEL COMPARISON")
    print("=" * 70)

    print()
    print(
        f"Dataset rows: {len(df)}"
    )

    print(
        f"Features: {len(FEATURES)}"
    )

    print(
        f"Circuit groups: {unique_groups}"
    )

    print(
        f"Cross-validation folds: {n_splits}"
    )

    print()

    for model_name, model in models.items():

        print(
            f"Evaluating {model_name}..."
        )

        scores = cross_validate(
            model,
            X,
            y,
            groups=groups,
            cv=cv,
            scoring=scoring,
            n_jobs=-1,
            return_train_score=False
        )

        accuracy_mean = (
            scores["test_accuracy"].mean()
        )

        accuracy_std = (
            scores["test_accuracy"].std()
        )

        precision_mean = (
            scores["test_precision"].mean()
        )

        recall_mean = (
            scores["test_recall"].mean()
        )

        f1_mean = (
            scores["test_f1"].mean()
        )

        f1_std = (
            scores["test_f1"].std()
        )

        result = {
            "Model": model_name,
            "Accuracy Mean": round(
                accuracy_mean,
                4
            ),
            "Accuracy Std": round(
                accuracy_std,
                4
            ),
            "Precision": round(
                precision_mean,
                4
            ),
            "Recall": round(
                recall_mean,
                4
            ),
            "F1 Mean": round(
                f1_mean,
                4
            ),
            "F1 Std": round(
                f1_std,
                4
            ),
            "CV Folds": n_splits,
        }

        results.append(result)

        print(
            f"  Accuracy : "
            f"{accuracy_mean:.4f} "
            f"+/- {accuracy_std:.4f}"
        )

        print(
            f"  Precision: "
            f"{precision_mean:.4f}"
        )

        print(
            f"  Recall   : "
            f"{recall_mean:.4f}"
        )

        print(
            f"  F1 Score : "
            f"{f1_mean:.4f} "
            f"+/- {f1_std:.4f}"
        )

        print()

    return pd.DataFrame(
        results
    )


# ============================================================
# SAVE RESULTS
# ============================================================

def save_results(results):

    results.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print(
        "Results saved to:"
    )

    print(
        OUTPUT_PATH
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print(
        "Loading QShield dataset..."
    )

    df = load_data()

    results = evaluate_models(
        df
    )

    save_results(
        results
    )

    print()
    print("=" * 70)
    print("FINAL MODEL COMPARISON")
    print("=" * 70)

    print()

    print(
        results.to_string(
            index=False
        )
    )

    print()
    print(
        "Model comparison completed successfully."
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()