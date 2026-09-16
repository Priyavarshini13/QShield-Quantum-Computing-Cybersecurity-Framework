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

from quantum.algorithms.qpe import (
    create_qpe_circuit
)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":

    print(
        "Creating QPE circuit..."
    )

    qpe_circuit = create_qpe_circuit(
        num_counting_qubits=3
    )

    print(
        "\nQPE circuit created successfully."
    )

    print(
        f"Qubits: {qpe_circuit.num_qubits}"
    )

    print(
        f"Gates: {qpe_circuit.size()}"
    )

    # -----------------------------------------------------
    # RUN QSHIELD SECURITY EVALUATION
    # -----------------------------------------------------

    evaluate_algorithm(
        circuit=qpe_circuit,
        algorithm_name="QPE",
        output_filename="qpe_security_results.csv"
    )