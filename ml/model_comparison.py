import os

import pandas as pd

from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier
)

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score
)

from sklearn.model_selection import GroupKFold

from sklearn.pipeline import Pipeline

from sklearn.preprocessing import StandardScaler

from sklearn.svm import SVC


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


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

df = pd.read_csv(DATASET_PATH)

print("=== QShield ML Model Comparison ===")

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
# MODELS
# ---------------------------------------------------------

models = {

    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    ),

    "SVM": Pipeline([
        (
            "scaler",
            StandardScaler()
        ),
        (
            "classifier",
            SVC(
                kernel="rbf",
                class_weight="balanced",
                random_state=42
            )
        )
    ]),

    "Gradient Boosting": GradientBoostingClassifier(
        n_estimators=150,
        learning_rate=0.05,
        max_depth=3,
        random_state=42
    )
}


# ---------------------------------------------------------
# 5-FOLD CIRCUIT-LEVEL CROSS VALIDATION
# ---------------------------------------------------------

group_kfold = GroupKFold(
    n_splits=5
)


results = []


# ---------------------------------------------------------
# MODEL LOOP
# ---------------------------------------------------------

for model_name, model in models.items():

    print(
        f"\n\n========================================"
    )

    print(
        f"MODEL: {model_name}"
    )

    print(
        "========================================"
    )

    fold_accuracies = []
    fold_precisions = []
    fold_recalls = []
    fold_f1_scores = []


    # -----------------------------------------------------
    # FOLD LOOP
    # -----------------------------------------------------

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


        # -------------------------------------------------
        # TRAIN
        # -------------------------------------------------

        model.fit(
            X_train,
            y_train
        )


        # -------------------------------------------------
        # PREDICT
        # -------------------------------------------------

        y_pred = model.predict(
            X_test
        )


        # -------------------------------------------------
        # METRICS
        # -------------------------------------------------

        accuracy = accuracy_score(
            y_test,
            y_pred
        )

        precision = precision_score(
            y_test,
            y_pred,
            zero_division=0
        )

        recall = recall_score(
            y_test,
            y_pred,
            zero_division=0
        )

        f1 = f1_score(
            y_test,
            y_pred,
            zero_division=0
        )


        fold_accuracies.append(
            accuracy
        )

        fold_precisions.append(
            precision
        )

        fold_recalls.append(
            recall
        )

        fold_f1_scores.append(
            f1
        )


        print(
            f"\nFold {fold}"
        )

        print(
            f"Accuracy : {accuracy:.4f}"
        )

        print(
            f"Precision: {precision:.4f}"
        )

        print(
            f"Recall   : {recall:.4f}"
        )

        print(
            f"F1 Score : {f1:.4f}"
        )


    # -----------------------------------------------------
    # MEAN / STANDARD DEVIATION
    # -----------------------------------------------------

    accuracy_mean = (
        pd.Series(
            fold_accuracies
        ).mean()
    )

    accuracy_std = (
        pd.Series(
            fold_accuracies
        ).std(
            ddof=0
        )
    )

    precision_mean = (
        pd.Series(
            fold_precisions
        ).mean()
    )

    recall_mean = (
        pd.Series(
            fold_recalls
        ).mean()
    )

    f1_mean = (
        pd.Series(
            fold_f1_scores
        ).mean()
    )

    f1_std = (
        pd.Series(
            fold_f1_scores
        ).std(
            ddof=0
        )
    )


    # -----------------------------------------------------
    # MODEL SUMMARY
    # -----------------------------------------------------

    print(
        "\n--- Model Summary ---"
    )

    print(
        f"Mean Accuracy : {accuracy_mean:.4f}"
    )

    print(
        f"Accuracy Std  : {accuracy_std:.4f}"
    )

    print(
        f"Mean Precision: {precision_mean:.4f}"
    )

    print(
        f"Mean Recall   : {recall_mean:.4f}"
    )

    print(
        f"Mean F1       : {f1_mean:.4f}"
    )

    print(
        f"F1 Std        : {f1_std:.4f}"
    )


    results.append({
        "Model": model_name,
        "Accuracy": accuracy_mean,
        "Accuracy Std": accuracy_std,
        "Precision": precision_mean,
        "Recall": recall_mean,
        "F1 Score": f1_mean,
        "F1 Std": f1_std
    })


# ---------------------------------------------------------
# FINAL COMPARISON
# ---------------------------------------------------------

results_df = pd.DataFrame(
    results
)

results_df = results_df.sort_values(
    by="F1 Score",
    ascending=False
)


print(
    "\n\n========================================"
)

print(
    "FINAL MODEL COMPARISON"
)

print(
    "========================================"
)

print(
    results_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


# ---------------------------------------------------------
# BEST MODEL
# ---------------------------------------------------------

best_model = results_df.iloc[0]

print(
    "\n========================================"
)

print(
    "BEST MODEL"
)

print(
    "========================================"
)

print(
    f"Model: {best_model['Model']}"
)

print(
    f"Accuracy: {best_model['Accuracy']:.4f}"
)

print(
    f"F1 Score: {best_model['F1 Score']:.4f}"
)