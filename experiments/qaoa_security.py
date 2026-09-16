import os
import sys

# ---------------------------------------------------------
# PROJECT PATH
# ---------------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)


# ---------------------------------------------------------
# QSHIELD FRAMEWORK
# ---------------------------------------------------------

from experiments.algorithm_security import (
    evaluate_algorithm
)

from quantum.algorithms.qaoa import (
    create_qaoa_circuit
)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":

    print(
        "Creating QAOA circuit..."
    )

    qaoa_circuit = create_qaoa_circuit(
        num_qubits=3
    )

    print(
        "\nQAOA circuit created successfully."
    )

    print(
        f"Qubits: {qaoa_circuit.num_qubits}"
    )

    print(
        f"Gates: {qaoa_circuit.size()}"
    )

    evaluate_algorithm(
        circuit=qaoa_circuit,
        algorithm_name="QAOA",
        output_filename="qaoa_security_results.csv"
    )