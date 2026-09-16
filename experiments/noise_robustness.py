import os
import sys

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

CIRCUIT_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "benchmarks",
    "bell_n4.qasm"
)

OUTPUT_PATH = os.path.join(
    PROJECT_ROOT,
    "experiments",
    "noise_robustness_results.csv"
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
# CREATE ATTACK VARIANTS
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
# MAIN EXPERIMENT
# ---------------------------------------------------------

def main():

    print(
        "=== QShield Noise Robustness Experiment ==="
    )

    print(
        "\nTraining Gradient Boosting model..."
    )

    model = train_model()

    print(
        "Model trained successfully."
    )

    print(
        "\nLoading benchmark circuit..."
    )

    circuit = load_qasm_circuit(
        CIRCUIT_PATH
    )

    print(
        f"Circuit: "
        f"{os.path.basename(CIRCUIT_PATH)}"
    )

    print(
        f"Qubits: {circuit.num_qubits}"
    )

    print(
        f"Depth: {circuit.depth()}"
    )

    print(
        f"Total gates: {circuit.size()}"
    )


    # -----------------------------------------------------
    # IDEAL REFERENCE
    # -----------------------------------------------------

    print(
        "\nGenerating ideal reference..."
    )

    ideal_counts = run_circuit(
        circuit
    )


    # -----------------------------------------------------
    # ATTACK VARIANTS
    # -----------------------------------------------------

    variants = create_variants(
        circuit
    )


    results = []


    # -----------------------------------------------------
    # NOISE LOOP
    # -----------------------------------------------------

    for noise_rate in NOISE_LEVELS:

        print(
            f"\n----------------------------------------"
        )

        print(
            f"Noise Level: {noise_rate}"
        )

        print(
            f"----------------------------------------"
        )

        noise_model = create_noise_model(
            noise_rate
        )


        # -------------------------------------------------
        # ATTACK LOOP
        # -------------------------------------------------

        for attack_type, variant in (
            variants.items()
        ):

            observed_counts = run_circuit(
                variant,
                noise_model
            )

            tvd = calculate_tvd(
                ideal_counts,
                observed_counts
            )


            # ---------------------------------------------
            # Feature extraction
            # ---------------------------------------------

            features = extract_features(
                variant
            )

            features["tvd"] = tvd

            features["noise_rate"] = noise_rate


            input_data = pd.DataFrame(
                [features]
            )

            input_data = input_data[
                FEATURES
            ]


            # ---------------------------------------------
            # Prediction
            # ---------------------------------------------

            prediction = model.predict(
                input_data
            )[0]

            probability = model.predict_proba(
                input_data
            )[0][1]


            if prediction == 1:

                status = "ANOMALOUS"

            else:

                status = "NORMAL"


            risk_score = round(
                probability * 100,
                2
            )


            # ---------------------------------------------
            # Expected label
            # ---------------------------------------------

            if attack_type == "Normal":

                expected_label = 0

            else:

                expected_label = 1


            # ---------------------------------------------
            # Correct detection
            # ---------------------------------------------

            correct = (
                prediction == expected_label
            )


            results.append({

                "noise_rate":
                    noise_rate,

                "attack_type":
                    attack_type,

                "tvd":
                    round(
                        tvd,
                        4
                    ),

                "risk_score":
                    risk_score,

                "status":
                    status,

                "expected_label":
                    expected_label,

                "predicted_label":
                    int(prediction),

                "correct":
                    correct

            })


            print(
                f"{attack_type:<25}"
                f"TVD={tvd:.4f}  "
                f"Risk={risk_score:6.2f}  "
                f"{status}"
            )


    # -----------------------------------------------------
    # SAVE RAW RESULTS
    # -----------------------------------------------------

    results_df = pd.DataFrame(
        results
    )

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
    # FINAL RESULTS
    # -----------------------------------------------------

    print(
        "\n\n========================================"
    )

    print(
        "NOISE ROBUSTNESS RESULTS"
    )

    print(
        "========================================"
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
    # PERFORMANCE BY NOISE
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
    # PERFORMANCE BY ATTACK
    # -----------------------------------------------------

    print(
        "\n=== Detection by Attack Type ==="
    )

    for attack_type in variants:

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


    print(
        "\nResults saved to:"
    )

    print(
        OUTPUT_PATH
    )

    print(
        "\n=== Experiment completed ==="
    )


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":

    main()