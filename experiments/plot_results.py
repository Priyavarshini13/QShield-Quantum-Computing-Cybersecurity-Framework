import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import f1_score


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RESULTS_FILE = os.path.join(
    BASE_DIR,
    "experiments",
    "multicircuit_robustness_results.csv"
)

PLOTS_DIR = os.path.join(
    BASE_DIR,
    "experiments",
    "plots"
)

os.makedirs(PLOTS_DIR, exist_ok=True)


# ---------------------------------------------------------
# Load results
# ---------------------------------------------------------

df = pd.read_csv(RESULTS_FILE)

print(f"Loaded {len(df)} evaluation results.")


# Make sure noise is numeric
df["noise_rate"] = pd.to_numeric(df["noise_rate"])


# Consistent ordering
attack_order = [
    "normal",
    "gate_insertion",
    "gate_deletion",
    "gate_substitution",
    "multiple_gate_insertion"
]

noise_levels = sorted(df["noise_rate"].unique())


# ---------------------------------------------------------
# 1. Accuracy vs Noise Level
# ---------------------------------------------------------

accuracy_by_noise = (
    df.groupby("noise_rate")["correct"]
    .mean()
    .reset_index()
)

plt.figure(figsize=(8, 5))

plt.plot(
    accuracy_by_noise["noise_rate"],
    accuracy_by_noise["correct"],
    marker="o",
    linewidth=2
)

plt.xlabel("Noise Rate")
plt.ylabel("Accuracy")
plt.title("QShield Accuracy vs Noise Level")

plt.ylim(0, 1.05)
plt.grid(True, alpha=0.3)
plt.tight_layout()

path = os.path.join(PLOTS_DIR, "accuracy_vs_noise.png")
plt.savefig(path, dpi=300)
plt.close()

print(f"Saved: {path}")


# ---------------------------------------------------------
# 2. F1 Score vs Noise Level
# ---------------------------------------------------------

f1_scores = []

for noise in noise_levels:

    subset = df[df["noise_rate"] == noise]

    score = f1_score(
        subset["expected_label"],
        subset["predicted_label"],
        zero_division=0
    )

    f1_scores.append(score)


plt.figure(figsize=(8, 5))

plt.plot(
    noise_levels,
    f1_scores,
    marker="o",
    linewidth=2
)

plt.xlabel("Noise Rate")
plt.ylabel("F1 Score")
plt.title("QShield F1 Score vs Noise Level")

plt.ylim(0, 1.05)
plt.grid(True, alpha=0.3)
plt.tight_layout()

path = os.path.join(PLOTS_DIR, "f1_vs_noise.png")
plt.savefig(path, dpi=300)
plt.close()

print(f"Saved: {path}")


# ---------------------------------------------------------
# 3. Classification Correctness by Attack Type
# ---------------------------------------------------------

attack_accuracy = (
    df.groupby("attack_type")["correct"]
    .mean()
    .reindex(attack_order)
)

plt.figure(figsize=(9, 5))

plt.bar(
    attack_accuracy.index,
    attack_accuracy.values
)

plt.xlabel("Condition")
plt.ylabel("Classification Accuracy")
plt.title("QShield Classification Accuracy by Attack Type")

plt.ylim(0, 1.05)
plt.xticks(rotation=25, ha="right")
plt.grid(axis="y", alpha=0.3)

plt.tight_layout()

path = os.path.join(PLOTS_DIR, "attack_detection_rate.png")
plt.savefig(path, dpi=300)
plt.close()

print(f"Saved: {path}")


# ---------------------------------------------------------
# 4. TVD vs Noise Level
# ---------------------------------------------------------

plt.figure(figsize=(9, 5))

for attack in attack_order:

    subset = df[df["attack_type"] == attack]

    tvd_by_noise = (
        subset.groupby("noise_rate")["tvd"]
        .mean()
        .reindex(noise_levels)
    )

    plt.plot(
        noise_levels,
        tvd_by_noise.values,
        marker="o",
        linewidth=2,
        label=attack.replace("_", " ").title()
    )


plt.xlabel("Noise Rate")
plt.ylabel("Total Variation Distance (TVD)")
plt.title("Behavioral Difference (TVD) vs Noise Level")

plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

path = os.path.join(PLOTS_DIR, "tvd_vs_noise.png")
plt.savefig(path, dpi=300)
plt.close()

print(f"Saved: {path}")


# ---------------------------------------------------------
# 5. Average Risk Score by Attack Type
# ---------------------------------------------------------

risk_by_attack = (
    df.groupby("attack_type")["risk_score"]
    .mean()
    .reindex(attack_order)
)

plt.figure(figsize=(9, 5))

plt.bar(
    risk_by_attack.index,
    risk_by_attack.values
)

plt.xlabel("Condition")
plt.ylabel("Average Risk Score")
plt.title("Average QShield Risk Score by Condition")

plt.ylim(0, 105)
plt.xticks(rotation=25, ha="right")
plt.grid(axis="y", alpha=0.3)

plt.tight_layout()

path = os.path.join(PLOTS_DIR, "risk_score_by_attack.png")
plt.savefig(path, dpi=300)
plt.close()

print(f"Saved: {path}")


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

print("\nAll plots generated successfully.")

print("\nGenerated files:")

for filename in [
    "accuracy_vs_noise.png",
    "f1_vs_noise.png",
    "attack_detection_rate.png",
    "tvd_vs_noise.png",
    "risk_score_by_attack.png"
]:
    print(f"  experiments/plots/{filename}")