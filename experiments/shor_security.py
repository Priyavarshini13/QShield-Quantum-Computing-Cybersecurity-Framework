import os
import sys

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)


from experiments.algorithm_security import (
    evaluate_algorithm
)

from quantum.algorithms.shor import (
    create_shor_demo_circuit
)


if __name__ == "__main__":

    print("Creating Shor circuit...")

    shor_circuit = create_shor_demo_circuit()

    print("\nShor circuit created successfully.")
    print(f"Qubits: {shor_circuit.num_qubits}")
    print(f"Gates: {shor_circuit.size()}")

    evaluate_algorithm(
        circuit=shor_circuit,
        algorithm_name="Shor",
        output_filename="shor_security_results.csv"
    )