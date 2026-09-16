import os
import random
import sys
import zipfile

import pandas as pd

from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error


# ---------------------------------------------------------
# PROJECT PATH
# ---------------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.append(PROJECT_ROOT)


# ---------------------------------------------------------
# PROJECT IMPORTS
# ---------------------------------------------------------

from quantum.qasm_loader import load_qasm_circuit
from quantum.feature_extractor import extract_features

from security.attack_generator import (
    gate_insertion,
    gate_deletion,
    gate_substitution,
    multiple_gate_insertion,
)


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

ZIP_FILE = os.path.join(
    PROJECT_ROOT,
    "QASMBench-master.zip",
)

OUTPUT_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "qshield_dataset.csv",
)

TEMP_DIR = os.path.join(
    PROJECT_ROOT,
    "data",
    "temp_benchmarks",
)

# Number of measurement shots
SHOTS = 200

# Number of repeated samples for each
# circuit + attack + noise combination
SAMPLES_PER_VARIATION = 3

# ---------------------------------------------------------
# IMPORTANT:
# The dataset MUST contain normal samples at every
# noise level used by the robustness experiment.
# ---------------------------------------------------------

NOISE_LEVELS = [
    0.005,
    0.010,
    0.020,
    0.030,
    0.040,
    0.050,
]

# Reproducibility
random.seed(42)


# ---------------------------------------------------------
# NOISE MODEL
# ---------------------------------------------------------

def create_noise_model(error_rate):
    """
    Create a depolarizing noise model.

    Single-qubit gates:
        error_rate

    Two-qubit gates:
        2 * error_rate
    """

    noise_model = NoiseModel()

    # ---------------------------------------------
    # Single-qubit depolarizing error
    # ---------------------------------------------

    single_qubit_error = depolarizing_error(
        error_rate,
        1,
    )

    # ---------------------------------------------
    # Two-qubit depolarizing error
    # ---------------------------------------------

    two_qubit_error = depolarizing_error(
        error_rate * 2,
        2,
    )

    # ---------------------------------------------
    # Apply single-qubit errors
    # ---------------------------------------------

    noise_model.add_all_qubit_quantum_error(
        single_qubit_error,
        [
            "h",
            "x",
            "y",
            "z",
            "rx",
            "ry",
            "rz",
            "u3",
        ],
    )

    # ---------------------------------------------
    # Apply two-qubit errors
    # ---------------------------------------------

    noise_model.add_all_qubit_quantum_error(
        two_qubit_error,
        [
            "cx",
            "cz",
        ],
    )

    return noise_model


# ---------------------------------------------------------
# RUN CIRCUIT
# ---------------------------------------------------------

def run_circuit(
    circuit,
    noise_model=None,
):
    """
    Execute a quantum circuit using AerSimulator.

    If noise_model is None:
        ideal simulation

    Otherwise:
        noisy simulation
    """

    if noise_model is None:
        simulator = AerSimulator()

    else:
        simulator = AerSimulator(
            noise_model=noise_model
        )

    result = simulator.run(
        circuit,
        shots=SHOTS,
    ).result()

    return result.get_counts()


# ---------------------------------------------------------
# NORMALIZE COUNTS
# ---------------------------------------------------------

def normalize_counts(counts):
    """
    Normalize Qiskit measurement keys.

    Example:

        '1 0 0 0' -> '1000'

    This makes multi-register measurement results
    easier to compare.
    """

    normalized = {}

    for state, count in counts.items():

        clean_state = state.replace(
            " ",
            "",
        )

        normalized[clean_state] = (
            normalized.get(
                clean_state,
                0,
            )
            + count
        )

    return normalized


# ---------------------------------------------------------
# TVD
# ---------------------------------------------------------

def calculate_tvd(
    reference_counts,
    observed_counts,
):
    """
    Calculate Total Variation Distance.

    TVD = 1/2 * sum(|P(x) - Q(x)|)
    """

    reference_counts = normalize_counts(
        reference_counts
    )

    observed_counts = normalize_counts(
        observed_counts
    )

    # ---------------------------------------------
    # Convert counts to probability distributions
    # ---------------------------------------------

    reference_distribution = {
        state: count / SHOTS
        for state, count in reference_counts.items()
    }

    observed_distribution = {
        state: count / SHOTS
        for state, count in observed_counts.items()
    }

    # ---------------------------------------------
    # Union of all observed states
    # ---------------------------------------------

    all_states = (
        set(reference_distribution)
        | set(observed_distribution)
    )

    difference = 0.0

    for state in all_states:

        p = reference_distribution.get(
            state,
            0,
        )

        q = observed_distribution.get(
            state,
            0,
        )

        difference += abs(p - q)

    return difference / 2


# ---------------------------------------------------------
# CREATE ATTACK VARIANTS
# ---------------------------------------------------------

def generate_attack_variants(circuit):
    """
    Generate attack/mutation variants.

    Attack types:

        1. gate_insertion
        2. gate_deletion
        3. gate_substitution
        4. multiple_gate_insertion
    """

    variants = []

    # -----------------------------------------------------
    # Gate insertion
    # -----------------------------------------------------

    try:

        variants.append(
            (
                "gate_insertion",
                gate_insertion(circuit),
            )
        )

    except Exception as error:

        print(
            f"  Gate insertion failed: {error}"
        )

    # -----------------------------------------------------
    # Gate deletion
    # -----------------------------------------------------

    try:

        variants.append(
            (
                "gate_deletion",
                gate_deletion(circuit),
            )
        )

    except Exception as error:

        print(
            f"  Gate deletion failed: {error}"
        )

    # -----------------------------------------------------
    # Gate substitution
    # -----------------------------------------------------

    try:

        variants.append(
            (
                "gate_substitution",
                gate_substitution(circuit),
            )
        )

    except Exception as error:

        print(
            f"  Gate substitution failed: {error}"
        )

    # -----------------------------------------------------
    # Multiple gate insertion
    # -----------------------------------------------------

    try:

        number_of_gates = random.choice(
            [2, 3]
        )

        variants.append(
            (
                "multiple_gate_insertion",
                multiple_gate_insertion(
                    circuit,
                    number_of_gates,
                ),
            )
        )

    except Exception as error:

        print(
            f"  Multiple gate insertion failed: {error}"
        )

    return variants


# ---------------------------------------------------------
# PROCESS CIRCUIT
# ---------------------------------------------------------

def process_circuit(qasm_path):

    # -----------------------------------------------------
    # Load QASM circuit
    # -----------------------------------------------------

    circuit = load_qasm_circuit(
        qasm_path
    )

    # -----------------------------------------------------
    # Avoid extremely expensive simulations
    # -----------------------------------------------------

    if circuit.num_qubits > 12:

        print(
            f"  Skipped: more than 12 qubits "
            f"({circuit.num_qubits})"
        )

        return []

    # -----------------------------------------------------
    # Skip single-qubit circuits
    # -----------------------------------------------------

    if circuit.num_qubits < 2:

        print(
            f"  Skipped: fewer than 2 qubits"
        )

        return []

    print(
        f"\nProcessing: "
        f"{os.path.basename(qasm_path)} "
        f"({circuit.num_qubits} qubits)"
    )

    dataset_rows = []

    # -----------------------------------------------------
    # IDEAL REFERENCE
    # -----------------------------------------------------

    try:

        ideal_counts = run_circuit(
            circuit
        )

    except Exception as error:

        print(
            f"  Ideal simulation failed: {error}"
        )

        return []

    # -----------------------------------------------------
    # NORMAL + ATTACK VARIANTS
    # -----------------------------------------------------

    variants = [
        (
            "normal",
            circuit,
        )
    ]

    variants.extend(
        generate_attack_variants(
            circuit
        )
    )

    # -----------------------------------------------------
    # NOISE + VARIATIONS
    # -----------------------------------------------------

    for attack_type, mutated_circuit in variants:

        for noise_rate in NOISE_LEVELS:

            print(
                f"  {attack_type:<25} "
                f"noise={noise_rate:.3f}",
                end="",
            )

            # ---------------------------------------------
            # Create noise model
            # ---------------------------------------------

            try:

                noise_model = create_noise_model(
                    noise_rate
                )

            except Exception as error:

                print(
                    f" -> noise model failed: {error}"
                )

                continue

            successful_samples = 0

            # ---------------------------------------------
            # Generate repeated samples
            # ---------------------------------------------

            for sample_id in range(
                SAMPLES_PER_VARIATION
            ):

                try:

                    # -------------------------------------
                    # Execute circuit with noise
                    # -------------------------------------

                    observed_counts = run_circuit(
                        mutated_circuit,
                        noise_model,
                    )

                    # -------------------------------------
                    # Behavioral difference
                    # -------------------------------------

                    tvd = calculate_tvd(
                        ideal_counts,
                        observed_counts,
                    )

                    # -------------------------------------
                    # Extract circuit features
                    # -------------------------------------

                    features = extract_features(
                        mutated_circuit
                    )

                    # -------------------------------------
                    # Metadata
                    # -------------------------------------

                    features[
                        "circuit_name"
                    ] = os.path.basename(
                        qasm_path
                    )

                    features[
                        "attack_type"
                    ] = attack_type

                    features[
                        "noise_rate"
                    ] = noise_rate

                    features[
                        "sample_id"
                    ] = sample_id

                    features[
                        "tvd"
                    ] = tvd

                    # -------------------------------------
                    # Classification label
                    #
                    # 0 = normal
                    # 1 = anomalous
                    # -------------------------------------

                    if attack_type == "normal":

                        features[
                            "label"
                        ] = 0

                    else:

                        features[
                            "label"
                        ] = 1

                    dataset_rows.append(
                        features
                    )

                    successful_samples += 1

                except Exception as error:

                    print(
                        f"\n    Sample {sample_id} "
                        f"failed: {error}"
                    )

            print(
                f" -> {successful_samples}/"
                f"{SAMPLES_PER_VARIATION} samples"
            )

    return dataset_rows


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print(
        "\n========================================"
    )

    print(
        " QShield Enhanced Research Dataset"
    )

    print(
        " Generator"
    )

    print(
        "========================================"
    )

    print(
        "\nNoise levels:"
    )

    for noise in NOISE_LEVELS:

        print(
            f"  - {noise:.3f}"
        )

    print(
        f"\nShots per sample: {SHOTS}"
    )

    print(
        f"Samples per variation: "
        f"{SAMPLES_PER_VARIATION}"
    )

    # -----------------------------------------------------
    # Check QASMBench ZIP
    # -----------------------------------------------------

    if not os.path.exists(
        ZIP_FILE
    ):

        print(
            "\nERROR:"
        )

        print(
            "QASMBench ZIP not found:"
        )

        print(
            ZIP_FILE
        )

        return

    # -----------------------------------------------------
    # Create required directories
    # -----------------------------------------------------

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True,
    )

    os.makedirs(
        TEMP_DIR,
        exist_ok=True,
    )

    dataset = []

    # -----------------------------------------------------
    # Open QASMBench
    # -----------------------------------------------------

    try:

        with zipfile.ZipFile(
            ZIP_FILE,
            "r",
        ) as archive:

            # ---------------------------------------------
            # Find small QASMBench circuits
            # ---------------------------------------------

            qasm_files = [
                name
                for name in archive.namelist()
                if (
                    name.startswith(
                        "QASMBench-master/small/"
                    )
                    and name.endswith(
                        ".qasm"
                    )
                    and "_transpiled.qasm"
                    not in name
                )
            ]

            print(
                f"\nFound "
                f"{len(qasm_files)} "
                f"small benchmark circuits."
            )

            # ---------------------------------------------
            # Process every circuit
            # ---------------------------------------------

            for index, qasm_file in enumerate(
                qasm_files,
                start=1,
            ):

                print(
                    "\n----------------------------------------"
                )

                print(
                    f"Circuit {index}/"
                    f"{len(qasm_files)}"
                )

                print(
                    f"File: {qasm_file}"
                )

                try:

                    # -------------------------------------
                    # Extract circuit
                    # -------------------------------------

                    archive.extract(
                        qasm_file,
                        TEMP_DIR,
                    )

                    extracted_path = os.path.join(
                        TEMP_DIR,
                        qasm_file,
                    )

                    # -------------------------------------
                    # Process circuit
                    # -------------------------------------

                    rows = process_circuit(
                        extracted_path
                    )

                    dataset.extend(
                        rows
                    )

                except Exception as error:

                    print(
                        "\nSkipped circuit:"
                    )

                    print(
                        qasm_file
                    )

                    print(
                        f"Reason: {error}"
                    )

    except zipfile.BadZipFile:

        print(
            "\nERROR: Invalid QASMBench ZIP file."
        )

        return

    # -----------------------------------------------------
    # Check dataset
    # -----------------------------------------------------

    if not dataset:

        print(
            "\nNo samples generated."
        )

        return

    # -----------------------------------------------------
    # Create DataFrame
    # -----------------------------------------------------

    dataframe = pd.DataFrame(
        dataset
    )

    # -----------------------------------------------------
    # Sort dataset
    #
    # Makes the generated CSV easier to inspect.
    # -----------------------------------------------------

    sort_columns = [
        "circuit_name",
        "attack_type",
        "noise_rate",
        "sample_id",
    ]

    available_sort_columns = [
        column
        for column in sort_columns
        if column in dataframe.columns
    ]

    if available_sort_columns:

        dataframe = dataframe.sort_values(
            by=available_sort_columns
        ).reset_index(
            drop=True
        )

    # -----------------------------------------------------
    # Save dataset
    # -----------------------------------------------------

    dataframe.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    # -----------------------------------------------------
    # Results
    # -----------------------------------------------------

    print(
        "\n========================================"
    )

    print(
        "QShield dataset generated successfully!"
    )

    print(
        "========================================"
    )

    print(
        f"\nTotal samples: "
        f"{len(dataframe)}"
    )

    print(
        f"Columns: "
        f"{len(dataframe.columns)}"
    )

    print(
        f"\nSaved to:"
    )

    print(
        OUTPUT_FILE
    )

    # -----------------------------------------------------
    # Class distribution
    # -----------------------------------------------------

    print(
        "\nClass distribution:"
    )

    print(
        dataframe[
            "label"
        ].value_counts()
    )

    # -----------------------------------------------------
    # Attack distribution
    # -----------------------------------------------------

    print(
        "\nAttack distribution:"
    )

    print(
        dataframe[
            "attack_type"
        ].value_counts()
    )

    # -----------------------------------------------------
    # Noise distribution
    # -----------------------------------------------------

    print(
        "\nNoise distribution:"
    )

    print(
        dataframe[
            "noise_rate"
        ].value_counts()
        .sort_index()
    )

    # -----------------------------------------------------
    # IMPORTANT VALIDATION
    #
    # Verify that NORMAL samples exist at every noise
    # level. This is required for noise-aware baseline
    # calibration.
    # -----------------------------------------------------

    print(
        "\nNormal samples by noise level:"
    )

    normal_rows = dataframe[
        dataframe["attack_type"] == "normal"
    ]

    normal_noise_counts = (
        normal_rows[
            "noise_rate"
        ]
        .value_counts()
        .sort_index()
    )

    for noise_rate in NOISE_LEVELS:

        count = int(
            normal_noise_counts.get(
                noise_rate,
                0,
            )
        )

        status = (
            "OK"
            if count > 0
            else "MISSING"
        )

        print(
            f"  {noise_rate:.3f}: "
            f"{count:4d} samples "
            f"[{status}]"
        )

    # -----------------------------------------------------
    # Final validation
    # -----------------------------------------------------

    missing_noise_levels = [
        noise_rate
        for noise_rate in NOISE_LEVELS
        if (
            normal_noise_counts.get(
                noise_rate,
                0,
            )
            == 0
        )
    ]

    if missing_noise_levels:

        print(
            "\nWARNING:"
        )

        print(
            "Normal samples are missing for:"
        )

        print(
            missing_noise_levels
        )

        print(
            "Noise-aware baseline calibration "
            "will not be valid for these levels."
        )

    else:

        print(
            "\nSUCCESS:"
        )

        print(
            "Normal samples exist at ALL six "
            "noise levels."
        )

        print(
            "The dataset is ready for the "
            "noise-aware calibration experiment."
        )


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":

    main()