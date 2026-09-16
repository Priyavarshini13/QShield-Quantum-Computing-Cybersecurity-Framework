import sys

# ============================================================
# WINDOWS UTF-8 FIX
# ============================================================

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


# ============================================================
# QSHIELD - GROVER'S SEARCH ALGORITHM
# ============================================================

def create_grover_circuit(target_state="11"):
    """
    Create a 2-qubit Grover search circuit.

    target_state:
        "00", "01", "10", or "11"
    """

    if not isinstance(target_state, str):
        raise ValueError(
            "Target state must be a string."
        )

    if len(target_state) != 2:
        raise ValueError(
            "Target state must contain exactly 2 bits."
        )

    if any(bit not in "01" for bit in target_state):
        raise ValueError(
            "Target state must contain only 0 and 1."
        )

    # --------------------------------------------------------
    # Create circuit
    # --------------------------------------------------------

    qc = QuantumCircuit(2, 2)

    # --------------------------------------------------------
    # Superposition
    # --------------------------------------------------------

    qc.h(0)
    qc.h(1)

    # --------------------------------------------------------
    # Oracle
    #
    # Qiskit uses little-endian ordering for measurement
    # strings. Therefore target_state[1] corresponds to q0
    # and target_state[0] corresponds to q1.
    # --------------------------------------------------------

    target_q0 = target_state[1]
    target_q1 = target_state[0]

    if target_q0 == "0":
        qc.x(0)

    if target_q1 == "0":
        qc.x(1)

    qc.cz(0, 1)

    if target_q0 == "0":
        qc.x(0)

    if target_q1 == "0":
        qc.x(1)

    # --------------------------------------------------------
    # Diffusion operator
    # --------------------------------------------------------

    qc.h(0)
    qc.h(1)

    qc.x(0)
    qc.x(1)

    qc.cz(0, 1)

    qc.x(0)
    qc.x(1)

    qc.h(0)
    qc.h(1)

    # --------------------------------------------------------
    # Measurement
    # --------------------------------------------------------

    qc.measure(
        [0, 1],
        [0, 1]
    )

    return qc


# ============================================================
# RUN GROVER
# ============================================================

def run_grover(
    target_state="11",
    shots=1000
):
    """
    Execute Grover's algorithm using AerSimulator.
    """

    if shots <= 0:
        raise ValueError(
            "Shots must be greater than zero."
        )

    circuit = create_grover_circuit(
        target_state
    )

    simulator = AerSimulator()

    result = simulator.run(
        circuit,
        shots=shots
    ).result()

    counts = result.get_counts()

    return circuit, counts


# ============================================================
# SUCCESS PROBABILITY
# ============================================================

def calculate_success_probability(
    counts,
    target_state,
    shots
):
    """
    Calculate probability of measuring target state.
    """

    if shots <= 0:
        return 0.0

    target_count = counts.get(
        target_state,
        0
    )

    return target_count / shots


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    TARGET_STATE = "11"
    SHOTS = 1000

    print("=" * 65)
    print("QSHIELD - QUANTUM ALGORITHM LAB")
    print("=" * 65)

    print()
    print("Algorithm:")
    print("Grover's Search Algorithm")

    print()
    print(
        f"Target state: |{TARGET_STATE}>"
    )

    print(
        f"Shots: {SHOTS}"
    )

    # --------------------------------------------------------
    # Execute
    # --------------------------------------------------------

    circuit, counts = run_grover(
        target_state=TARGET_STATE,
        shots=SHOTS
    )

    # --------------------------------------------------------
    # Display circuit
    # --------------------------------------------------------

    print()
    print("Quantum Circuit:")

    print(
        circuit.draw(
            output="text"
        )
    )

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    print()
    print("Measurement Results:")

    print(counts)

    # --------------------------------------------------------
    # Success probability
    # --------------------------------------------------------

    success_probability = (
        calculate_success_probability(
            counts,
            TARGET_STATE,
            SHOTS
        )
    )

    print()
    print(
        "Target-state probability:"
    )

    print(
        f"{success_probability * 100:.2f}%"
    )

    # --------------------------------------------------------
    # Most frequent state
    # --------------------------------------------------------

    most_frequent_state = max(
        counts,
        key=counts.get
    )

    print()
    print(
        "Most frequently measured state:"
    )

    print(
        f"|{most_frequent_state}>"
    )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    print()
    print("RESULT:")

    if most_frequent_state == TARGET_STATE:

        print(
            "Grover successfully identified "
            "the target state."
        )

    else:

        print(
            "The target state was not the "
            "most frequently measured state."
        )

    print()
    print("=" * 65)