from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error


def create_normal_circuit():
    """Create a simple Bell-state circuit."""

    qc = QuantumCircuit(2, 2)

    qc.h(0)
    qc.cx(0, 1)

    qc.measure([0, 1], [0, 1])

    return qc


def create_noise_model():
    """Create a simple quantum hardware noise model."""

    noise_model = NoiseModel()

    # Single-qubit depolarizing error
    single_qubit_error = depolarizing_error(
        0.02,
        1
    )

    # Two-qubit depolarizing error
    two_qubit_error = depolarizing_error(
        0.05,
        2
    )

    # Apply noise to gates
    noise_model.add_all_qubit_quantum_error(
        single_qubit_error,
        ["h"]
    )

    noise_model.add_all_qubit_quantum_error(
        two_qubit_error,
        ["cx"]
    )

    return noise_model


def run_with_noise(circuit, noise_model, shots=1000):
    """Run a quantum circuit with simulated hardware noise."""

    simulator = AerSimulator(
        noise_model=noise_model
    )

    result = simulator.run(
        circuit,
        shots=shots
    ).result()

    return result.get_counts()


if __name__ == "__main__":

    SHOTS = 1000

    circuit = create_normal_circuit()

    noise_model = create_noise_model()

    noisy_counts = run_with_noise(
        circuit,
        noise_model,
        SHOTS
    )

    print("=== QShield Quantum Noise Simulator ===")

    print("\nCircuit:")
    print(circuit)

    print("\nNoise Model:")
    print(noise_model)

    print("\nNoisy Measurement Results:")
    print(noisy_counts)