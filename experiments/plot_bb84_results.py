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
    "bb84_evaluation_results.csv"
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
# LOAD DATA
# ============================================================

df = pd.read_csv(
    RESULTS_FILE
)


# ============================================================
# CONVERT QBER TO PERCENTAGE
# ============================================================

df["qber_percent"] = (
    df["qber"] * 100
)


# ============================================================
# GROUP DATA
# ============================================================

normal = df[
    df["scenario"] == "normal"
]["qber_percent"]

eve = df[
    df["scenario"] == "intercept_resend"
]["qber_percent"]


# ============================================================
# PRINT STATISTICS
# ============================================================

print("=" * 60)
print("QSHIELD - BB84 QBER VISUALIZATION")
print("=" * 60)

print(
    f"\nNormal average QBER: "
    f"{normal.mean():.2f}%"
)

print(
    f"Intercept-resend average QBER: "
    f"{eve.mean():.2f}%"
)

print(
    f"BB84 security threshold: 11.00%"
)


# ============================================================
# HISTOGRAM
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.hist(
    normal,
    bins=20,
    alpha=0.7,
    label="Normal Channel"
)

plt.hist(
    eve,
    bins=20,
    alpha=0.7,
    label="Intercept-Resend Attack"
)

plt.axvline(
    11,
    linestyle="--",
    linewidth=2,
    label="11% Security Threshold"
)

plt.xlabel(
    "QBER (%)"
)

plt.ylabel(
    "Number of Trials"
)

plt.title(
    "BB84 QBER Distribution"
)

plt.legend()

plt.tight_layout()


# ============================================================
# SAVE
# ============================================================

output_file = os.path.join(
    PLOTS_DIR,
    "bb84_qber_distribution.png"
)

plt.savefig(
    output_file,
    dpi=300
)

plt.show()


print(
    f"\nPlot saved to:\n{output_file}"
)

print(
    "\nBB84 visualization complete."
)