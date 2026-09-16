import os
import sys
import statistics
import csv

# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)


# ============================================================
# IMPORT BB84
# ============================================================

from cryptography.bb84 import (
    generate_bits,
    generate_bases,
    prepare_qubits,
    measure_qubits,
    intercept_resend_attack,
    sift_key,
    calculate_qber
)


# ============================================================
# EXPERIMENT PARAMETERS
# ============================================================

NUM_TRIALS = 1000
QUBITS_PER_TRIAL = 32

OUTPUT_FILE = os.path.join(
    os.path.dirname(
        os.path.abspath(__file__)
    ),
    "bb84_evaluation_results.csv"
)


# ============================================================
# NORMAL BB84 TRIAL
# ============================================================

def run_normal_trial(length):
    """
    Run one BB84 trial without Eve.
    """

    # --------------------------------------------------------
    # Alice
    # --------------------------------------------------------

    alice_bits = generate_bits(length)
    alice_bases = generate_bases(length)

    states = prepare_qubits(
        alice_bits,
        alice_bases
    )

    # --------------------------------------------------------
    # Bob
    # --------------------------------------------------------

    bob_bases = generate_bases(length)

    bob_bits = measure_qubits(
        states,
        bob_bases
    )

    # --------------------------------------------------------
    # Sifting
    # --------------------------------------------------------

    (
        alice_key,
        bob_key,
        matching_positions
    ) = sift_key(
        alice_bits,
        alice_bases,
        bob_bits,
        bob_bases
    )

    # --------------------------------------------------------
    # QBER
    # --------------------------------------------------------

    qber = calculate_qber(
        alice_key,
        bob_key
    )

    return {
        "qber": qber,
        "key_length": len(alice_key),
        "detected": qber >= 0.11
    }


# ============================================================
# EVE BB84 TRIAL
# ============================================================

def run_eve_trial(length):
    """
    Run one BB84 trial with Eve performing
    an intercept-resend attack.
    """

    # --------------------------------------------------------
    # Alice
    # --------------------------------------------------------

    alice_bits = generate_bits(length)
    alice_bases = generate_bases(length)

    states = prepare_qubits(
        alice_bits,
        alice_bases
    )

    # --------------------------------------------------------
    # Eve
    # --------------------------------------------------------

    eve_bases = generate_bases(length)

    (
        eve_bits,
        resent_states
    ) = intercept_resend_attack(
        states,
        eve_bases
    )

    # --------------------------------------------------------
    # Bob
    # --------------------------------------------------------

    bob_bases = generate_bases(length)

    bob_bits = measure_qubits(
        resent_states,
        bob_bases
    )

    # --------------------------------------------------------
    # Sifting
    # --------------------------------------------------------

    (
        alice_key,
        bob_key,
        matching_positions
    ) = sift_key(
        alice_bits,
        alice_bases,
        bob_bits,
        bob_bases
    )

    # --------------------------------------------------------
    # QBER
    # --------------------------------------------------------

    qber = calculate_qber(
        alice_key,
        bob_key
    )

    return {
        "qber": qber,
        "key_length": len(alice_key),
        "detected": qber >= 0.11
    }


# ============================================================
# RUN EXPERIMENT
# ============================================================

def run_evaluation():

    print("=" * 70)
    print("QSHIELD - BB84 STATISTICAL SECURITY EVALUATION")
    print("=" * 70)

    print("\nExperiment parameters:")
    print(f"Trials: {NUM_TRIALS}")
    print(f"Qubits per trial: {QUBITS_PER_TRIAL}")

    print("\nRunning normal BB84 trials...")

    normal_results = []

    for trial in range(NUM_TRIALS):

        result = run_normal_trial(
            QUBITS_PER_TRIAL
        )

        normal_results.append(result)

        if (trial + 1) % 100 == 0:
            print(
                f"Normal trials completed: "
                f"{trial + 1}/{NUM_TRIALS}"
            )

    print("\nRunning intercept-resend attack trials...")

    eve_results = []

    for trial in range(NUM_TRIALS):

        result = run_eve_trial(
            QUBITS_PER_TRIAL
        )

        eve_results.append(result)

        if (trial + 1) % 100 == 0:
            print(
                f"Eve trials completed: "
                f"{trial + 1}/{NUM_TRIALS}"
            )

    # ========================================================
    # NORMAL STATISTICS
    # ========================================================

    normal_qbers = [
        result["qber"]
        for result in normal_results
    ]

    normal_key_lengths = [
        result["key_length"]
        for result in normal_results
    ]

    normal_average_qber = statistics.mean(
        normal_qbers
    )

    normal_std_qber = statistics.stdev(
        normal_qbers
    )

    normal_false_positives = sum(
        result["detected"]
        for result in normal_results
    )

    normal_false_positive_rate = (
        normal_false_positives /
        NUM_TRIALS
    )

    # ========================================================
    # EVE STATISTICS
    # ========================================================

    eve_qbers = [
        result["qber"]
        for result in eve_results
    ]

    eve_key_lengths = [
        result["key_length"]
        for result in eve_results
    ]

    eve_average_qber = statistics.mean(
        eve_qbers
    )

    eve_std_qber = statistics.stdev(
        eve_qbers
    )

    eve_detected = sum(
        result["detected"]
        for result in eve_results
    )

    eve_detection_rate = (
        eve_detected /
        NUM_TRIALS
    )

    # ========================================================
    # PRINT RESULTS
    # ========================================================

    print("\n" + "=" * 70)
    print("BB84 EVALUATION RESULTS")
    print("=" * 70)

    print("\nNORMAL CHANNEL")
    print("-" * 70)

    print(
        f"Average QBER: "
        f"{normal_average_qber * 100:.2f}%"
    )

    print(
        f"QBER standard deviation: "
        f"{normal_std_qber * 100:.2f}%"
    )

    print(
        f"Average sifted key length: "
        f"{statistics.mean(normal_key_lengths):.2f} bits"
    )

    print(
        f"False positives: "
        f"{normal_false_positives}/{NUM_TRIALS}"
    )

    print(
        f"False-positive rate: "
        f"{normal_false_positive_rate * 100:.2f}%"
    )

    print("\nINTERCEPT-RESEND ATTACK")
    print("-" * 70)

    print(
        f"Average QBER: "
        f"{eve_average_qber * 100:.2f}%"
    )

    print(
        f"QBER standard deviation: "
        f"{eve_std_qber * 100:.2f}%"
    )

    print(
        f"Average sifted key length: "
        f"{statistics.mean(eve_key_lengths):.2f} bits"
    )

    print(
        f"Detected attacks: "
        f"{eve_detected}/{NUM_TRIALS}"
    )

    print(
        f"Attack detection rate: "
        f"{eve_detection_rate * 100:.2f}%"
    )

    # ========================================================
    # COMPARISON
    # ========================================================

    qber_increase = (
        eve_average_qber -
        normal_average_qber
    )

    print("\n" + "=" * 70)
    print("SECURITY COMPARISON")
    print("=" * 70)

    print(
        f"\nNormal average QBER: "
        f"{normal_average_qber * 100:.2f}%"
    )

    print(
        f"Eve average QBER: "
        f"{eve_average_qber * 100:.2f}%"
    )

    print(
        f"QBER increase: "
        f"{qber_increase * 100:.2f} percentage points"
    )

    print(
        "\nBB84 security threshold: 11%"
    )

    if eve_average_qber >= 0.11:

        print(
            "\nRESULT: "
            "Intercept-resend attack produces "
            "a detectable increase in QBER."
        )

    else:

        print(
            "\nRESULT: "
            "Average QBER remained below "
            "the detection threshold."
        )

    # ========================================================
    # SAVE CSV
    # ========================================================

    with open(
        OUTPUT_FILE,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "trial",
            "scenario",
            "qber",
            "key_length",
            "detected"
        ])

        for i, result in enumerate(
            normal_results,
            start=1
        ):

            writer.writerow([
                i,
                "normal",
                result["qber"],
                result["key_length"],
                result["detected"]
            ])

        for i, result in enumerate(
            eve_results,
            start=1
        ):

            writer.writerow([
                i,
                "intercept_resend",
                result["qber"],
                result["key_length"],
                result["detected"]
            ])

    print("\nResults saved to:")

    print(
        OUTPUT_FILE
    )

    print("\n" + "=" * 70)
    print("BB84 STATISTICAL EVALUATION COMPLETE")
    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    run_evaluation()