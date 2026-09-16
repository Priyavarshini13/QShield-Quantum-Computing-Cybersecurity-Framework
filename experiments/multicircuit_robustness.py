import os
import random
import sys
import zipfile

import pandas as pd

from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


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
# QSHIELD MODULES
# ---------------------------------------------------------

from quantum.qasm_loader import load_qasm_circuit
from quantum.feature_extractor import extract_features

from security.attack_generator import (
    gate_insertion,
    gate_deletion,
    gate_substitution,
    multiple_gate_insertion
)


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

DATASET_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "qshield_dataset.csv"
)

ZIP_FILE = os.path.join(
    PROJECT_ROOT,
    "QASMBench-master.zip"
)

OUTPUT_PATH = os.path.join(
    PROJECT_ROOT,
    "experiments",
    "multicircuit_robustness_results.csv"
)


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

SHOTS = 200

NOISE_LEVELS = [
    0.005,
    0.01,
    0.02,
    0.03,
    0.04,
    0.05
]

MAX_QUBITS = 12

random.seed(42)


FEATURES = [
    "num_qubits",
    "depth",
    "total_gates",
    "h_gates",
    "x_gates",
    "y_gates",
    "z_gates",
    "cx_gates",
    "cz_gates",
    "rx_gates",
    "ry_gates",
    "rz_gates",
    "measurement_gates",
    "barriers",
    "tvd",
    "noise_rate"
]


# ---------------------------------------------------------
# TRAIN MODEL
# ---------------------------------------------------------

def train_model():

    print(
        "\nTraining Gradient Boosting model..."
    )

    df = pd.read_csv(
        DATASET_PATH
    )

    X = df[FEATURES]

    y = df["label"]

    model = GradientBoostingClassifier(
        n_estimators=150,
        learning_rate=0.05,
        max_depth=3,
        random_state=42
    )

    model.fit(
        X,
        y
    )

    print(
        "Model trained successfully."
    )

    return model


# ---------------------------------------------------------
# NOISE MODEL
# ---------------------------------------------------------

def create_noise_model(
    error_rate
):

    noise_model = NoiseModel()

    single_qubit_error = depolarizing_error(
        error_rate,
        1
    )

    two_qubit_error = depolarizing_error(
        error_rate * 2,
        2
    )

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
            "u3"
        ]
    )

    noise_model.add_all_qubit_quantum_error(
        two_qubit_error,
        [
            "cx",
            "cz"
        ]
    )

    return noise_model


# ---------------------------------------------------------
# RUN CIRCUIT
# ---------------------------------------------------------

def run_circuit(
    circuit,
    noise_model=None
):

    if noise_model is None:

        simulator = AerSimulator()

    else:

        simulator = AerSimulator(
            noise_model=noise_model
        )

    result = simulator.run(
        circuit,
        shots=SHOTS
    ).result()

    return result.get_counts()


# ---------------------------------------------------------
# NORMALIZE COUNTS
# ---------------------------------------------------------

def normalize_counts(
    counts
):

    normalized = {}

    for state, count in counts.items():

        clean_state = state.replace(
            " ",
            ""
        )

        normalized[clean_state] = (
            normalized.get(
                clean_state,
                0
            )
            + count
        )

    return normalized


# ---------------------------------------------------------
# TVD
# ---------------------------------------------------------

def calculate_tvd(
    reference_counts,
    observed_counts
):

    reference_counts = normalize_counts(
        reference_counts
    )

    observed_counts = normalize_counts(
        observed_counts
    )

    reference_distribution = {
        state: count / SHOTS
        for state, count
        in reference_counts.items()
    }

    observed_distribution = {
        state: count / SHOTS
        for state, count
        in observed_counts.items()
    }

    all_states = (
        set(reference_distribution)
        |
        set(observed_distribution)
    )

    difference = 0.0

    for state in all_states:

        p = reference_distribution.get(
            state,
            0
        )

        q = observed_distribution.get(
            state,
            0
        )

        difference += abs(
            p - q
        )

    return difference / 2


# ---------------------------------------------------------
# CREATE VARIANTS
# ---------------------------------------------------------

def create_variants(
    circuit
):

    return {

        "Normal": circuit,

        "Gate Insertion":
            gate_insertion(circuit),

        "Gate Deletion":
            gate_deletion(circuit),

        "Gate Substitution":
            gate_substitution(circuit),

        "Multiple Gate Insertion":
            multiple_gate_insertion(
                circuit,
                number_of_gates=2
            )
    }


# ---------------------------------------------------------
# PROCESS ONE CIRCUIT
# ---------------------------------------------------------

def process_circuit(
    circuit,
    circuit_name,
    model
):

    results = []

    print(
        f"\nProcessing: "
        f"{circuit_name} "
        f"({circuit.num_qubits} qubits)"
    )

    # -----------------------------------------------------
    # Ideal reference
    # -----------------------------------------------------

    ideal_counts = run_circuit(
        circuit
    )

    # -----------------------------------------------------
    # Create attack variants
    # -----------------------------------------------------

    variants = create_variants(
        circuit
    )

    # -----------------------------------------------------
    # Noise levels
    # -----------------------------------------------------

    for noise_rate in NOISE_LEVELS:

        noise_model = create_noise_model(
            noise_rate
        )

        for attack_type, variant in (
            variants.items()
        ):

            try:

                # -----------------------------------------
                # Execute noisy variant
                # -----------------------------------------

                observed_counts = run_circuit(
                    variant,
                    noise_model
                )

                # -----------------------------------------
                # TVD
                # -----------------------------------------

                tvd = calculate_tvd(
                    ideal_counts,
                    observed_counts
                )

                # -----------------------------------------
                # Features
                # -----------------------------------------

                features = extract_features(
                    variant
                )

                features["tvd"] = tvd

                features["noise_rate"] = (
                    noise_rate
                )

                # -----------------------------------------
                # Model input
                # -----------------------------------------

                input_data = pd.DataFrame(
                    [features]
                )

                input_data = input_data[
                    FEATURES
                ]

                # -----------------------------------------
                # Prediction
                # -----------------------------------------

                prediction = model.predict(
                    input_data
                )[0]

                probability = model.predict_proba(
                    input_data
                )[0][1]

                # -----------------------------------------
                # Expected label
                # -----------------------------------------

                if attack_type == "Normal":

                    expected_label = 0

                else:

                    expected_label = 1

                # -----------------------------------------
                # Result
                # -----------------------------------------

                results.append({

                    "circuit_name":
                        circuit_name,

                    "num_qubits":
                        circuit.num_qubits,

                    "attack_type":
                        attack_type,

                    "noise_rate":
                        noise_rate,

                    "tvd":
                        round(
                            tvd,
                            4
                        ),

                    "risk_score":
                        round(
                            probability * 100,
                            2
                        ),

                    "expected_label":
                        expected_label,

                    "predicted_label":
                        int(prediction),

                    "correct":
                        prediction
                        == expected_label

                })

            except Exception as error:

                print(
                    f"  Skipped "
                    f"{attack_type} "
                    f"at noise "
                    f"{noise_rate}: "
                    f"{error}"
                )

    return results


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print(
        "=== QShield Multi-Circuit "
        "Noise Robustness Experiment ==="
    )

    # -----------------------------------------------------
    # Train model
    # -----------------------------------------------------

    model = train_model()

    # -----------------------------------------------------
    # Check ZIP
    # -----------------------------------------------------

    if not os.path.exists(
        ZIP_FILE
    ):

        print(
            "\nERROR: "
            "QASMBench ZIP not found."
        )

        print(
            ZIP_FILE
        )

        return

    all_results = []

    usable_circuits = 0

    skipped_circuits = 0


    # -----------------------------------------------------
    # Open QASMBench
    # -----------------------------------------------------

    with zipfile.ZipFile(
        ZIP_FILE,
        "r"
    ) as archive:

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


        # -------------------------------------------------
        # Temporary directory
        # -------------------------------------------------

        temp_dir = os.path.join(
            PROJECT_ROOT,
            "data",
            "temp_benchmarks"
        )

        os.makedirs(
            temp_dir,
            exist_ok=True
        )


        # -------------------------------------------------
        # Process circuits
        # -------------------------------------------------

        for qasm_file in qasm_files:

            try:

                archive.extract(
                    qasm_file,
                    temp_dir
                )

                extracted_path = os.path.join(
                    temp_dir,
                    qasm_file
                )

                circuit = load_qasm_circuit(
                    extracted_path
                )


                # -----------------------------------------
                # Circuit filtering
                # -----------------------------------------

                if circuit.num_qubits < 2:

                    skipped_circuits += 1

                    continue


                if circuit.num_qubits > MAX_QUBITS:

                    print(
                        f"\nSkipping "
                        f"{os.path.basename(qasm_file)} "
                        f"because it has "
                        f"{circuit.num_qubits} qubits."
                    )

                    skipped_circuits += 1

                    continue


                # -----------------------------------------
                # Process
                # -----------------------------------------

                circuit_name = os.path.basename(
                    qasm_file
                )

                rows = process_circuit(
                    circuit,
                    circuit_name,
                    model
                )

                all_results.extend(
                    rows
                )

                usable_circuits += 1


            except Exception as error:

                skipped_circuits += 1

                print(
                    f"\nSkipped circuit:"
                )

                print(
                    qasm_file
                )

                print(
                    f"Reason: {error}"
                )


    # -----------------------------------------------------
    # CHECK RESULTS
    # -----------------------------------------------------

    if not all_results:

        print(
            "\nNo results generated."
        )

        return


    results_df = pd.DataFrame(
        all_results
    )


    # -----------------------------------------------------
    # SAVE RESULTS
    # -----------------------------------------------------

    results_df.to_csv(
        OUTPUT_PATH,
        index=False
    )


    # -----------------------------------------------------
    # OVERALL METRICS
    # -----------------------------------------------------

    y_true = results_df[
        "expected_label"
    ]

    y_pred = results_df[
        "predicted_label"
    ]


    accuracy = accuracy_score(
        y_true,
        y_pred
    )

    precision = precision_score(
        y_true,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_true,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_true,
        y_pred,
        zero_division=0
    )


    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    print(
        "\n========================================"
    )

    print(
        "MULTI-CIRCUIT ROBUSTNESS RESULTS"
    )

    print(
        "========================================"
    )

    print(
        f"\nUsable circuits: "
        f"{usable_circuits}"
    )

    print(
        f"Skipped circuits: "
        f"{skipped_circuits}"
    )

    print(
        f"Total evaluations: "
        f"{len(results_df)}"
    )

    print(
        f"\nOverall Accuracy : "
        f"{accuracy:.4f}"
    )

    print(
        f"Overall Precision: "
        f"{precision:.4f}"
    )

    print(
        f"Overall Recall   : "
        f"{recall:.4f}"
    )

    print(
        f"Overall F1       : "
        f"{f1:.4f}"
    )


    # -----------------------------------------------------
    # NOISE PERFORMANCE
    # -----------------------------------------------------

    print(
        "\n=== Performance by Noise Level ==="
    )

    for noise_rate in NOISE_LEVELS:

        subset = results_df[
            results_df["noise_rate"]
            == noise_rate
        ]

        noise_accuracy = accuracy_score(
            subset["expected_label"],
            subset["predicted_label"]
        )

        noise_f1 = f1_score(
            subset["expected_label"],
            subset["predicted_label"],
            zero_division=0
        )

        print(
            f"Noise {noise_rate:.3f}  "
            f"Accuracy={noise_accuracy:.4f}  "
            f"F1={noise_f1:.4f}"
        )


    # -----------------------------------------------------
    # ATTACK PERFORMANCE
    # -----------------------------------------------------

    print(
        "\n=== Detection by Attack Type ==="
    )

    attack_types = [
        "Normal",
        "Gate Insertion",
        "Gate Deletion",
        "Gate Substitution",
        "Multiple Gate Insertion"
    ]

    for attack_type in attack_types:

        subset = results_df[
            results_df["attack_type"]
            == attack_type
        ]

        detection_rate = (
            subset["correct"].mean()
        )

        print(
            f"{attack_type:<25}"
            f"{detection_rate * 100:.2f}%"
        )


    # -----------------------------------------------------
    # CIRCUIT PERFORMANCE
    # -----------------------------------------------------

    print(
        "\n=== Performance by Circuit ==="
    )

    circuit_summary = (
        results_df
        .groupby("circuit_name")
        ["correct"]
        .mean()
        .sort_values()
    )

    for circuit_name, score in (
        circuit_summary.items()
    ):

        print(
            f"{circuit_name:<30}"
            f"{score * 100:.2f}%"
        )


    # -----------------------------------------------------
    # SAVE SUMMARY
    # -----------------------------------------------------

    summary_path = os.path.join(
        PROJECT_ROOT,
        "experiments",
        "multicircuit_summary.csv"
    )

    summary_df = pd.DataFrame({

        "metric": [
            "usable_circuits",
            "skipped_circuits",
            "total_evaluations",
            "accuracy",
            "precision",
            "recall",
            "f1"
        ],

        "value": [
            usable_circuits,
            skipped_circuits,
            len(results_df),
            accuracy,
            precision,
            recall,
            f1
        ]

    })

    summary_df.to_csv(
        summary_path,
        index=False
    )


    print(
        "\nResults saved to:"
    )

    print(
        OUTPUT_PATH
    )

    print(
        "\nSummary saved to:"
    )

    print(
        summary_path
    )

    print(
        "\n=== Experiment completed ==="
    )


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":

    main()