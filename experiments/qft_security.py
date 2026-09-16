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

from quantum.algorithms.qft import (
    create_qft_circuit
)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":

    print(
        "Creating QFT circuit..."
    )

    qft_circuit = create_qft_circuit(
        num_qubits=3
    )

    print(
        "\nQFT circuit created successfully."
    )

    print(
        f"Qubits: {qft_circuit.num_qubits}"
    )

    print(
        f"Gates: {qft_circuit.size()}"
    )

    # -----------------------------------------------------
    # RUN QSHIELD SECURITY EVALUATION
    # -----------------------------------------------------

    evaluate_algorithm(
        circuit=qft_circuit,
        algorithm_name="QFT",
        output_filename="qft_security_results.csv"
    )