from qasm_loader import load_qasm_circuit
from feature_extractor import extract_features


if __name__ == "__main__":

    file_path = "data/benchmarks/bell_n4.qasm"

    circuit = load_qasm_circuit(file_path)

    features = extract_features(circuit)

    print("=== QShield QASMBench Feature Extraction ===\n")

    for name, value in features.items():
        print(f"{name}: {value}")