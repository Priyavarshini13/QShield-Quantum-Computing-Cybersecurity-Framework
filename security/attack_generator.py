import os
import random
import sys

from qiskit import QuantumCircuit


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.append(PROJECT_ROOT)

from quantum.qasm_loader import load_qasm_circuit


# ============================================================
# SINGLE-QUBIT MUTATION GATES
# ============================================================

SINGLE_QUBIT_GATES = [
    "x",
    "y",
    "z",
    "h",
]


# ============================================================
# HELPER: ADD SINGLE-QUBIT GATE
# ============================================================

def add_gate(
    circuit,
    gate_name,
    qubit,
):
    """
    Add a supported single-qubit gate
    to a quantum circuit.
    """

    if gate_name == "x":
        circuit.x(qubit)

    elif gate_name == "y":
        circuit.y(qubit)

    elif gate_name == "z":
        circuit.z(qubit)

    elif gate_name == "h":
        circuit.h(qubit)


# ============================================================
# HELPER: COPY CIRCUIT
# ============================================================

def copy_circuit(circuit):
    """
    Create a structural copy of the circuit.
    """

    return circuit.copy()


# ============================================================
# HELPER: GET ELIGIBLE GATES
# ============================================================

def get_eligible_gate_indices(
    circuit,
):
    """
    Return indices of operations that can safely
    participate in mutation.

    Measurement and barrier operations are excluded.
    """

    eligible_indices = []

    for index, instruction in enumerate(
        circuit.data
    ):

        operation = instruction.operation

        if operation.name in [
            "measure",
            "barrier",
        ]:
            continue

        eligible_indices.append(
            index
        )

    return eligible_indices


# ============================================================
# HELPER: GET SINGLE-QUBIT GATES
# ============================================================

def get_single_qubit_gate_indices(
    circuit,
):
    """
    Return indices of non-measurement,
    non-barrier single-qubit operations.
    """

    eligible_indices = []

    for index, instruction in enumerate(
        circuit.data
    ):

        operation = instruction.operation

        if operation.name in [
            "measure",
            "barrier",
        ]:
            continue

        if len(instruction.qubits) != 1:
            continue

        eligible_indices.append(
            index
        )

    return eligible_indices


# ============================================================
# GATE INSERTION
# ============================================================

def gate_insertion(
    circuit,
):
    """
    Insert one random single-qubit gate immediately
    before the first measurement.

    The original circuit structure and measurements
    are preserved.
    """

    mutated = QuantumCircuit(
        circuit.num_qubits,
        circuit.num_clbits,
    )

    inserted = False

    for instruction in circuit.data:

        operation = instruction.operation

        qubits = [
            circuit.find_bit(q).index
            for q in instruction.qubits
        ]

        clbits = [
            circuit.find_bit(c).index
            for c in instruction.clbits
        ]

        # Insert attack immediately before measurement.
        if (
            operation.name == "measure"
            and not inserted
        ):

            gate = random.choice(
                SINGLE_QUBIT_GATES
            )

            qubit = random.randrange(
                circuit.num_qubits
            )

            add_gate(
                mutated,
                gate,
                qubit,
            )

            inserted = True

        mutated.append(
            operation,
            qubits,
            clbits,
        )

    # If the circuit has no measurement,
    # append the mutation at the end.
    if not inserted:

        gate = random.choice(
            SINGLE_QUBIT_GATES
        )

        qubit = random.randrange(
            circuit.num_qubits
        )

        add_gate(
            mutated,
            gate,
            qubit,
        )

    return mutated


# ============================================================
# GATE DELETION
# ============================================================

def gate_deletion(
    circuit,
):
    """
    Delete one eligible quantum operation.

    To make deletion more meaningful, operations are
    selected from non-measurement and non-barrier gates.

    Multi-qubit operations remain valid because the complete
    instruction is removed rather than reconstructing it.
    """

    eligible_indices = (
        get_eligible_gate_indices(
            circuit
        )
    )

    if not eligible_indices:
        return copy_circuit(
            circuit
        )

    # Prefer actual quantum gates over metadata-like
    # operations when possible.
    quantum_gate_indices = []

    for index in eligible_indices:

        operation = (
            circuit.data[index]
            .operation
        )

        if operation.name not in [
            "delay",
            "reset",
        ]:
            quantum_gate_indices.append(
                index
            )

    if quantum_gate_indices:
        eligible_indices = (
            quantum_gate_indices
        )

    delete_index = random.choice(
        eligible_indices
    )

    mutated = QuantumCircuit(
        circuit.num_qubits,
        circuit.num_clbits,
    )

    for index, instruction in enumerate(
        circuit.data
    ):

        if index == delete_index:
            continue

        operation = instruction.operation

        qubits = [
            circuit.find_bit(q).index
            for q in instruction.qubits
        ]

        clbits = [
            circuit.find_bit(c).index
            for c in instruction.clbits
        ]

        mutated.append(
            operation,
            qubits,
            clbits,
        )

    return mutated


# ============================================================
# GATE SUBSTITUTION
# ============================================================

def gate_substitution(
    circuit,
):
    """
    Replace one single-qubit gate with a different
    supported single-qubit gate.

    Multi-qubit operations are intentionally excluded
    because replacing them with a single-qubit gate would
    change circuit semantics and arity.
    """

    eligible_indices = (
        get_single_qubit_gate_indices(
            circuit
        )
    )

    if not eligible_indices:
        return copy_circuit(
            circuit
        )

    substitute_index = random.choice(
        eligible_indices
    )

    mutated = QuantumCircuit(
        circuit.num_qubits,
        circuit.num_clbits,
    )

    for index, instruction in enumerate(
        circuit.data
    ):

        operation = instruction.operation

        qubits = [
            circuit.find_bit(q).index
            for q in instruction.qubits
        ]

        clbits = [
            circuit.find_bit(c).index
            for c in instruction.clbits
        ]

        if index == substitute_index:

            original_gate = (
                operation.name
            )

            available_gates = [
                gate
                for gate in SINGLE_QUBIT_GATES
                if gate != original_gate
            ]

            # If the original gate is not one of our
            # supported mutation gates, choose randomly.
            if not available_gates:
                available_gates = (
                    SINGLE_QUBIT_GATES
                )

            new_gate = random.choice(
                available_gates
            )

            add_gate(
                mutated,
                new_gate,
                qubits[0],
            )

            continue

        mutated.append(
            operation,
            qubits,
            clbits,
        )

    return mutated


# ============================================================
# MULTIPLE GATE INSERTION
# ============================================================

def multiple_gate_insertion(
    circuit,
    number_of_gates=2,
):
    """
    Insert multiple random single-qubit gates immediately
    before the first measurement.

    This represents a stronger compound mutation.
    """

    if number_of_gates <= 0:
        return copy_circuit(
            circuit
        )

    mutated = QuantumCircuit(
        circuit.num_qubits,
        circuit.num_clbits,
    )

    inserted = False

    for instruction in circuit.data:

        operation = instruction.operation

        qubits = [
            circuit.find_bit(q).index
            for q in instruction.qubits
        ]

        clbits = [
            circuit.find_bit(c).index
            for c in instruction.clbits
        ]

        # Insert multiple mutations before measurement.
        if (
            operation.name == "measure"
            and not inserted
        ):

            for _ in range(
                number_of_gates
            ):

                gate = random.choice(
                    SINGLE_QUBIT_GATES
                )

                qubit = random.randrange(
                    circuit.num_qubits
                )

                add_gate(
                    mutated,
                    gate,
                    qubit,
                )

            inserted = True

        mutated.append(
            operation,
            qubits,
            clbits,
        )

    # Handle circuits without measurement.
    if not inserted:

        for _ in range(
            number_of_gates
        ):

            gate = random.choice(
                SINGLE_QUBIT_GATES
            )

            qubit = random.randrange(
                circuit.num_qubits
            )

            add_gate(
                mutated,
                gate,
                qubit,
            )

    return mutated


# ============================================================
# MUTATION DISPATCHER
# ============================================================

def apply_attack(
    circuit,
    attack_type,
):
    """
    Apply a selected QShield attack.

    Supported attack names:

        normal
        gate_insertion
        gate_deletion
        gate_substitution
        multiple_gate_insertion
    """

    if attack_type == "normal":
        return copy_circuit(
            circuit
        )

    if attack_type == "gate_insertion":
        return gate_insertion(
            circuit
        )

    if attack_type == "gate_deletion":
        return gate_deletion(
            circuit
        )

    if attack_type == "gate_substitution":
        return gate_substitution(
            circuit
        )

    if attack_type == "multiple_gate_insertion":
        return multiple_gate_insertion(
            circuit
        )

    raise ValueError(
        f"Unsupported attack type: {attack_type}"
    )


# ============================================================
# CIRCUIT INFORMATION
# ============================================================

def print_circuit_info(
    name,
    circuit,
):
    """
    Print important circuit information.
    """

    print(
        f"\n=== {name} ==="
    )

    print(
        "Qubits:",
        circuit.num_qubits,
    )

    print(
        "Depth:",
        circuit.depth(),
    )

    print(
        "Total gates:",
        circuit.size(),
    )

    print(
        "Operations:",
        circuit.count_ops(),
    )


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    random.seed(42)

    file_path = os.path.join(
        PROJECT_ROOT,
        "data",
        "benchmarks",
        "bell_n4.qasm",
    )

    original = load_qasm_circuit(
        file_path
    )

    inserted = gate_insertion(
        original
    )

    deleted = gate_deletion(
        original
    )

    substituted = gate_substitution(
        original
    )

    multiple_inserted = (
        multiple_gate_insertion(
            original,
            number_of_gates=2,
        )
    )

    print(
        "=== QShield Enhanced Attack Generator ==="
    )

    print_circuit_info(
        "ORIGINAL",
        original,
    )

    print_circuit_info(
        "RANDOM GATE INSERTION",
        inserted,
    )

    print_circuit_info(
        "RANDOM GATE DELETION",
        deleted,
    )

    print_circuit_info(
        "RANDOM GATE SUBSTITUTION",
        substituted,
    )

    print_circuit_info(
        "MULTIPLE GATE INSERTION",
        multiple_inserted,
    )