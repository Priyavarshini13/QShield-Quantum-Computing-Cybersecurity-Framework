from qiskit import QuantumCircuit


def extract_features(circuit: QuantumCircuit):
    """Convert a quantum circuit into numerical ML features."""

    operations = circuit.count_ops()

    features = {
        "num_qubits": circuit.num_qubits,
        "depth": circuit.depth(),
        "total_gates": circuit.size(),

        "h_gates": operations.get("h", 0),
        "x_gates": operations.get("x", 0),
        "y_gates": operations.get("y", 0),
        "z_gates": operations.get("z", 0),

        "cx_gates": operations.get("cx", 0),
        "cz_gates": operations.get("cz", 0),

        "rx_gates": operations.get("rx", 0),
        "ry_gates": operations.get("ry", 0),
        "rz_gates": operations.get("rz", 0),

        "measurement_gates": operations.get("measure", 0),
        "barriers": operations.get("barrier", 0),
    }

    return features


if __name__ == "__main__":

    # Example quantum circuit
    qc = QuantumCircuit(2, 2)

    qc.h(0)
    qc.cx(0, 1)

    qc.measure([0, 1], [0, 1])

    features = extract_features(qc)

    print("=== QShield Quantum Feature Extractor ===\n")

    for name, value in features.items():
        print(f"{name}: {value}")