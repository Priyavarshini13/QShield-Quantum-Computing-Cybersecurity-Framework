import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RESULTS_FILE = (
    PROJECT_ROOT
    / "experiments"
    / "security_evaluation_results.csv"
)

PLOTS_DIR = (
    PROJECT_ROOT
    / "experiments"
    / "plots"
)

PLOTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# LOAD RESULTS
# ============================================================

if not RESULTS_FILE.exists():

    print()
    print("ERROR: security_evaluation_results.csv not found.")
    print()
    print("Expected location:")
    print(RESULTS_FILE)
    print()

    sys.exit(1)


df = pd.read_csv(
    RESULTS_FILE
)


# ============================================================
# KEEP ONLY SUCCESSFUL RUNS
# ============================================================

df = df[
    df["status"] == "SUCCESS"
].copy()


if df.empty:

    print()
    print("ERROR: No successful evaluation results found.")
    print()

    sys.exit(1)


# ============================================================
# ATTACK ORDER
# ============================================================

attack_order = [
    "normal",
    "gate_insertion",
    "gate_deletion",
    "gate_substitution",
    "multiple_gate_insertion",
]


attack_labels = {
    "normal": "Normal",
    "gate_insertion": "Gate insertion",
    "gate_deletion": "Gate deletion",
    "gate_substitution": "Gate substitution",
    "multiple_gate_insertion": "Multiple insertion",
}


# ============================================================
# 1. SECURITY DETECTION RATE
# ============================================================

detection_data = []

for attack in attack_order:

    subset = df[
        df["attack_type"] == attack
    ]

    if len(subset) == 0:
        continue

    detected = (
        subset["prediction"] == 1
    ).sum()

    total = len(subset)

    detection_rate = (
        detected / total
    ) * 100

    detection_data.append(
        {
            "attack_type": attack,
            "label": attack_labels[attack],
            "detection_rate": detection_rate,
        }
    )


detection_df = pd.DataFrame(
    detection_data
)


plt.figure(
    figsize=(10, 6)
)

plt.bar(
    detection_df["label"],
    detection_df["detection_rate"],
)

plt.ylabel(
    "Detection Rate (%)"
)

plt.xlabel(
    "Security Condition"
)

plt.title(
    "QShield Security Anomaly Detection Rate"
)

plt.ylim(
    0,
    105
)

plt.xticks(
    rotation=20,
    ha="right"
)

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    PLOTS_DIR
    / "security_detection_rate.png",
    dpi=300,
)

plt.close()


# ============================================================
# 2. AVERAGE RISK SCORE
# ============================================================

risk_df = (
    df.groupby("attack_type")["risk_score"]
    .mean()
    .reindex(
        attack_order
    )
    .dropna()
    .reset_index()
)

risk_df["label"] = (
    risk_df["attack_type"]
    .map(attack_labels)
)


plt.figure(
    figsize=(10, 6)
)

plt.bar(
    risk_df["label"],
    risk_df["risk_score"],
)

plt.ylabel(
    "Average Risk Score"
)

plt.xlabel(
    "Security Condition"
)

plt.title(
    "QShield Average Security Risk Score"
)

plt.ylim(
    0,
    105
)

plt.xticks(
    rotation=20,
    ha="right"
)

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    PLOTS_DIR
    / "security_risk_score.png",
    dpi=300,
)

plt.close()


# ============================================================
# 3. AVERAGE TVD
# ============================================================

tvd_df = (
    df.groupby("attack_type")["tvd"]
    .mean()
    .reindex(
        attack_order
    )
    .dropna()
    .reset_index()
)

tvd_df["label"] = (
    tvd_df["attack_type"]
    .map(attack_labels)
)


plt.figure(
    figsize=(10, 6)
)

plt.bar(
    tvd_df["label"],
    tvd_df["tvd"],
)

plt.ylabel(
    "Average Total Variation Distance"
)

plt.xlabel(
    "Security Condition"
)

plt.title(
    "Behavioral Difference Between Ideal and Observed Circuits"
)

plt.xticks(
    rotation=20,
    ha="right"
)

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    PLOTS_DIR
    / "security_tvd.png",
    dpi=300,
)

plt.close()


# ============================================================
# 4. DETECTION RATE BY CIRCUIT
# ============================================================

circuit_data = []

for circuit in sorted(
    df["circuit"].unique()
):

    subset = df[
        df["circuit"] == circuit
    ]

    # Ignore normal condition for attack
    # detection performance.
    attack_subset = subset[
        subset["attack_type"] != "normal"
    ]

    if len(attack_subset) == 0:
        continue

    detected = (
        attack_subset["prediction"] == 1
    ).sum()

    total = len(
        attack_subset
    )

    detection_rate = (
        detected / total
    ) * 100

    circuit_data.append(
        {
            "circuit": circuit,
            "detection_rate": detection_rate,
        }
    )


circuit_df = pd.DataFrame(
    circuit_data
)

# Sort from lowest to highest
circuit_df = circuit_df.sort_values(
    "detection_rate"
)


plt.figure(
    figsize=(12, 8)
)

plt.barh(
    circuit_df["circuit"],
    circuit_df["detection_rate"],
)

plt.xlabel(
    "Attack Detection Rate (%)"
)

plt.ylabel(
    "Quantum Circuit"
)

plt.title(
    "QShield Attack Detection Across Benchmark Circuits"
)

plt.xlim(
    0,
    105
)

plt.grid(
    axis="x",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    PLOTS_DIR
    / "circuit_detection_rate.png",
    dpi=300,
)

plt.close()


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("QSHIELD SECURITY EVALUATION PLOTS")
print("=" * 70)
print()

print(
    f"Successful evaluation rows : {len(df)}"
)

print(
    f"Circuits represented       : {df['circuit'].nunique()}"
)

print()

print(
    "Generated plots:"
)

print()

print(
    "1. security_detection_rate.png"
)

print(
    "2. security_risk_score.png"
)

print(
    "3. security_tvd.png"
)

print(
    "4. circuit_detection_rate.png"
)

print()

print(
    "Saved to:"
)

print(
    PLOTS_DIR
)

print()