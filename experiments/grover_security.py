import os
import sys

# ============================================================
# WINDOWS UTF-8 FIX
# ============================================================

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


import pandas as pd


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(
        0,
        PROJECT_ROOT
    )


# ============================================================
# QSHIELD MODULES
# ============================================================

from quantum.algorithms.grover import (
    create_grover_circuit
)

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

from quantum.feature_extractor import (
    extract_features
)


# ============================================================
# CONFIGURATION
# ============================================================

TARGET_STATE = "11"

SHOTS = 200

NOISE_LEVELS = [
    0.005,
    0.020,
    0.050
]

ATTACK_TYPES = [
    "Normal",
    "Gate Insertion",
    "Gate Deletion",
    "Gate Substitution",
    "Multiple Gate Insertion"
]


# ============================================================
# CREATE ATTACK VARIANT
# ============================================================

def create_variant(
    circuit,
    attack_type
):

    if attack_type == "Normal":

        return circuit

    if attack_type == "Gate Insertion":

        return gate_insertion(
            circuit
        )

    if attack_type == "Gate Deletion":

        return gate_deletion(
            circuit
        )

    if attack_type == "Gate Substitution":

        return gate_substitution(
            circuit
        )

    if attack_type == "Multiple Gate Insertion":

        return multiple_gate_insertion(
            circuit,
            number_of_gates=2
        )

    raise ValueError(
        f"Unknown attack type: {attack_type}"
    )


# ============================================================
# TARGET PROBABILITY
# ============================================================

def calculate_target_probability(
    counts,
    target_state
):

    total_shots = sum(
        counts.values()
    )

    if total_shots == 0:
        return 0.0

    return (
        counts.get(
            target_state,
            0
        )
        / total_shots
    )


# ============================================================
# ANALYZE ONE VARIANT
# ============================================================

def analyze_variant(
    model,
    original_circuit,
    attack_type,
    noise_rate
):

    # --------------------------------------------------------
    # Create variant
    # --------------------------------------------------------

    variant_circuit = create_variant(
        original_circuit,
        attack_type
    )

    # --------------------------------------------------------
    # Ideal reference
    # --------------------------------------------------------

    ideal_counts = run_circuit(
        original_circuit
    )

    # --------------------------------------------------------
    # Noise model
    # --------------------------------------------------------

    noise_model = create_noise_model(
        noise_rate
    )

    # --------------------------------------------------------
    # Execute variant
    # --------------------------------------------------------

    observed_counts = run_circuit(
        variant_circuit,
        noise_model
    )

    # --------------------------------------------------------
    # TVD
    # --------------------------------------------------------

    tvd = calculate_tvd(
        ideal_counts,
        observed_counts
    )

    # --------------------------------------------------------
    # Grover success probability
    # --------------------------------------------------------

    target_probability = (
        calculate_target_probability(
            observed_counts,
            TARGET_STATE
        )
    )

    # --------------------------------------------------------
    # Feature extraction
    # --------------------------------------------------------

    features = extract_features(
        variant_circuit
    )

    features["tvd"] = tvd
    features["noise_rate"] = noise_rate

    # --------------------------------------------------------
    # ML input
    # --------------------------------------------------------

    input_data = pd.DataFrame(
        [features]
    )

    input_data = input_data[
        FEATURES
    ]

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    prediction = model.predict(
        input_data
    )[0]

    probabilities = model.predict_proba(
        input_data
    )[0]

    normal_probability = probabilities[0]
    anomaly_probability = probabilities[1]

    # --------------------------------------------------------
    # Noise baseline
    # --------------------------------------------------------

    noise_baseline = (
        calculate_noise_tvd_baseline(
            noise_rate
        )
    )

    # --------------------------------------------------------
    # Excess TVD
    # --------------------------------------------------------

    excess_tvd = calculate_tvd_excess(
        tvd,
        noise_baseline
    )

    # --------------------------------------------------------
    # Calibrated risk
    # --------------------------------------------------------

    calibrated_probability = (
        calibrate_risk_score(
            anomaly_probability,
            tvd,
            noise_baseline
        )
    )

    risk_score = round(
        calibrated_probability * 100,
        2
    )

    risk_level = get_risk_level(
        risk_score
    )

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    status = (
        "ANOMALOUS"
        if prediction == 1
        else "NORMAL"
    )

    # --------------------------------------------------------
    # Expected label
    # --------------------------------------------------------

    expected_label = (
        0
        if attack_type == "Normal"
        else 1
    )

    correct_prediction = int(
        int(prediction)
        == expected_label
    )

    # --------------------------------------------------------
    # Gate statistics
    # --------------------------------------------------------

    original_gates = (
        original_circuit.size()
    )

    modified_gates = (
        variant_circuit.size()
    )

    gate_difference = (
        modified_gates
        - original_gates
    )

    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {

        "algorithm":
            "Grover",

        "target_state":
            TARGET_STATE,

        "attack_type":
            attack_type,

        "noise_rate":
            noise_rate,

        "expected_label":
            expected_label,

        "prediction":
            int(prediction),

        "correct_prediction":
            correct_prediction,

        "status":
            status,

        "risk_level":
            risk_level,

        "risk_score":
            risk_score,

        "normal_probability":
            round(
                normal_probability * 100,
                2
            ),

        "anomaly_probability":
            round(
                anomaly_probability * 100,
                2
            ),

        "grover_success_probability":
            round(
                target_probability * 100,
                2
            ),

        "observed_tvd":
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
            original_gates,

        "modified_gates":
            modified_gates,

        "gate_difference":
            gate_difference
    }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print(
        "QSHIELD - GROVER SECURITY EVALUATION"
    )
    print("=" * 70)

    print()
    print(
        f"Target state: |{TARGET_STATE}>"
    )

    print(
        f"Shots: {SHOTS}"
    )

    print(
        f"Noise levels: {NOISE_LEVELS}"
    )

    # --------------------------------------------------------
    # Create circuit
    # --------------------------------------------------------

    print()
    print(
        "Creating Grover circuit..."
    )

    original_circuit = (
        create_grover_circuit(
            TARGET_STATE
        )
    )

    print()
    print(
        "Original Grover circuit:"
    )

    print(
        original_circuit.draw(
            output="text"
        )
    )

    # --------------------------------------------------------
    # Train model
    # --------------------------------------------------------

    print()
    print(
        "Training Gradient Boosting model..."
    )

    model = train_model()

    print(
        "Gradient Boosting model ready."
    )

    # --------------------------------------------------------
    # Run evaluation
    # --------------------------------------------------------

    results = []

    total_tests = (
        len(NOISE_LEVELS)
        * len(ATTACK_TYPES)
    )

    completed_tests = 0

    for noise_rate in NOISE_LEVELS:

        print()
        print("-" * 70)
        print(
            f"NOISE LEVEL: {noise_rate}"
        )
        print("-" * 70)

        for attack_type in ATTACK_TYPES:

            completed_tests += 1

            print()
            print(
                f"[{completed_tests}/{total_tests}] "
                f"{attack_type}"
            )

            try:

                result = analyze_variant(
                    model,
                    original_circuit,
                    attack_type,
                    noise_rate
                )

                results.append(
                    result
                )

                print(
                    f"  Status: "
                    f"{result['status']}"
                )

                print(
                    f"  Risk: "
                    f"{result['risk_score']}/100 "
                    f"({result['risk_level']})"
                )

                print(
                    f"  Grover success: "
                    f"{result['grover_success_probability']}%"
                )

                print(
                    f"  ML anomaly probability: "
                    f"{result['anomaly_probability']}%"
                )

                print(
                    f"  TVD: "
                    f"{result['observed_tvd']}"
                )

                print(
                    f"  Excess TVD: "
                    f"{result['excess_tvd']}"
                )

                print(
                    f"  Gates: "
                    f"{result['original_gates']} -> "
                    f"{result['modified_gates']}"
                )

            except Exception as error:

                print(
                    f"  FAILED: "
                    f"{type(error).__name__}: "
                    f"{error}"
                )

    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------

    results_df = pd.DataFrame(
        results
    )

    output_path = os.path.join(
        PROJECT_ROOT,
        "experiments",
        "grover_security_results.csv"
    )

    results_df.to_csv(
        output_path,
        index=False
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "GROVER SECURITY EVALUATION COMPLETE"
    )
    print("=" * 70)

    if results_df.empty:

        print()
        print(
            "No successful evaluations."
        )

    else:

        print()

        summary_columns = [
            "attack_type",
            "noise_rate",
            "status",
            "risk_level",
            "risk_score",
            "grover_success_probability",
            "anomaly_probability",
            "observed_tvd"
        ]

        print(
            results_df[
                summary_columns
            ].to_string(
                index=False
            )
        )

        # ----------------------------------------------------
        # Attack detection
        # ----------------------------------------------------

        attack_results = results_df[
            results_df["attack_type"]
            != "Normal"
        ]

        normal_results = results_df[
            results_df["attack_type"]
            == "Normal"
        ]

        if not attack_results.empty:

            attack_detection = (
                attack_results[
                    "prediction"
                ].eq(1).mean()
                * 100
            )

        else:

            attack_detection = 0.0

        if not normal_results.empty:

            false_positive_rate = (
                normal_results[
                    "prediction"
                ].eq(1).mean()
                * 100
            )

        else:

            false_positive_rate = 0.0

        print()
        print("-" * 70)
        print(
            "GROVER SECURITY SUMMARY"
        )
        print("-" * 70)

        print(
            f"Attack detection rate : "
            f"{attack_detection:.2f}%"
        )

        print(
            f"False-positive rate   : "
            f"{false_positive_rate:.2f}%"
        )

        print()
        print(
            "Results saved to:"
        )

        print(
            output_path
        )

    print()
    print(
        "=== Grover security experiment completed ==="
    )