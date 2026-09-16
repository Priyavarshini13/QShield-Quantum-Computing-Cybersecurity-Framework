import os

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

RESULTS_FILE = os.path.join(
    PROJECT_ROOT,
    "experiments",
    "bb84_noise_evaluation_results.csv"
)

PLOTS_DIR = os.path.join(
    PROJECT_ROOT,
    "experiments",
    "plots"
)

os.makedirs(
    PLOTS_DIR,
    exist_ok=True
)


# ============================================================
# LOAD RESULTS
# ============================================================

df = pd.read_csv(
    RESULTS_FILE
)


# ============================================================
# CONVERT VALUES
# ============================================================

df["noise_percent"] = (
    df["noise_rate"] * 100
)

df["qber_percent"] = (
    df["average_qber"] * 100
)

df["detection_percent"] = (
    df["detection_rate"] * 100
)


# ============================================================
# SELECT SCENARIOS
# ============================================================

noise_only = df[
    df["scenario"] == "noise"
].copy()

noise_plus_eve = df[
    df["scenario"] == "noise_plus_eve"
].copy()


# Sort by noise level

noise_only = noise_only.sort_values(
    "noise_rate"
)

noise_plus_eve = noise_plus_eve.sort_values(
    "noise_rate"
)


# ============================================================
# PRINT DATA
# ============================================================

print("=" * 70)
print("QSHIELD - BB84 NOISE VS EAVESDROPPING")
print("=" * 70)

print("\nNoise-only results:")

for _, row in noise_only.iterrows():

    print(
        f"Noise: "
        f"{row['noise_percent']:.0f}% "
        f"| QBER: "
        f"{row['qber_percent']:.2f}% "
        f"| Detection: "
        f"{row['detection_percent']:.2f}%"
    )


print("\nNoise + Eve results:")

for _, row in noise_plus_eve.iterrows():

    print(
        f"Noise: "
        f"{row['noise_percent']:.0f}% "
        f"| QBER: "
        f"{row['qber_percent']:.2f}% "
        f"| Detection: "
        f"{row['detection_percent']:.2f}%"
    )


# ============================================================
# QBER COMPARISON GRAPH
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.plot(
    noise_only["noise_percent"],
    noise_only["qber_percent"],
    marker="o",
    linewidth=2,
    label="Noise Only"
)

plt.plot(
    noise_plus_eve["noise_percent"],
    noise_plus_eve["qber_percent"],
    marker="o",
    linewidth=2,
    label="Noise + Intercept-Resend"
)

plt.axhline(
    11,
    linestyle="--",
    linewidth=2,
    label="11% Security Threshold"
)

plt.xlabel(
    "Channel Noise Level (%)"
)

plt.ylabel(
    "Average QBER (%)"
)

plt.title(
    "BB84: QBER Under Channel Noise and Eavesdropping"
)

plt.xticks(
    [0, 2, 5, 10, 15]
)

plt.grid(
    alpha=0.3
)

plt.legend()

plt.tight_layout()


# ============================================================
# SAVE QBER GRAPH
# ============================================================

qber_plot = os.path.join(
    PLOTS_DIR,
    "bb84_noise_vs_eve_qber.png"
)

plt.savefig(
    qber_plot,
    dpi=300,
    bbox_inches="tight"
)

plt.show()


print(
    f"\nQBER graph saved to:\n{qber_plot}"
)


# ============================================================
# DETECTION RATE GRAPH
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.plot(
    noise_only["noise_percent"],
    noise_only["detection_percent"],
    marker="o",
    linewidth=2,
    label="Noise Only"
)

plt.plot(
    noise_plus_eve["noise_percent"],
    noise_plus_eve["detection_percent"],
    marker="o",
    linewidth=2,
    label="Noise + Intercept-Resend"
)

plt.xlabel(
    "Channel Noise Level (%)"
)

plt.ylabel(
    "Detection Rate (%)"
)

plt.title(
    "BB84: Security Detection Rate"
)

plt.xticks(
    [0, 2, 5, 10, 15]
)

plt.ylim(
    0,
    100
)

plt.grid(
    alpha=0.3
)

plt.legend()

plt.tight_layout()


# ============================================================
# SAVE DETECTION GRAPH
# ============================================================

detection_plot = os.path.join(
    PLOTS_DIR,
    "bb84_noise_vs_eve_detection.png"
)

plt.savefig(
    detection_plot,
    dpi=300,
    bbox_inches="tight"
)

plt.show()


print(
    f"Detection graph saved to:\n{detection_plot}"
)


# ============================================================
# FINAL INTERPRETATION
# ============================================================

print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)

print(
    "\nThe noise-only condition produces a gradual increase "
    "in QBER as channel noise increases."
)

print(
    "The intercept-resend condition produces substantially "
    "higher QBER across the tested noise levels."
)

print(
    "This demonstrates that QBER can provide a useful "
    "security signal for distinguishing channel disturbance "
    "from eavesdropping in this simulated experiment."
)

print(
    "\nBB84 noise analysis complete."
)