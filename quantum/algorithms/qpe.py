from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import numpy as np


# ---------------------------------------------------------
# CONTROLLED-U OPERATION
# ---------------------------------------------------------

def controlled_phase_rotation(
    qc,
    control,
    target,
    angle
):
    """
    Apply a controlled phase rotation.

    This is the controlled-U operation used
    in the QPE circuit.
    """

    qc.cp(
        angle,
        control,
        target
    )


# ---------------------------------------------------------
# INVERSE QFT
# ---------------------------------------------------------

def inverse_qft(
    qc,
    qubits
):
    """
    Apply the inverse Quantum Fourier Transform.
    """

    n = len(qubits)

    # Reverse qubit order
    for i in range(n // 2):
        qc.swap(
            qubits[i],
            qubits[n - i - 1]
        )

    # Inverse QFT
    for j in range(n):

        for m in range(j):

            angle = -np.pi / (
                2 ** (j - m)
            )

            qc.cp(
                angle,
                qubits[m],
                qubits[j]
            )

        qc.h(
            qubits[j]
        )


# ---------------------------------------------------------
# CREATE QPE CIRCUIT
# ---------------------------------------------------------

def create_qpe_circuit(
    num_counting_qubits=3
):
    """
    Create a Quantum Phase Estimation circuit.

    The target qubit is prepared in |1>.
    The unitary operation is a phase rotation.

    For this demonstration:

        phase = 1/4

    The expected phase estimate is approximately:

        0.25
    """

    total_qubits = (
        num_counting_qubits + 1
    )

    qc = QuantumCircuit(
        total_qubits,
        num_counting_qubits
    )

    counting_qubits = list(
        range(num_counting_qubits)
    )

    target_qubit = num_counting_qubits

    # -----------------------------------------------------
    # Prepare target eigenstate |1>
    # -----------------------------------------------------

    qc.x(
        target_qubit
    )

    # -----------------------------------------------------
    # Put counting qubits into superposition
    # -----------------------------------------------------

    for qubit in counting_qubits:

        qc.h(
            qubit
        )

    # -----------------------------------------------------
    # Controlled-U operations
    # -----------------------------------------------------

    phase = 1 / 4

    for j, control in enumerate(
        counting_qubits
    ):

        angle = (
            2
            * np.pi
            * phase
            * (2 ** j)
        )

        controlled_phase_rotation(
            qc,
            control,
            target_qubit,
            angle
        )

    # -----------------------------------------------------
    # Inverse QFT
    # -----------------------------------------------------

    inverse_qft(
        qc,
        counting_qubits
    )

    # -----------------------------------------------------
    # Measurement
    # -----------------------------------------------------

    qc.measure(
        counting_qubits,
        range(num_counting_qubits)
    )

    return qc


# ---------------------------------------------------------
# ESTIMATE PHASE
# ---------------------------------------------------------

def estimate_phase(
    counts,
    num_counting_qubits
):
    """
    Convert the most frequently measured
    binary state into a phase estimate.
    """

    most_frequent_state = max(
        counts,
        key=counts.get
    )

    measured_integer = int(
        most_frequent_state,
        2
    )

    phase_estimate = (
        measured_integer
        /
        (2 ** num_counting_qubits)
    )

    return (
        most_frequent_state,
        phase_estimate
    )


# ---------------------------------------------------------
# RUN QPE
# ---------------------------------------------------------

def run_qpe(
    num_counting_qubits=3,
    shots=1000
):
    """
    Execute the QPE circuit using Aer.
    """

    circuit = create_qpe_circuit(
        num_counting_qubits
    )

    simulator = AerSimulator()

    result = simulator.run(
        circuit,
        shots=shots
    ).result()

    counts = result.get_counts()

    state, phase_estimate = (
        estimate_phase(
            counts,
            num_counting_qubits
        )
    )

    return (
        circuit,
        counts,
        state,
        phase_estimate
    )


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":

    NUM_COUNTING_QUBITS = 3

    SHOTS = 1000

    print(
        "=" * 60
    )

    print(
        "QSHIELD - QUANTUM PHASE ESTIMATION"
    )

    print(
        "=" * 60
    )

    circuit, counts, state, phase = (
        run_qpe(
            NUM_COUNTING_QUBITS,
            SHOTS
        )
    )

    print(
        "\nQPE Circuit:"
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

    print(
        "\nMost frequently measured state:"
    )

    print(
        f"|{state}>"
    )

    print(
        "\nEstimated phase:"
    )

    print(
        f"{phase:.4f}"
    )

    print(
        "\nExpected phase:"
    )

    print(
        "0.2500"
    )

    phase_error = abs(
        phase - 0.25
    )

    print(
        "\nPhase estimation error:"
    )

    print(
        f"{phase_error:.4f}"
    )

    if phase_error <= 0.125:

        print(
            "\nRESULT: "
            "QPE successfully estimated "
            "the target phase."
        )

    else:

        print(
            "\nRESULT: "
            "QPE phase estimation "
            "needs further evaluation."
        )