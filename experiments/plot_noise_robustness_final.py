from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "experiments"
    / "noise_robustness_calibrated_results.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "experiments"
    / "plots"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# LOAD DATA
# ============================================================

print()
print("=" * 70)
print("QSHIELD FINAL NOISE ROBUSTNESS PLOTS")
print("=" * 70)
print()

if not INPUT_FILE.exists():

    print("ERROR: Results CSV not found:")
    print(INPUT_FILE)
    raise SystemExit


df = pd.read_csv(INPUT_FILE)


if df.empty:

    print("ERROR: No evaluation rows found.")
    raise SystemExit


print(
    f"Evaluation rows             : {len(df)}"
)

print(
    f"Circuits represented        : "
    f"{df['circuit'].nunique()}"
)

print(
    f"Noise levels represented    : "
    f"{df['noise_rate'].nunique()}"
)

print()


# ============================================================
# CONVERT DATA TYPES
# ============================================================

df["noise_rate"] = pd.to_numeric(
    df["noise_rate"],
    errors="coerce",
)

df["prediction"] = pd.to_numeric(
    df["prediction"],
    errors="coerce",
)

df["risk_score"] = pd.to_numeric(
    df["risk_score"],
    errors="coerce",
)

df["observed_tvd"] = pd.to_numeric(
    df["observed_tvd"],
    errors="coerce",
)


# Remove rows where essential numeric values are unavailable

df = df.dropna(
    subset=[
        "noise_rate",
        "prediction",
        "risk_score",
        "observed_tvd",
    ]
).copy()


print(
    f"Valid evaluation rows       : {len(df)}"
)

print()


# ============================================================
# ATTACK TYPES
# ============================================================

# These names exactly match the calibrated CSV.

attack_types = [
    "Gate Insertion",
    "Gate Deletion",
    "Gate Substitution",
    "Multiple Gate Insertion",
]


attack_labels = {
    "Gate Insertion": "Gate Insertion",
    "Gate Deletion": "Gate Deletion",
    "Gate Substitution": "Gate Substitution",
    "Multiple Gate Insertion": "Multiple Gate Insertion",
}


NORMAL_LABEL = "Normal"


# ============================================================
# NOISE LEVELS
# ============================================================

noise_levels = sorted(
    df["noise_rate"]
    .dropna()
    .unique()
)


# ============================================================
# 1. ATTACK DETECTION RATE VS NOISE
# ============================================================

attack_df = df[
    df["attack_type"].isin(
        attack_types
    )
].copy()


detection_data = []


for noise in noise_levels:

    subset = attack_df[
        attack_df["noise_rate"] == noise
    ]

    for attack in attack_types:

        attack_subset = subset[
            subset["attack_type"] == attack
        ]

        if attack_subset.empty:
            continue

        detection_rate = (
            attack_subset["prediction"] == 1
        ).mean() * 100

        detection_data.append(
            {
                "noise_rate": noise,
                "attack_type": attack,
                "detection_rate": detection_rate,
            }
        )


detection_df = pd.DataFrame(
    detection_data,
    columns=[
        "noise_rate",
        "attack_type",
        "detection_rate",
    ],
)


plt.figure(
    figsize=(11, 7)
)

for attack in attack_types:

    subset = detection_df[
        detection_df["attack_type"] == attack
    ]

    if subset.empty:
        continue

    plt.plot(
        subset["noise_rate"],
        subset["detection_rate"],
        marker="o",
        linewidth=2,
        label=attack_labels[attack],
    )


plt.xlabel(
    "Noise Rate"
)

plt.ylabel(
    "Attack Detection Rate (%)"
)

plt.title(
    "QShield Attack Detection Under Increasing Noise"
)

plt.ylim(
    0,
    105,
)

plt.grid(
    True,
    alpha=0.3,
)

plt.legend()

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "noise_attack_detection.png",
    dpi=300,
)

plt.close()


# ============================================================
# 2. AVERAGE RISK SCORE VS NOISE
# ============================================================

risk_data = (
    df
    .groupby(
        [
            "noise_rate",
            "attack_type",
        ]
    )["risk_score"]
    .mean()
    .reset_index()
)


plt.figure(
    figsize=(11, 7)
)


for attack in [
    NORMAL_LABEL,
    *attack_types,
]:

    subset = risk_data[
        risk_data["attack_type"] == attack
    ]

    if subset.empty:
        continue

    label = (
        "Normal"
        if attack == NORMAL_LABEL
        else attack_labels[attack]
    )

    plt.plot(
        subset["noise_rate"],
        subset["risk_score"],
        marker="o",
        linewidth=2,
        label=label,
    )


plt.xlabel(
    "Noise Rate"
)

plt.ylabel(
    "Average Security Risk Score"
)

plt.title(
    "QShield Security Risk Score Under Increasing Noise"
)

plt.ylim(
    0,
    105,
)

plt.grid(
    True,
    alpha=0.3,
)

plt.legend()

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "noise_risk_score.png",
    dpi=300,
)

plt.close()


# ============================================================
# 3. AVERAGE TVD VS NOISE
# ============================================================

tvd_data = (
    df
    .groupby(
        [
            "noise_rate",
            "attack_type",
        ]
    )["observed_tvd"]
    .mean()
    .reset_index()
)


plt.figure(
    figsize=(11, 7)
)


for attack in [
    NORMAL_LABEL,
    *attack_types,
]:

    subset = tvd_data[
        tvd_data["attack_type"] == attack
    ]

    if subset.empty:
        continue

    label = (
        "Normal"
        if attack == NORMAL_LABEL
        else attack_labels[attack]
    )

    plt.plot(
        subset["noise_rate"],
        subset["observed_tvd"],
        marker="o",
        linewidth=2,
        label=label,
    )


plt.xlabel(
    "Noise Rate"
)

plt.ylabel(
    "Average Total Variation Distance (TVD)"
)

plt.title(
    "Behavioral Difference Under Increasing Noise"
)

plt.ylim(
    0,
    1.05,
)

plt.grid(
    True,
    alpha=0.3,
)

plt.legend()

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "noise_tvd.png",
    dpi=300,
)

plt.close()


# ============================================================
# 4. OVERALL ATTACK DETECTION BY ATTACK TYPE
# ============================================================

overall_detection = []


for attack in attack_types:

    subset = attack_df[
        attack_df["attack_type"] == attack
    ]

    if subset.empty:
        continue

    rate = (
        subset["prediction"] == 1
    ).mean() * 100

    overall_detection.append(
        {
            "attack_type": attack,
            "detection_rate": rate,
        }
    )


overall_df = pd.DataFrame(
    overall_detection
)


plt.figure(
    figsize=(10, 7)
)


if not overall_df.empty:

    labels = [
        attack_labels[a]
        for a in overall_df["attack_type"]
    ]

    values = overall_df[
        "detection_rate"
    ]

    plt.bar(
        labels,
        values,
    )

    plt.ylabel(
        "Detection Rate (%)"
    )

    plt.xlabel(
        "Attack Type"
    )

    plt.title(
        "QShield Overall Attack Detection Across Noise Levels"
    )

    plt.ylim(
        0,
        105,
    )

    plt.xticks(
        rotation=20,
        ha="right",
    )

    plt.grid(
        axis="y",
        alpha=0.3,
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR
        / "overall_attack_detection.png",
        dpi=300,
    )

plt.close()


# ============================================================
# 5. NORMAL FALSE POSITIVE RATE VS NOISE
# ============================================================

normal_df = df[
    df["attack_type"] == NORMAL_LABEL
].copy()


false_positive_data = []


for noise in noise_levels:

    subset = normal_df[
        normal_df["noise_rate"] == noise
    ]

    if subset.empty:
        continue

    false_positive_rate = (
        subset["prediction"] == 1
    ).mean() * 100

    false_positive_data.append(
        {
            "noise_rate": noise,
            "false_positive_rate":
                false_positive_rate,
        }
    )


false_positive_df = pd.DataFrame(
    false_positive_data
)


plt.figure(
    figsize=(10, 7)
)


if not false_positive_df.empty:

    plt.plot(
        false_positive_df["noise_rate"],
        false_positive_df["false_positive_rate"],
        marker="o",
        linewidth=2,
    )

    plt.xlabel(
        "Noise Rate"
    )

    plt.ylabel(
        "False Positive Rate (%)"
    )

    plt.title(
        "QShield False Positive Rate for Normal Circuits"
    )

    plt.ylim(
        0,
        105,
    )

    plt.grid(
        True,
        alpha=0.3,
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR
        / "noise_false_positive_rate.png",
        dpi=300,
    )

plt.close()


# ============================================================
# SAVE SUMMARY CSV
# ============================================================

summary_file = (
    PROJECT_ROOT
    / "experiments"
    / "noise_robustness_summary.csv"
)


summary_rows = []


for noise in noise_levels:

    noise_subset = df[
        df["noise_rate"] == noise
    ]

    for attack in [
        NORMAL_LABEL,
        *attack_types,
    ]:

        subset = noise_subset[
            noise_subset["attack_type"] == attack
        ]

        if subset.empty:
            continue

        detection = (
            (subset["prediction"] == 1).mean()
            * 100
        )

        avg_risk = (
            subset["risk_score"].mean()
        )

        avg_tvd = (
            subset["observed_tvd"].mean()
        )

        summary_rows.append(
            {
                "noise_rate": noise,
                "attack_type": attack,
                "detection_rate": round(
                    detection,
                    2,
                ),
                "average_risk_score": round(
                    avg_risk,
                    2,
                ),
                "average_tvd": round(
                    avg_tvd,
                    4,
                ),
                "samples": len(subset),
            }
        )


summary_df = pd.DataFrame(
    summary_rows
)


summary_df.to_csv(
    summary_file,
    index=False,
)


# ============================================================
# COMPLETE
# ============================================================

print(
    "Generated plots:"
)

print()

print(
    "1. noise_attack_detection.png"
)

print(
    "2. noise_risk_score.png"
)

print(
    "3. noise_tvd.png"
)

print(
    "4. overall_attack_detection.png"
)

print(
    "5. noise_false_positive_rate.png"
)

print()

print(
    "Summary CSV:"
)

print(
    summary_file
)

print()

print(
    "Saved to:"
)

print(
    OUTPUT_DIR
)

print()

print("=" * 70)
print("PLOTTING COMPLETE")
print("=" * 70)
print()