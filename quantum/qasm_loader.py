from qiskit import qasm2


def load_qasm_circuit(file_path):
    """Load an OpenQASM 2.0 circuit."""

    circuit = qasm2.load(file_path)

    return circuit


if __name__ == "__main__":

    file_path = "data/benchmarks/bell_n4.qasm"

    circuit = load_qasm_circuit(file_path)

    print("=== QShield QASMBench Loader ===")

    print("\nCircuit:")
    print(circuit)

    print("\nNumber of qubits:")
    print(circuit.num_qubits)

    print("\nCircuit depth:")
    print(circuit.depth())

    print("\nTotal gates:")
    print(circuit.size())

    print("\nOperations:")
    print(circuit.count_ops())