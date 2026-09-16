import os
import sys
import pandas as pd


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
# QSHIELD MODULES
# ---------------------------------------------------------

from quantum.feature_extractor import extract_features

from security.attack_generator import apply_attack

from ml.qshield_detector import (
    train_model,
    create_noise_model,
    calculate_tvd,
    calculate_noise_tvd_baseline,
    calculate_tvd_excess,
    calibrate_risk_score
)

from qiskit_aer import AerSimulator


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

SHOTS = 200

NOISE_LEVELS = [
    0.005,
    0.02,
    0.05
]

ATTACKS = [
    "normal",
    "gate_insertion",
    "gate_deletion",
    "gate_substitution",
    "multiple_gate_insertion"
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
# RUN CIRCUIT
# ---------------------------------------------------------

def run_circuit(
    circuit,
    noise_rate=0.0
):
    """
    Execute a quantum circuit with optional
    depolarizing noise.
    """

    if noise_rate == 0:

        simulator = AerSimulator()

    else:

        noise_model = create_noise_model(
            noise_rate
        )

        simulator = AerSimulator(
            noise_model=noise_model
        )

    result = simulator.run(
        circuit,
        shots=SHOTS
    ).result()

    return result.get_counts()


# ---------------------------------------------------------
# CREATE ATTACKED CIRCUIT
# ---------------------------------------------------------

def create_attacked_circuit(
    circuit,
    attack
):
    """
    Create the requested security variant.
    """

    if attack == "normal":

        return circuit.copy()

    return apply_attack(
        circuit,
        attack
    )


# ---------------------------------------------------------
# ANALYZE ONE VARIANT
# ---------------------------------------------------------

def analyze_variant(
    model,
    original_circuit,
    variant_circuit,
    algorithm_name,
    attack,
    noise_rate
):
    """
    Analyze one quantum circuit variant.
    """

    # -----------------------------------------------------
    # IDEAL REFERENCE
    # -----------------------------------------------------

    ideal_counts = run_circuit(
        original_circuit,
        noise_rate=0.0
    )

    # -----------------------------------------------------
    # NOISY EXECUTION
    # -----------------------------------------------------

    observed_counts = run_circuit(
        variant_circuit,
        noise_rate=noise_rate
    )

    # -----------------------------------------------------
    # TVD
    # -----------------------------------------------------

    tvd = calculate_tvd(
        ideal_counts,
        observed_counts
    )

    # -----------------------------------------------------
    # FEATURES
    # -----------------------------------------------------

    features = extract_features(
        variant_circuit
    )

    features["tvd"] = tvd
    features["noise_rate"] = noise_rate

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
    # NOISE BASELINE
    # -----------------------------------------------------

    noise_baseline = (
        calculate_noise_tvd_baseline(
            noise_rate
        )
    )

    excess_tvd = calculate_tvd_excess(
        tvd,
        noise_baseline
    )

    # -----------------------------------------------------
    # CALIBRATED RISK
    # -----------------------------------------------------

    calibrated_probability = (
        calibrate_risk_score(
            anomaly_probability,
            tvd,
            noise_baseline
        )
    )

    risk_score = (
        calibrated_probability * 100
    )

    # -----------------------------------------------------
    # RISK LEVEL
    # -----------------------------------------------------

    if risk_score < 30:

        risk_level = "LOW"

    elif risk_score < 70:

        risk_level = "MEDIUM"

    else:

        risk_level = "HIGH"

    # -----------------------------------------------------
    # SECURITY STATUS
    # -----------------------------------------------------

    if prediction == 1:

        status = "ANOMALOUS"

    else:

        status = "NORMAL"

    # -----------------------------------------------------
    # RETURN RESULT
    # -----------------------------------------------------

    return {

        "algorithm":
            algorithm_name,

        "num_qubits":
            original_circuit.num_qubits,

        "attack":
            attack,

        "noise_rate":
            noise_rate,

        "status":
            status,

        "risk_level":
            risk_level,

        "risk_score":
            round(
                risk_score,
                2
            ),

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

        "tvd":
            round(
                tvd,
                4
            ),

        "noise_tvd_baseline":
            round(
                noise_baseline,
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

        "original_gates":
            original_circuit.size(),

        "attacked_gates":
            variant_circuit.size(),

        "original_depth":
            original_circuit.depth(),

        "attacked_depth":
            variant_circuit.depth()
    }


# ---------------------------------------------------------
# RUN COMPLETE SECURITY EVALUATION
# ---------------------------------------------------------

def evaluate_algorithm(
    circuit,
    algorithm_name,
    output_filename
):
    """
    Run QShield security evaluation for
    any quantum algorithm.
    """

    print(
        "\n"
        + "=" * 70
    )

    print(
        f"QSHIELD - {algorithm_name.upper()} "
        "SECURITY EVALUATION"
    )

    print(
        "=" * 70
    )

    print(
        f"\nAlgorithm: {algorithm_name}"
    )

    print(
        f"Qubits: {circuit.num_qubits}"
    )

    print(
        f"Gates: {circuit.size()}"
    )

    print(
        f"Shots: {SHOTS}"
    )

    print(
        f"Noise levels: {NOISE_LEVELS}"
    )

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
    # RESULTS
    # -----------------------------------------------------

    results = []

    # -----------------------------------------------------
    # NOISE LOOP
    # -----------------------------------------------------

    for noise_rate in NOISE_LEVELS:

        print(
            "\n"
            + "=" * 70
        )

        print(
            f"NOISE LEVEL: {noise_rate}"
        )

        print(
            "=" * 70
        )

        baseline = (
            calculate_noise_tvd_baseline(
                noise_rate
            )
        )

        print(
            f"Normal-noise TVD baseline: "
            f"{baseline:.4f}"
        )

        # -------------------------------------------------
        # ATTACK LOOP
        # -------------------------------------------------

        for attack in ATTACKS:

            print(
                "\n"
                + "-" * 60
            )

            print(
                f"Attack: {attack}"
            )

            print(
                "-" * 60
            )

            try:

                variant = (
                    create_attacked_circuit(
                        circuit,
                        attack
                    )
                )

                result = analyze_variant(
                    model,
                    circuit,
                    variant,
                    algorithm_name,
                    attack,
                    noise_rate
                )

                results.append(
                    result
                )

                print(
                    f"Status: "
                    f"{result['status']}"
                )

                print(
                    f"Risk Level: "
                    f"{result['risk_level']}"
                )

                print(
                    f"Risk Score: "
                    f"{result['risk_score']}/100"
                )

                print(
                    f"Anomaly Probability: "
                    f"{result['anomaly_probability']}%"
                )

                print(
                    f"TVD: "
                    f"{result['tvd']}"
                )

                print(
                    f"Excess TVD: "
                    f"{result['excess_tvd']}"
                )

                print(
                    f"Gates: "
                    f"{result['original_gates']} "
                    f"→ "
                    f"{result['attacked_gates']}"
                )

            except Exception as error:

                print(
                    f"ERROR: {error}"
                )

    # -----------------------------------------------------
    # SAVE RESULTS
    # -----------------------------------------------------

    results_df = pd.DataFrame(
        results
    )

    output_path = os.path.join(
        PROJECT_ROOT,
        "experiments",
        output_filename
    )

    results_df.to_csv(
        output_path,
        index=False
    )

    # -----------------------------------------------------
    # FINAL SUMMARY
    # -----------------------------------------------------

    print(
        "\n"
        + "=" * 70
    )

    print(
        f"{algorithm_name.upper()} "
        "SECURITY EVALUATION COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        f"\nResults saved to:"
    )

    print(
        output_path
    )

    if not results_df.empty:

        print(
            "\nSummary:"
        )

        print(
            results_df[
                [
                    "algorithm",
                    "attack",
                    "noise_rate",
                    "status",
                    "risk_level",
                    "risk_score",
                    "tvd"
                ]
            ].to_string(
                index=False
            )
        )

    return results_df


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":

    print(
        "This module provides the reusable "
        "QShield algorithm security framework."
    )

    print(
        "\nIt is imported by individual "
        "algorithm experiments."
    )