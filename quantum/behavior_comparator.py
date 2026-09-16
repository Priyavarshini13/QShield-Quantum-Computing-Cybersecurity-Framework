from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


def create_normal_circuit():
    """Create the expected quantum circuit."""

    qc = QuantumCircuit(2, 2)

    qc.h(0)
    qc.cx(0, 1)

    qc.measure([0, 1], [0, 1])

    return qc


def create_modified_circuit():
    """Create a modified quantum circuit."""

    qc = QuantumCircuit(2, 2)

    qc.h(0)
    qc.cx(0, 1)

    # Intentional mutation
    qc.x(0)

    qc.measure([0, 1], [0, 1])

    return qc


def run_circuit(circuit, shots=1000):
    """Run a circuit using the local simulator."""

    simulator = AerSimulator()

    result = simulator.run(
        circuit,
        shots=shots
    ).result()

    return result.get_counts()


def counts_to_distribution(counts, shots):
    """Convert measurement counts into probabilities."""

    return {
        state: count / shots
        for state, count in counts.items()
    }


def calculate_tvd(normal_counts, modified_counts, shots):
    """
    Calculate Total Variation Distance (TVD)
    between two quantum measurement distributions.
    """

    normal_distribution = counts_to_distribution(
        normal_counts,
        shots
    )

    modified_distribution = counts_to_distribution(
        modified_counts,
        shots
    )

    all_states = set(normal_distribution) | set(modified_distribution)

    total_difference = 0

    for state in all_states:

        normal_probability = normal_distribution.get(
            state,
            0
        )

        modified_probability = modified_distribution.get(
            state,
            0
        )

        total_difference += abs(
            normal_probability - modified_probability
        )

    # TVD = 1/2 × sum of absolute differences
    tvd = total_difference / 2

    return tvd


if __name__ == "__main__":

    SHOTS = 1000

    normal_circuit = create_normal_circuit()
    modified_circuit = create_modified_circuit()

    normal_counts = run_circuit(
        normal_circuit,
        SHOTS
    )

    modified_counts = run_circuit(
        modified_circuit,
        SHOTS
    )

    tvd = calculate_tvd(
        normal_counts,
        modified_counts,
        SHOTS
    )

    print("=== QShield Quantum Behavior Comparator ===")

    print("\nNormal Circuit Results:")
    print(normal_counts)

    print("\nModified Circuit Results:")
    print(modified_counts)

    print("\nTotal Variation Distance:")
    print(f"{tvd:.4f}")

    print("\nAnomaly Interpretation:")

    if tvd < 0.1:
        print("LOW — Behavior is very similar")

    elif tvd < 0.3:
        print("MEDIUM — Noticeable behavioral difference")

    else:
        print("HIGH — Significant behavioral difference")