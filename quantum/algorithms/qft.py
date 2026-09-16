from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


def create_qft_circuit(num_qubits=3):
    qc = QuantumCircuit(num_qubits, num_qubits)

    # Prepare a simple input state
    qc.x(0)

    # Quantum Fourier Transform
    for j in range(num_qubits):
        qc.h(j)

        for k in range(j + 1, num_qubits):
            angle = 3.141592653589793 / (2 ** (k - j))
            qc.cp(angle, k, j)

    # Swap qubits for final ordering
    for i in range(num_qubits // 2):
        qc.swap(i, num_qubits - i - 1)

    qc.measure(range(num_qubits), range(num_qubits))

    return qc


def run_qft(num_qubits=3, shots=1000):
    circuit = create_qft_circuit(num_qubits)

    simulator = AerSimulator()

    result = simulator.run(
        circuit,
        shots=shots
    ).result()

    counts = result.get_counts()

    return circuit, counts


if __name__ == "__main__":
    circuit, counts = run_qft()

    print("QFT Circuit:")
    print(circuit)

    print("\nMeasurement Results:")
    print(counts)

    print("\nRESULT: QFT circuit executed successfully.")