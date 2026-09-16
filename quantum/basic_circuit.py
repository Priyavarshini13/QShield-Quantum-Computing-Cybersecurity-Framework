from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


def create_bell_circuit():
    """Create a simple 2-qubit Bell-state circuit."""
    circuit = QuantumCircuit(2, 2)

    # Put qubit 0 into superposition
    circuit.h(0)

    # Entangle qubit 0 and qubit 1
    circuit.cx(0, 1)

    # Measure both qubits
    circuit.measure([0, 1], [0, 1])

    return circuit


def run_circuit(circuit, shots=1000):
    """Run the circuit using a local quantum simulator."""
    simulator = AerSimulator()

    job = simulator.run(circuit, shots=shots)
    result = job.result()

    return result.get_counts()


if __name__ == "__main__":
    circuit = create_bell_circuit()

    print("=== Quantum Circuit ===")
    print(circuit)

    counts = run_circuit(circuit)

    print("\n=== Measurement Results ===")
    print(counts)