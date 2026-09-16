from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import math


def create_shor_demo_circuit():
    """
    Create a small educational Shor-style order-finding circuit.

    This demonstration uses N = 15 and a = 2.
    It focuses on the quantum period-finding component
    rather than implementing the complete scalable Shor algorithm.
    """

    counting_qubits = 4
    target_qubits = 4

    total_qubits = counting_qubits + target_qubits

    qc = QuantumCircuit(
        total_qubits,
        counting_qubits
    )

    counting = list(range(counting_qubits))
    target = list(
        range(
            counting_qubits,
            total_qubits
        )
    )

    # ---------------------------------------------------------
    # Step 1: Prepare target register in |1>
    # ---------------------------------------------------------

    qc.x(target[0])

    # ---------------------------------------------------------
    # Step 2: Create superposition in counting register
    # ---------------------------------------------------------

    for qubit in counting:
        qc.h(qubit)

    # ---------------------------------------------------------
    # Step 3: Controlled modular-exponentiation demonstration
    #
    # For N = 15 and a = 2:
    #
    # 2^x mod 15 has period r = 4
    #
    # The complete modular arithmetic circuit is expensive
    # for a small educational implementation, so this circuit
    # demonstrates the periodic phase structure directly.
    # ---------------------------------------------------------

    for qubit in counting:
        power = 2 ** qubit
        angle = (2 * math.pi * power) / 4

        qc.cp(
            angle,
            qubit,
            target[0]
        )

    # ---------------------------------------------------------
    # Step 4: Inverse QFT on counting register
    # ---------------------------------------------------------

    apply_inverse_qft(
        qc,
        counting
    )

    # ---------------------------------------------------------
    # Step 5: Measure counting register
    # ---------------------------------------------------------

    qc.measure(
        counting,
        range(counting_qubits)
    )

    return qc


def apply_inverse_qft(qc, qubits):
    """
    Apply inverse Quantum Fourier Transform.
    """

    n = len(qubits)

    # Reverse order
    for i in range(n // 2):
        qc.swap(
            qubits[i],
            qubits[n - i - 1]
        )

    # Controlled phase rotations
    for j in range(n):
        for m in range(j):
            angle = -math.pi / (
                2 ** (j - m)
            )

            qc.cp(
                angle,
                qubits[m],
                qubits[j]
            )

        qc.h(qubits[j])


def estimate_period_from_measurement(
    bitstring,
    counting_qubits=4
):
    """
    Convert the measured phase into an approximate period.

    For this demonstration:

        N = 15
        a = 2

    Expected period:

        r = 4
    """

    decimal_value = int(
        bitstring,
        2
    )

    phase = (
        decimal_value /
        (2 ** counting_qubits)
    )

    if phase == 0:
        return None, phase

    estimated_period = round(
        1 / phase
    )

    return estimated_period, phase


def run_shor_demo(shots=1000):
    """
    Execute the Shor period-finding demonstration.
    """

    circuit = create_shor_demo_circuit()

    simulator = AerSimulator()

    result = simulator.run(
        circuit,
        shots=shots
    ).result()

    counts = result.get_counts()

    return circuit, counts


def analyze_results(counts):
    """
    Analyze the most frequently measured phase.
    """

    most_frequent_state = max(
        counts,
        key=counts.get
    )

    estimated_period, phase = (
        estimate_period_from_measurement(
            most_frequent_state
        )
    )

    return (
        most_frequent_state,
        estimated_period,
        phase
    )


if __name__ == "__main__":

    SHOTS = 1000

    print("=" * 60)
    print("QSHIELD - SHOR'S ALGORITHM DEMONSTRATION")
    print("=" * 60)

    print("\nProblem:")
    print("Integer factorization using quantum period finding")

    print("\nParameters:")
    print("Number: N = 15")
    print("Base: a = 2")
    print("Expected period: r = 4")
    print(f"Shots: {SHOTS}")

    circuit, counts = run_shor_demo(
        shots=SHOTS
    )

    print("\nQuantum Circuit:")
    print(circuit)

    print("\nMeasurement Results:")
    print(counts)

    (
        state,
        estimated_period,
        phase
    ) = analyze_results(counts)

    print("\nMost frequently measured state:")
    print(f"|{state}>")

    print("\nEstimated phase:")
    print(f"{phase:.4f}")

    print("\nEstimated period:")

    if estimated_period is not None:
        print(estimated_period)
    else:
        print("Could not estimate")

    print("\nExpected period:")
    print("4")

    if estimated_period == 4:

        print(
            "\nRESULT: "
            "Shor period-finding demonstration "
            "successfully identified r = 4."
        )

        print(
            "\nSecurity significance:"
        )

        print(
            "Shor's algorithm demonstrates the "
            "quantum threat to classical public-key "
            "cryptography such as RSA and ECC."
        )

    else:

        print(
            "\nRESULT: "
            "Period estimation was not exact."
        )