import os

import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)
from sklearn.model_selection import GroupShuffleSplit


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

print("=== QShield ML Circuit-Level Evaluation ===")

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
# CIRCUIT-LEVEL TRAIN / TEST SPLIT
# ---------------------------------------------------------

splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.20,
    random_state=42
)

train_indices, test_indices = next(
    splitter.split(
        X,
        y,
        groups=groups
    )
)

X_train = X.iloc[train_indices]
X_test = X.iloc[test_indices]

y_train = y.iloc[train_indices]
y_test = y.iloc[test_indices]


print("\nTraining samples:")
print(len(X_train))

print("\nTesting samples:")
print(len(X_test))

print("\nTraining circuits:")
print(
    df.iloc[train_indices]["circuit_name"]
    .nunique()
)

print("\nTesting circuits:")
print(
    df.iloc[test_indices]["circuit_name"]
    .nunique()
)


# ---------------------------------------------------------
# RANDOM FOREST
# ---------------------------------------------------------

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

print("\nTraining Random Forest...")

model.fit(
    X_train,
    y_train
)


# ---------------------------------------------------------
# PREDICTION
# ---------------------------------------------------------

y_pred = model.predict(
    X_test
)


# ---------------------------------------------------------
# EVALUATION
# ---------------------------------------------------------

accuracy = accuracy_score(
    y_test,
    y_pred
)

print("\n=== MODEL RESULTS ===")

print(
    f"\nAccuracy: {accuracy:.4f}"
)

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "Normal",
            "Anomalous"
        ]
    )
)

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# ---------------------------------------------------------
# FEATURE IMPORTANCE
# ---------------------------------------------------------

importance = pd.DataFrame({
    "feature": features,
    "importance": model.feature_importances_
})

importance = importance.sort_values(
    by="importance",
    ascending=False
)

print("\n=== FEATURE IMPORTANCE ===")

print(
    importance.to_string(
        index=False
    )
)