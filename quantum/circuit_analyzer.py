from qiskit import QuantumCircuit


def analyze_circuit(circuit: QuantumCircuit):
    """Extract structural features from a quantum circuit."""

    features = {
        "num_qubits": circuit.num_qubits,
        "num_classical_bits": circuit.num_clbits,
        "depth": circuit.depth(),
        "total_gates": circuit.size(),
        "num_operations": len(circuit.count_ops()),
        "operations": dict(circuit.count_ops()),
    }

    return features


if __name__ == "__main__":
    # Example circuit
    qc = QuantumCircuit(2, 2)

    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])

    features = analyze_circuit(qc)

    print("=== QShield Circuit Analyzer ===\n")

    for key, value in features.items():
        print(f"{key}: {value}")