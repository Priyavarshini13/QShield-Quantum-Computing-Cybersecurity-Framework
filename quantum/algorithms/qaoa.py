from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import numpy as np


# ---------------------------------------------------------
# GRAPH
# ---------------------------------------------------------

EDGES = [
    (0, 1),
    (1, 2),
    (0, 2)
]


# ---------------------------------------------------------
# CREATE QAOA CIRCUIT
# ---------------------------------------------------------

def create_qaoa_circuit(
    num_qubits=3,
    gamma=np.pi / 8,
    beta=np.pi / 4
):
    """
    Create a QAOA circuit for a 3-node
    triangle MaxCut problem.
    """

    qc = QuantumCircuit(
        num_qubits,
        num_qubits
    )

    # -----------------------------------------------------
    # Initial superposition
    # -----------------------------------------------------

    for qubit in range(num_qubits):

        qc.h(qubit)

    # -----------------------------------------------------
    # Cost Hamiltonian
    # -----------------------------------------------------

    for q1, q2 in EDGES:

        qc.cx(
            q1,
            q2
        )

        qc.rz(
            2 * gamma,
            q2
        )

        qc.cx(
            q1,
            q2
        )

    # -----------------------------------------------------
    # Mixing Hamiltonian
    # -----------------------------------------------------

    for qubit in range(num_qubits):

        qc.rx(
            2 * beta,
            qubit
        )

    # -----------------------------------------------------
    # Measurement
    # -----------------------------------------------------

    qc.measure(
        range(num_qubits),
        range(num_qubits)
    )

    return qc


# ---------------------------------------------------------
# CALCULATE CUT VALUE
# ---------------------------------------------------------

def calculate_cut_value(
    bitstring
):
    """
    Calculate the MaxCut value.

    A cut is counted when the two connected
    vertices have different binary values.
    """

    bits = bitstring[::-1]

    value = 0

    for q1, q2 in EDGES:

        if bits[q1] != bits[q2]:

            value += 1

    return value


# ---------------------------------------------------------
# RUN QAOA
# ---------------------------------------------------------

def run_qaoa(
    num_qubits=3,
    gamma=np.pi / 8,
    beta=np.pi / 4,
    shots=1000
):

    circuit = create_qaoa_circuit(
        num_qubits,
        gamma,
        beta
    )

    simulator = AerSimulator()

    result = simulator.run(
        circuit,
        shots=shots
    ).result()

    counts = result.get_counts()

    return circuit, counts


# ---------------------------------------------------------
# FIND BEST SOLUTION
# ---------------------------------------------------------

def find_best_solution(
    counts
):

    # Find state with highest MaxCut value.
    best_state = None
    best_cut = -1

    for state in counts:

        cut_value = calculate_cut_value(
            state
        )

        if cut_value > best_cut:

            best_cut = cut_value
            best_state = state

    best_count = counts[
        best_state
    ]

    return (
        best_state,
        best_count,
        best_cut
    )


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":

    NUM_QUBITS = 3

    GAMMA = np.pi / 8

    BETA = np.pi / 4

    SHOTS = 1000

    print(
        "=" * 60
    )

    print(
        "QSHIELD - QAOA MAXCUT"
    )

    print(
        "=" * 60
    )

    print(
        "\nProblem:"
    )

    print(
        "3-node MaxCut optimization"
    )

    print(
        "\nParameters:"
    )

    print(
        f"Qubits: {NUM_QUBITS}"
    )

    print(
        f"Gamma: {GAMMA:.4f}"
    )

    print(
        f"Beta: {BETA:.4f}"
    )

    print(
        f"Shots: {SHOTS}"
    )

    # -----------------------------------------------------
    # RUN
    # -----------------------------------------------------

    circuit, counts = run_qaoa(
        NUM_QUBITS,
        GAMMA,
        BETA,
        SHOTS
    )

    print(
        "\nQAOA Circuit:"
    )

    print(
        circuit
    )

    print(
        "\nMeasurement Results:"
    )

    print(
        counts
    )

    # -----------------------------------------------------
    # BEST SOLUTION
    # -----------------------------------------------------

    best_state, best_count, cut_value = (
        find_best_solution(
            counts
        )
    )

    print(
        "\nBest MaxCut state:"
    )

    print(
        f"|{best_state}>"
    )

    print(
        "\nOccurrences:"
    )

    print(
        best_count
    )

    print(
        "\nMaxCut value:"
    )

    print(
        f"{cut_value} / 3"
    )

    # -----------------------------------------------------
    # RESULT
    # -----------------------------------------------------

    if cut_value == 2:

        print(
            "\nRESULT: "
            "QAOA found an optimal MaxCut solution."
        )

    else:

        print(
            "\nRESULT: "
            "QAOA did not find an optimal solution."
        )