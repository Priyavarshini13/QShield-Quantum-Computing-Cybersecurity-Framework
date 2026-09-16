import os
import sys
import csv
import statistics


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
# BB84 IMPORTS
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

NUM_TRIALS = 500

QUBITS_PER_TRIAL = 32

NOISE_LEVELS = [
    0.00,
    0.02,
    0.05,
    0.10,
    0.15
]

QBER_THRESHOLD = 0.11

OUTPUT_FILE = os.path.join(
    os.path.dirname(
        os.path.abspath(__file__)
    ),
    "bb84_noise_evaluation_results.csv"
)


# ============================================================
# CHANNEL NOISE
# ============================================================

def apply_channel_noise(
    states,
    noise_rate
):
    """
    Apply a simple Pauli-channel noise model
    to the BB84 states.

    With probability = noise_rate,
    a random Pauli X, Y, or Z operation
    is applied.

    State representation:

        |0>
        |1>
        |+>
        |->

    X:
        |0> <-> |1>
        |+> -> |+>
        |-> -> |->

    Z:
        |0> -> |0>
        |1> -> |1>
        |+> <-> |->
        
    Y:
        |0> <-> |1>
        |+> <-> |->
        
    Global phase is ignored because it does not
    affect measurement probabilities.
    """

    noisy_states = []

    for state in states:

        # No noise on this qubit
        if random_value() > noise_rate:

            noisy_states.append(state)
            continue

        # Random Pauli error
        error = random_choice(
            ["X", "Y", "Z"]
        )

        # ----------------------------------------------------
        # X ERROR
        # ----------------------------------------------------

        if error == "X":

            if state == "|0>":
                noisy_state = "|1>"

            elif state == "|1>":
                noisy_state = "|0>"

            else:
                # X does not change measurement result
                # in the Hadamard basis
                noisy_state = state

        # ----------------------------------------------------
        # Z ERROR
        # ----------------------------------------------------

        elif error == "Z":

            if state == "|+>":
                noisy_state = "|->"

            elif state == "|->":
                noisy_state = "|+>"

            else:
                noisy_state = state

        # ----------------------------------------------------
        # Y ERROR
        # ----------------------------------------------------

        else:

            if state == "|0>":
                noisy_state = "|1>"

            elif state == "|1>":
                noisy_state = "|0>"

            elif state == "|+>":
                noisy_state = "|->"

            else:
                noisy_state = "|+>"

        noisy_states.append(
            noisy_state
        )

    return noisy_states


# ============================================================
# RANDOM HELPERS
# ============================================================

def random_value():
    """
    Generate a random floating-point value.
    """

    import random

    return random.random()


def random_choice(values):
    """
    Select a random element.
    """

    import random

    return random.choice(values)


# ============================================================
# SINGLE BB84 TRIAL
# ============================================================

def run_trial(
    length,
    noise_rate,
    use_eve
):
    """
    Run one BB84 experiment.

    Parameters:

        length:
            Number of transmitted qubits.

        noise_rate:
            Channel noise probability.

        use_eve:
            Whether Eve performs
            intercept-resend.
    """

    # ========================================================
    # ALICE
    # ========================================================

    alice_bits = generate_bits(
        length
    )

    alice_bases = generate_bases(
        length
    )

    states = prepare_qubits(
        alice_bits,
        alice_bases
    )

    # ========================================================
    # EVE
    # ========================================================

    if use_eve:

        eve_bases = generate_bases(
            length
        )

        (
            eve_bits,
            states
        ) = intercept_resend_attack(
            states,
            eve_bases
        )

    # ========================================================
    # CHANNEL NOISE
    # ========================================================

    if noise_rate > 0:

        states = apply_channel_noise(
            states,
            noise_rate
        )

    # ========================================================
    # BOB
    # ========================================================

    bob_bases = generate_bases(
        length
    )

    bob_bits = measure_qubits(
        states,
        bob_bases
    )

    # ========================================================
    # KEY SIFTING
    # ========================================================

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

    # ========================================================
    # QBER
    # ========================================================

    qber = calculate_qber(
        alice_key,
        bob_key
    )

    detected = (
        qber >= QBER_THRESHOLD
    )

    return {
        "qber": qber,
        "key_length": len(alice_key),
        "detected": detected
    }


# ============================================================
# RUN SCENARIO
# ============================================================

def evaluate_scenario(
    scenario,
    noise_rate
):
    """
    Run multiple trials for one scenario.
    """

    if scenario == "normal":

        use_eve = False

        effective_noise = 0.0

    elif scenario == "noise":

        use_eve = False

        effective_noise = noise_rate

    elif scenario == "eve":

        use_eve = True

        effective_noise = 0.0

    elif scenario == "noise_plus_eve":

        use_eve = True

        effective_noise = noise_rate

    else:

        raise ValueError(
            f"Unknown scenario: {scenario}"
        )

    results = []

    for _ in range(NUM_TRIALS):

        result = run_trial(
            length=QUBITS_PER_TRIAL,
            noise_rate=effective_noise,
            use_eve=use_eve
        )

        results.append(
            result
        )

    return results


# ============================================================
# STATISTICS
# ============================================================

def calculate_statistics(
    results
):
    """
    Calculate average QBER,
    standard deviation,
    detection rate,
    and average key length.
    """

    qbers = [
        result["qber"]
        for result in results
    ]

    key_lengths = [
        result["key_length"]
        for result in results
    ]

    detections = [
        result["detected"]
        for result in results
    ]

    average_qber = statistics.mean(
        qbers
    )

    if len(qbers) > 1:

        qber_std = statistics.stdev(
            qbers
        )

    else:

        qber_std = 0.0

    detection_rate = (
        sum(detections)
        /
        len(detections)
    )

    average_key_length = (
        statistics.mean(
            key_lengths
        )
    )

    return {
        "average_qber": average_qber,
        "qber_std": qber_std,
        "detection_rate": detection_rate,
        "average_key_length": average_key_length
    }


# ============================================================
# MAIN EVALUATION
# ============================================================

def run_evaluation():

    print("=" * 70)
    print("QSHIELD - BB84 NOISE AND EAVESDROPPING EVALUATION")
    print("=" * 70)

    print("\nExperiment parameters:")
    print(f"Trials per scenario: {NUM_TRIALS}")
    print(
        f"Qubits per trial: {QUBITS_PER_TRIAL}"
    )

    print(
        f"QBER security threshold: "
        f"{QBER_THRESHOLD * 100:.0f}%"
    )

    print(
        "\nNoise levels:"
    )

    for noise in NOISE_LEVELS:

        print(
            f"  {noise * 100:.0f}%"
        )

    scenarios = [
        "normal",
        "noise",
        "eve",
        "noise_plus_eve"
    ]

    all_results = []

    # ========================================================
    # RUN EXPERIMENTS
    # ========================================================

    for noise_rate in NOISE_LEVELS:

        print("\n" + "=" * 70)

        print(
            f"NOISE LEVEL: "
            f"{noise_rate * 100:.0f}%"
        )

        print("=" * 70)

        for scenario in scenarios:

            # Normal and Eve-only should only be
            # evaluated once at zero noise.
            if scenario in [
                "normal",
                "eve"
            ] and noise_rate != 0.0:

                continue

            print(
                f"\nRunning scenario: "
                f"{scenario}"
            )

            results = evaluate_scenario(
                scenario,
                noise_rate
            )

            stats = calculate_statistics(
                results
            )

            # ------------------------------------------------
            # Print
            # ------------------------------------------------

            print(
                f"Average QBER: "
                f"{stats['average_qber'] * 100:.2f}%"
            )

            print(
                f"QBER Std. Dev.: "
                f"{stats['qber_std'] * 100:.2f}%"
            )

            print(
                f"Average sifted key: "
                f"{stats['average_key_length']:.2f} bits"
            )

            print(
                f"Detection rate: "
                f"{stats['detection_rate'] * 100:.2f}%"
            )

            # ------------------------------------------------
            # Save summary
            # ------------------------------------------------

            all_results.append({
                "scenario": scenario,
                "noise_rate": noise_rate,
                "average_qber": stats[
                    "average_qber"
                ],
                "qber_std": stats[
                    "qber_std"
                ],
                "average_key_length": stats[
                    "average_key_length"
                ],
                "detection_rate": stats[
                    "detection_rate"
                ]
            })

    # ========================================================
    # SECURITY INTERPRETATION
    # ========================================================

    print("\n" + "=" * 70)
    print("SECURITY ANALYSIS")
    print("=" * 70)

    for result in all_results:

        scenario = result[
            "scenario"
        ]

        noise = result[
            "noise_rate"
        ]

        qber = result[
            "average_qber"
        ]

        detection = result[
            "detection_rate"
        ]

        print(
            f"\n{scenario.upper()} "
            f"| Noise = {noise * 100:.0f}%"
        )

        print(
            f"Average QBER: "
            f"{qber * 100:.2f}%"
        )

        print(
            f"Detection rate: "
            f"{detection * 100:.2f}%"
        )

        if qber >= QBER_THRESHOLD:

            print(
                "Assessment: "
                "HIGH QBER / POTENTIAL SECURITY RISK"
            )

        else:

            print(
                "Assessment: "
                "QBER BELOW THRESHOLD"
            )

    # ========================================================
    # SAVE CSV
    # ========================================================

    with open(
        OUTPUT_FILE,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(
            file
        )

        writer.writerow([
            "scenario",
            "noise_rate",
            "average_qber",
            "qber_std",
            "average_key_length",
            "detection_rate"
        ])

        for result in all_results:

            writer.writerow([
                result["scenario"],
                result["noise_rate"],
                result["average_qber"],
                result["qber_std"],
                result["average_key_length"],
                result["detection_rate"]
            ])

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)

    for result in all_results:

        print(
            f"\n"
            f"{result['scenario']:18s} "
            f"| Noise "
            f"{result['noise_rate'] * 100:5.1f}% "
            f"| QBER "
            f"{result['average_qber'] * 100:6.2f}% "
            f"| Detection "
            f"{result['detection_rate'] * 100:6.2f}%"
        )

    print("\nResults saved to:")

    print(
        OUTPUT_FILE
    )

    print(
        "\nBB84 noise and eavesdropping "
        "evaluation complete."
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    run_evaluation()