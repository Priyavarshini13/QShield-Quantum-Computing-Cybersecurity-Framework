import os
import sys
import glob
import random

import pandas as pd

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

from ml.qshield_detector import (
    train_model,
    run_circuit,
    create_noise_model,
    calculate_tvd,
    calculate_noise_tvd_baseline,
    calculate_tvd_excess,
    calibrate_risk_score,
    get_risk_level,
    FEATURES
)


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

BENCHMARK_ROOT = os.path.join(
    PROJECT_ROOT,
    "data",
    "temp_benchmarks",
    "QASMBench-master",
    "small"
)

OUTPUT_DIR = os.path.join(
    PROJECT_ROOT,
    "experiments"
)

PLOTS_DIR = os.path.join(
    OUTPUT_DIR,
    "plots"
)

RESULTS_PATH = os.path.join(
    OUTPUT_DIR,
    "noise_robustness_calibrated_results.csv"
)

SUMMARY_PATH = os.path.join(
    OUTPUT_DIR,
    "noise_robustness_calibrated_summary.csv"
)

SHOTS = 200

NOISE_LEVELS = [
    0.005,
    0.010,
    0.020,
    0.030,
    0.040,
    0.050
]

MAX_CIRCUITS = 30

RANDOM_SEED = 42

random.seed(
    RANDOM_SEED
)


# ---------------------------------------------------------
# ATTACK CONFIGURATION
# ---------------------------------------------------------

ATTACK_TYPES = [
    "Normal",
    "Gate Insertion",
    "Gate Deletion",
    "Gate Substitution",
    "Multiple Gate Insertion"
]


# ---------------------------------------------------------
# FIND BENCHMARK CIRCUITS
# ---------------------------------------------------------

def find_qasm_files():

    pattern = os.path.join(
        BENCHMARK_ROOT,
        "**",
        "*.qasm"
    )

    files = glob.glob(
        pattern,
        recursive=True
    )

    files = sorted(
        files
    )

    return files[:MAX_CIRCUITS]


# ---------------------------------------------------------
# CREATE ATTACK VARIANT
# ---------------------------------------------------------

def create_variant(
    circuit,
    attack_type
):

    if attack_type == "Normal":

        return circuit

    elif attack_type == "Gate Insertion":

        return gate_insertion(
            circuit
        )

    elif attack_type == "Gate Deletion":

        return gate_deletion(
            circuit
        )

    elif attack_type == "Gate Substitution":

        return gate_substitution(
            circuit
        )

    elif attack_type == "Multiple Gate Insertion":

        return multiple_gate_insertion(
            circuit,
            number_of_gates=2
        )

    else:

        raise ValueError(
            f"Unknown attack type: {attack_type}"
        )


# ---------------------------------------------------------
# ANALYZE ONE CIRCUIT
# ---------------------------------------------------------

def analyze_circuit(
    model,
    circuit,
    circuit_name,
    attack_type,
    noise_rate
):

    # -----------------------------------------------------
    # CREATE VARIANT
    # -----------------------------------------------------

    variant_circuit = create_variant(
        circuit,
        attack_type
    )

    # -----------------------------------------------------
    # IDEAL REFERENCE
    # -----------------------------------------------------

    ideal_counts = run_circuit(
        circuit
    )

    # -----------------------------------------------------
    # NOISY EXECUTION
    # -----------------------------------------------------

    noise_model = create_noise_model(
        noise_rate
    )

    observed_counts = run_circuit(
        variant_circuit,
        noise_model
    )

    # -----------------------------------------------------
    # BEHAVIORAL DIFFERENCE
    # -----------------------------------------------------

    tvd = calculate_tvd(
        ideal_counts,
        observed_counts
    )

    # -----------------------------------------------------
    # CIRCUIT FEATURES
    # -----------------------------------------------------

    features = extract_features(
        variant_circuit
    )

    features["tvd"] = tvd

    features["noise_rate"] = noise_rate

    # -----------------------------------------------------
    # MODEL INPUT
    # -----------------------------------------------------

    input_data = pd.DataFrame(
        [features]
    )

    input_data = input_data[
        FEATURES
    ]

    # -----------------------------------------------------
    # ML PREDICTION
    # -----------------------------------------------------

    prediction = model.predict(
        input_data
    )[0]

    probabilities = model.predict_proba(
        input_data
    )[0]

    normal_probability = probabilities[0]

    anomaly_probability = probabilities[1]

    # -----------------------------------------------------
    # NOISE TVD BASELINE
    # -----------------------------------------------------

    noise_baseline = calculate_noise_tvd_baseline(
        noise_rate
    )

    # -----------------------------------------------------
    # EXCESS TVD
    # -----------------------------------------------------

    excess_tvd = calculate_tvd_excess(
        tvd,
        noise_baseline
    )

    # -----------------------------------------------------
    # CALIBRATED RISK
    # -----------------------------------------------------

    calibrated_probability = calibrate_risk_score(
        anomaly_probability,
        tvd,
        noise_baseline
    )

    risk_score = round(
        calibrated_probability * 100,
        2
    )

    risk_level = get_risk_level(
        risk_score
    )

    # -----------------------------------------------------
    # SECURITY STATUS
    # -----------------------------------------------------

    if prediction == 1:

        status = "ANOMALOUS"

    else:

        status = "NORMAL"

    # -----------------------------------------------------
    # EXPECTED LABEL
    # -----------------------------------------------------

    if attack_type == "Normal":

        expected_label = 0

    else:

        expected_label = 1

    # -----------------------------------------------------
    # CORRECTNESS
    # -----------------------------------------------------

    correct_prediction = (
        int(prediction) == expected_label
    )

    # -----------------------------------------------------
    # RESULT
    # -----------------------------------------------------

    return {

        "circuit": circuit_name,

        "attack_type": attack_type,

        "noise_rate": noise_rate,

        "expected_label": expected_label,

        "prediction": int(
            prediction
        ),

        "correct_prediction":
            int(correct_prediction),

        "status": status,

        "risk_level": risk_level,

        "risk_score": risk_score,

        "anomaly_probability":
            round(
                anomaly_probability * 100,
                2
            ),

        "normal_probability":
            round(
                normal_probability * 100,
                2
            ),

        "noise_tvd_baseline":
            round(
                noise_baseline,
                4
            ),

        "observed_tvd":
            round(
                tvd,
                4
            ),

        "excess_tvd":
            round(
                excess_tvd,
                4
            ),

        "calibrated_probability":
            round(
                calibrated_probability * 100,
                2
            ),

        "num_qubits":
            variant_circuit.num_qubits,

        "depth":
            variant_circuit.depth(),

        "total_gates":
            variant_circuit.size()
    }


# ---------------------------------------------------------
# CALCULATE SUMMARY
# ---------------------------------------------------------

def calculate_summary(
    results_df
):

    summary_rows = []

    # -----------------------------------------------------
    # By noise level
    # -----------------------------------------------------

    for noise_rate in NOISE_LEVELS:

        noise_df = results_df[
            results_df["noise_rate"]
            == noise_rate
        ]

        if noise_df.empty:

            continue

        # -------------------------------------------------
        # Normal false-positive rate
        # -------------------------------------------------

        normal_df = noise_df[
            noise_df["attack_type"]
            == "Normal"
        ]

        if not normal_df.empty:

            false_positive_rate = (
                normal_df["prediction"].eq(1).mean()
                * 100
            )

            normal_mean_risk = (
                normal_df["risk_score"].mean()
            )

        else:

            false_positive_rate = 0.0
            normal_mean_risk = 0.0

        # -------------------------------------------------
        # Attack detection
        # -------------------------------------------------

        attack_df = noise_df[
            noise_df["attack_type"]
            != "Normal"
        ]

        if not attack_df.empty:

            overall_attack_detection = (
                attack_df["prediction"].eq(1).mean()
                * 100
            )

        else:

            overall_attack_detection = 0.0

        # -------------------------------------------------
        # Per attack detection
        # -------------------------------------------------

        row = {

            "noise_rate":
                noise_rate,

            "normal_false_positive_rate":
                round(
                    false_positive_rate,
                    2
                ),

            "normal_mean_risk":
                round(
                    normal_mean_risk,
                    2
                ),

            "overall_attack_detection":
                round(
                    overall_attack_detection,
                    2
                )
        }

        for attack_type in ATTACK_TYPES[1:]:

            attack_specific = noise_df[
                noise_df["attack_type"]
                == attack_type
            ]

            if attack_specific.empty:

                detection_rate = 0.0

            else:

                detection_rate = (
                    attack_specific[
                        "prediction"
                    ].eq(1).mean()
                    * 100
                )

            column_name = (
                attack_type
                .lower()
                .replace(
                    " ",
                    "_"
                )
                .replace(
                    "-",
                    "_"
                )
                + "_detection_rate"
            )

            row[column_name] = round(
                detection_rate,
                2
            )

        # -------------------------------------------------
        # Risk and TVD
        # -------------------------------------------------

        row["mean_risk_score"] = round(
            noise_df["risk_score"].mean(),
            2
        )

        row["mean_observed_tvd"] = round(
            noise_df["observed_tvd"].mean(),
            4
        )

        row["mean_excess_tvd"] = round(
            noise_df["excess_tvd"].mean(),
            4
        )

        summary_rows.append(
            row
        )

    return pd.DataFrame(
        summary_rows
    )


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":

    print(
        "\n"
        + "=" * 70
    )

    print(
        "QSHIELD CALIBRATED NOISE ROBUSTNESS EVALUATION"
    )

    print(
        "=" * 70
    )

    print(
        "\nBenchmark directory:"
    )

    print(
        BENCHMARK_ROOT
    )

    # -----------------------------------------------------
    # CREATE OUTPUT DIRECTORIES
    # -----------------------------------------------------

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    os.makedirs(
        PLOTS_DIR,
        exist_ok=True
    )

    # -----------------------------------------------------
    # FIND CIRCUITS
    # -----------------------------------------------------

    qasm_files = find_qasm_files()

    print(
        f"\nQASM circuits found: {len(qasm_files)}"
    )

    if not qasm_files:

        print(
            "\nERROR: No QASM benchmark files found."
        )

        print(
            "Expected path:"
        )

        print(
            BENCHMARK_ROOT
        )

        sys.exit(1)

    # -----------------------------------------------------
    # TRAIN MODEL
    # -----------------------------------------------------

    print(
        "\nTraining Random Forest model..."
    )

    model = train_model()

    print(
        "Random Forest model training complete."
    )
    # -----------------------------------------------------
    # EVALUATION
    # -----------------------------------------------------

    results = []

    successful_runs = 0

    failed_runs = 0

    total_runs = (
        len(qasm_files)
        * len(NOISE_LEVELS)
        * len(ATTACK_TYPES)
    )

    # -----------------------------------------------------
    # CIRCUIT LOOP
    # -----------------------------------------------------

    for index, qasm_path in enumerate(
        qasm_files,
        start=1
    ):

        circuit_name = os.path.basename(
            qasm_path
        )

        print(
            f"\n[{index}/{len(qasm_files)}] "
            f"{circuit_name}"
        )

        try:

            circuit = load_qasm_circuit(
                qasm_path
            )

        except Exception as error:

            print(
                f"  SKIPPED - QASM loading failed: "
                f"{error}"
            )

            failed_runs += (
                len(NOISE_LEVELS)
                * len(ATTACK_TYPES)
            )

            continue

        # -------------------------------------------------
        # NOISE LOOP
        # -------------------------------------------------

        for noise_rate in NOISE_LEVELS:

            print(
                f"  Noise = {noise_rate}"
            )

            # ---------------------------------------------
            # ATTACK LOOP
            # ---------------------------------------------

            for attack_type in ATTACK_TYPES:

                try:

                    result = analyze_circuit(
                        model,
                        circuit,
                        circuit_name,
                        attack_type,
                        noise_rate
                    )

                    results.append(
                        result
                    )

                    successful_runs += 1

                except Exception as error:

                    failed_runs += 1

                    print(
                        f"    {attack_type}: "
                        f"FAILED - {error}"
                    )

    # -----------------------------------------------------
    # RESULTS DATAFRAME
    # -----------------------------------------------------

    results_df = pd.DataFrame(
        results
    )

    # -----------------------------------------------------
    # SAVE RESULTS
    # -----------------------------------------------------

    results_df.to_csv(
        RESULTS_PATH,
        index=False
    )

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    summary_df = calculate_summary(
        results_df
    )

    summary_df.to_csv(
        SUMMARY_PATH,
        index=False
    )

    # -----------------------------------------------------
    # PRINT SUMMARY
    # -----------------------------------------------------

    print(
        "\n"
        + "=" * 70
    )

    print(
        "EVALUATION COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        f"\nSuccessful evaluation rows : "
        f"{successful_runs}"
    )

    print(
        f"Failed evaluation rows     : "
        f"{failed_runs}"
    )

    print(
        f"Total attempted rows       : "
        f"{total_runs}"
    )

    if not results_df.empty:

        print(
            f"Circuits represented       : "
            f"{results_df['circuit'].nunique()}"
        )

    # -----------------------------------------------------
    # SUMMARY TABLE
    # -----------------------------------------------------

    if not summary_df.empty:

        print(
            "\n"
            + "-" * 70
        )

        print(
            "CALIBRATED NOISE ROBUSTNESS SUMMARY"
        )

        print(
            "-" * 70
        )

        print(
            summary_df.to_string(
                index=False
            )
        )

    # -----------------------------------------------------
    # OVERALL ATTACK PERFORMANCE
    # -----------------------------------------------------

    if not results_df.empty:

        attacks_df = results_df[
            results_df["attack_type"]
            != "Normal"
        ]

        normal_df = results_df[
            results_df["attack_type"]
            == "Normal"
        ]

        if not attacks_df.empty:

            overall_attack_detection = (
                attacks_df[
                    "prediction"
                ].eq(1).mean()
                * 100
            )

        else:

            overall_attack_detection = 0.0

        if not normal_df.empty:

            overall_false_positive_rate = (
                normal_df[
                    "prediction"
                ].eq(1).mean()
                * 100
            )

        else:

            overall_false_positive_rate = 0.0

        print(
            "\n"
            + "-" * 70
        )

        print(
            "OVERALL CALIBRATED PERFORMANCE"
        )

        print(
            "-" * 70
        )

        print(
            f"Attack detection rate : "
            f"{overall_attack_detection:.2f}%"
        )

        print(
            f"False-positive rate   : "
            f"{overall_false_positive_rate:.2f}%"
        )

    # -----------------------------------------------------
    # OUTPUT FILES
    # -----------------------------------------------------

    print(
        "\nResults CSV:"
    )

    print(
        RESULTS_PATH
    )

    print(
        "\nSummary CSV:"
    )

    print(
        SUMMARY_PATH
    )

    print(
        "\n=== QShield calibrated evaluation completed ==="
    )