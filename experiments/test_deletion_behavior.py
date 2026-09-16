import glob
import os
import sys

sys.path.append(".")

from qiskit_aer import AerSimulator

from quantum.qasm_loader import load_qasm_circuit
from quantum.behavior_comparator import calculate_tvd
from security.attack_generator import gate_deletion


# ============================================================
# CONFIGURATION
# ============================================================

QASMBENCH_SMALL = (
    r"C:\Users\priya\Downloads\C-DAC IISc NQM Internship"
    r"\QASMBench-master\QASMBench-master\small"
)

SHOTS = 500
MAX_CIRCUITS = 20


# ============================================================
# FIND BENCHMARKS
# ============================================================

pattern = os.path.join(
    QASMBENCH_SMALL,
    "*",
    "*.qasm",
)

files = [
    f
    for f in glob.glob(pattern)
    if "_transpiled" not in os.path.basename(f)
]

files.sort()


print("Starting deletion behavior test...")
print(
    "Found non-transpiled circuits:",
    len(files),
)
print()


# ============================================================
# SIMULATOR
# ============================================================

simulator = AerSimulator()

tested = 0
skipped = 0
tvds = []


# ============================================================
# TEST
# ============================================================

for file_path in files:

    if tested >= MAX_CIRCUITS:
        break

    try:

        circuit = load_qasm_circuit(
            file_path
        )

        deleted = gate_deletion(
            circuit
        )

        original_counts = (
            simulator
            .run(
                circuit,
                shots=SHOTS,
            )
            .result()
            .get_counts()
        )

        deleted_counts = (
            simulator
            .run(
                deleted,
                shots=SHOTS,
            )
            .result()
            .get_counts()
        )

        tvd = calculate_tvd(
            original_counts,
            deleted_counts,
            SHOTS,
        )

        tvds.append(tvd)

        print(
            f"{os.path.basename(file_path):35s}"
            f" TVD = {tvd:.4f}"
        )

        tested += 1

    except Exception as e:

        skipped += 1

        print(
            f"{os.path.basename(file_path):35s}"
            f" SKIPPED - {e}"
        )


# ============================================================
# RESULTS
# ============================================================

print()
print("=" * 65)
print("DELETION BEHAVIOR TEST")
print("=" * 65)

print(
    "Circuits attempted:",
    min(len(files), MAX_CIRCUITS),
)

print(
    "Circuits tested:",
    tested,
)

print(
    "Circuits skipped:",
    skipped,
)


if tvds:

    mean_tvd = (
        sum(tvds) / len(tvds)
    )

    print(
        f"Mean TVD:    {mean_tvd:.4f}"
    )

    print(
        f"Minimum TVD: {min(tvds):.4f}"
    )

    print(
        f"Maximum TVD: {max(tvds):.4f}"
    )

    print()

    strong = sum(
        tvd >= 0.10
        for tvd in tvds
    )

    print(
        f"TVD >= 0.10: "
        f"{strong}/{len(tvds)}"
    )

else:

    print()
    print(
        "No circuits could be evaluated."
    )


print()
print("Test complete.")