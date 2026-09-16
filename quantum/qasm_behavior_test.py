import os
import sys

from qiskit_aer import AerSimulator


# Allow imports from the QShield project root
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.append(PROJECT_ROOT)


from quantum.qasm_loader import load_qasm_circuit

from security.attack_generator import (
    gate_insertion,
    gate_deletion,
    gate_substitution
)


SHOTS = 1000


def run_circuit(circuit):
    """Run a quantum circuit using AerSimulator."""

    simulator = AerSimulator()

    result = simulator.run(
        circuit,
        shots=SHOTS
    ).result()

    return result.get_counts()


def normalize_counts(counts):
    """
    Normalize Qiskit measurement keys.

    Qiskit can return multi-register results
    with spaces between classical registers.

    Example:
        '1 1 1 0' -> '1110'
    """

    normalized = {}

    for state, count in counts.items():

        clean_state = state.replace(" ", "")

        normalized[clean_state] = (
            normalized.get(clean_state, 0) + count
        )

    return normalized


def calculate_tvd(reference_counts, observed_counts):
    """
    Calculate Total Variation Distance.

    TVD range:
        0.0 = identical distributions
        1.0 = completely different distributions
    """

    reference_counts = normalize_counts(
        reference_counts
    )

    observed_counts = normalize_counts(
        observed_counts
    )

    reference_distribution = {
        state: count / SHOTS
        for state, count in reference_counts.items()
    }

    observed_distribution = {
        state: count / SHOTS
        for state, count in observed_counts.items()
    }

    all_states = (
        set(reference_distribution)
        | set(observed_distribution)
    )

    total_difference = 0.0

    for state in all_states:

        reference_probability = (
            reference_distribution.get(state, 0)
        )

        observed_probability = (
            observed_distribution.get(state, 0)
        )

        total_difference += abs(
            reference_probability
            - observed_probability
        )

    tvd = total_difference / 2

    return tvd


def classify_anomaly(tvd):
    """Convert TVD into an anomaly level."""

    if tvd < 0.1:
        return "LOW"

    elif tvd < 0.3:
        return "MEDIUM"

    else:
        return "HIGH"


if __name__ == "__main__":

    # Real QASMBench circuit
    file_path = os.path.join(
        PROJECT_ROOT,
        "data",
        "benchmarks",
        "bell_n4.qasm"
    )

    # Load benchmark circuit
    original = load_qasm_circuit(
        file_path
    )

    # Generate mutations
    inserted = gate_insertion(
        original
    )

    deleted = gate_deletion(
        original
    )

    substituted = gate_substitution(
        original
    )

    print(
        "=== QShield QASMBench Behavior Analysis ==="
    )

    # ------------------------------------------------
    # ORIGINAL CIRCUIT
    # ------------------------------------------------

    print(
        "\nRunning original circuit..."
    )

    original_counts = run_circuit(
        original
    )

    print(
        "Original Results:"
    )

    print(original_counts)

    # ------------------------------------------------
    # MUTATIONS
    # ------------------------------------------------

    mutations = {
        "Gate Insertion": inserted,
        "Gate Deletion": deleted,
        "Gate Substitution": substituted
    }

    for name, mutated_circuit in mutations.items():

        print(
            f"\n--- {name} ---"
        )

        mutated_counts = run_circuit(
            mutated_circuit
        )

        print(
            "Mutated Results:"
        )

        print(mutated_counts)

        tvd = calculate_tvd(
            original_counts,
            mutated_counts
        )

        anomaly_level = classify_anomaly(
            tvd
        )

        print(
            f"TVD: {tvd:.4f}"
        )

        print(
            f"Anomaly Level: {anomaly_level}"
        )