import os
import sys

import pandas as pd

from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

from sklearn.ensemble import RandomForestClassifier


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

from quantum.qasm_loader import load_qasm_circuit
from quantum.feature_extractor import extract_features

from security.attack_generator import (
    gate_insertion,
    gate_deletion,
    gate_substitution,
    multiple_gate_insertion
)


# ---------------------------------------------------------
# CONFIGURATION
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

SHOTS = 200

NOISE_LEVELS = [
    0.005,
    0.01,
    0.02
]


# ---------------------------------------------------------
# MODEL FEATURES
# ---------------------------------------------------------

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
# LOAD DATASET
# ---------------------------------------------------------

def load_dataset():
    """
    Load the QShield training dataset.
    """

    return pd.read_csv(
        DATASET_PATH
    )


# ---------------------------------------------------------
# TRAIN RANDOM FOREST MODEL
# ---------------------------------------------------------

def train_model():
    """
    Train the QShield Random Forest anomaly detector.
    """

    df = load_dataset()

    X = df[FEATURES]

    y = df["label"]

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    )

    model.fit(
        X,
        y
    )

    return model


# ---------------------------------------------------------
# CREATE NOISE MODEL
# ---------------------------------------------------------

def create_noise_model(
    error_rate
):
    """
    Create a depolarizing noise model.

    Single-qubit gates:
        error_rate

    Two-qubit gates:
        2 * error_rate
    """

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
    """
    Execute a quantum circuit using Aer.
    """

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
    """
    Normalize measurement keys by removing
    spaces between classical registers.
    """

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
# CALCULATE TVD
# ---------------------------------------------------------

def calculate_tvd(
    reference_counts,
    observed_counts
):
    """
    Calculate Total Variation Distance (TVD)
    between two measurement distributions.
    """

    reference_counts = normalize_counts(
        reference_counts
    )

    observed_counts = normalize_counts(
        observed_counts
    )

    reference_total = sum(
        reference_counts.values()
    )

    observed_total = sum(
        observed_counts.values()
    )

    if reference_total == 0 or observed_total == 0:
        return 0.0

    reference_distribution = {
        state: count / reference_total
        for state, count
        in reference_counts.items()
    }

    observed_distribution = {
        state: count / observed_total
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
            0.0
        )

        q = observed_distribution.get(
            state,
            0.0
        )

        difference += abs(
            p - q
        )

    return difference / 2.0


# ---------------------------------------------------------
# CREATE ATTACK VARIANTS
# ---------------------------------------------------------

def create_variants(
    circuit
):
    """
    Generate the standard QShield attack variants.
    """

    variants = {

        "Normal":
            circuit.copy(),

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

    return variants


# ---------------------------------------------------------
# CALCULATE RISK LEVEL
# ---------------------------------------------------------

def get_risk_level(
    risk_score
):
    """
    Convert numerical risk score into
    LOW / MEDIUM / HIGH.
    """

    if risk_score < 30:

        return "LOW"

    elif risk_score < 70:

        return "MEDIUM"

    else:

        return "HIGH"


# ---------------------------------------------------------
# NOISE-AWARE TVD BASELINE
# ---------------------------------------------------------

def calculate_noise_tvd_baseline(
    noise_rate
):
    """
    Calculate the expected TVD for normal
    circuits at the selected noise level.

    The baseline is obtained from normal
    samples in the QShield dataset.
    """

    df = load_dataset()

    normal_samples = df[
        (df["label"] == 0)
        &
        (
            df["noise_rate"].round(6)
            ==
            round(noise_rate, 6)
        )
    ]

    if normal_samples.empty:

        return 0.0

    baseline = normal_samples["tvd"].mean()

    return float(
        baseline
    )


# ---------------------------------------------------------
# CALCULATE EXCESS TVD
# ---------------------------------------------------------

def calculate_tvd_excess(
    observed_tvd,
    noise_baseline
):
    """
    Calculate behavioral deviation beyond
    the expected normal noise behavior.
    """

    excess = (
        observed_tvd
        - noise_baseline
    )

    return max(
        0.0,
        excess
    )


# ---------------------------------------------------------
# CALIBRATE RISK SCORE
# ---------------------------------------------------------

def calibrate_risk_score(
    anomaly_probability,
    observed_tvd,
    noise_baseline
):
    """
    Combine ML anomaly probability with
    behavioral deviation beyond normal noise.

    70%:
        ML anomaly probability

    30%:
        Excess TVD signal
    """

    excess_tvd = calculate_tvd_excess(
        observed_tvd,
        noise_baseline
    )

    tvd_signal = min(
        excess_tvd / 0.5,
        1.0
    )

    calibrated_probability = (
        0.7 * anomaly_probability
        +
        0.3 * tvd_signal
    )

    calibrated_probability = min(
        max(
            calibrated_probability,
            0.0
        ),
        1.0
    )

    return calibrated_probability


# ---------------------------------------------------------
# ANALYZE ONE CIRCUIT VARIANT
# ---------------------------------------------------------

def analyze_variant(
    model,
    original_circuit,
    variant_circuit,
    attack_type,
    noise_rate
):
    """
    Analyze one circuit variant under a
    specified noise level.
    """

    # -----------------------------------------------------
    # IDEAL REFERENCE EXECUTION
    # -----------------------------------------------------

    ideal_counts = run_circuit(
        original_circuit
    )

    # -----------------------------------------------------
    # CREATE NOISE MODEL
    # -----------------------------------------------------

    noise_model = create_noise_model(
        noise_rate
    )

    # -----------------------------------------------------
    # EXECUTE VARIANT UNDER NOISE
    # -----------------------------------------------------

    observed_counts = run_circuit(
        variant_circuit,
        noise_model
    )

    # -----------------------------------------------------
    # CALCULATE TVD
    # -----------------------------------------------------

    tvd = calculate_tvd(
        ideal_counts,
        observed_counts
    )

    # -----------------------------------------------------
    # EXTRACT CIRCUIT FEATURES
    # -----------------------------------------------------

    features = extract_features(
        variant_circuit
    )

    features["tvd"] = tvd

    features["noise_rate"] = noise_rate

    # -----------------------------------------------------
    # PREPARE MODEL INPUT
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
    # NOISE-AWARE CALIBRATION
    # -----------------------------------------------------

    noise_baseline = calculate_noise_tvd_baseline(
        noise_rate
    )

    excess_tvd = calculate_tvd_excess(
        tvd,
        noise_baseline
    )

    calibrated_probability = calibrate_risk_score(
        anomaly_probability,
        tvd,
        noise_baseline
    )

    # -----------------------------------------------------
    # FINAL RISK SCORE
    # -----------------------------------------------------

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
    # RETURN RESULT
    # -----------------------------------------------------

    return {

        "attack_type":
            attack_type,

        "noise_rate":
            noise_rate,

        "status":
            status,

        "risk_level":
            risk_level,

        "risk_score":
            risk_score,

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

        "tvd":
            round(
                tvd,
                4
            ),

        "num_qubits":
            variant_circuit.num_qubits,

        "depth":
            variant_circuit.depth(),

        "total_gates":
            variant_circuit.size()
    }


# ---------------------------------------------------------
# MAIN TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    print(
        "=== QShield Attack-Aware "
        "Security Detector ==="
    )

    # -----------------------------------------------------
    # TRAIN MODEL
    # -----------------------------------------------------

    print(
        "\nLoading dataset..."
    )

    model = train_model()

    print(
        "Random Forest model trained."
    )

    # -----------------------------------------------------
    # LOAD CIRCUIT
    # -----------------------------------------------------

    print(
        "\nLoading quantum circuit:"
    )

    print(
        CIRCUIT_PATH
    )

    original_circuit = load_qasm_circuit(
        CIRCUIT_PATH
    )

    # -----------------------------------------------------
    # CREATE VARIANTS
    # -----------------------------------------------------

    variants = create_variants(
        original_circuit
    )

    # -----------------------------------------------------
    # RUN EVALUATION
    # -----------------------------------------------------

    all_results = []

    for noise_rate in NOISE_LEVELS:

        print(
            "\n========================================"
        )

        print(
            f"NOISE LEVEL: {noise_rate}"
        )

        print(
            "========================================"
        )

        for attack_type, variant_circuit in (
            variants.items()
        ):

            result = analyze_variant(
                model,
                original_circuit,
                variant_circuit,
                attack_type,
                noise_rate
            )

            all_results.append(
                result
            )

            print(
                f"\n{attack_type}"
            )

            print(
                f"  Status: "
                f"{result['status']}"
            )

            print(
                f"  Risk Level: "
                f"{result['risk_level']}"
            )

            print(
                f"  Risk Score: "
                f"{result['risk_score']}/100"
            )

            print(
                f"  ML Anomaly Probability: "
                f"{result['anomaly_probability']}%"
            )

            print(
                f"  Normal Probability: "
                f"{result['normal_probability']}%"
            )

            print(
                f"  Noise TVD Baseline: "
                f"{result['noise_tvd_baseline']}"
            )

            print(
                f"  Excess TVD: "
                f"{result['excess_tvd']}"
            )

            print(
                f"  Calibrated Probability: "
                f"{result['calibrated_probability']}%"
            )

            print(
                f"  Observed TVD: "
                f"{result['tvd']}"
            )

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    results_df = pd.DataFrame(
        all_results
    )

    print(
        "\n\n========================================"
    )

    print(
        "QSHIELD SECURITY SUMMARY"
    )

    print(
        "========================================"
    )

    print(
        results_df[
            [
                "attack_type",
                "noise_rate",
                "status",
                "risk_level",
                "risk_score",
                "anomaly_probability",
                "noise_tvd_baseline",
                "excess_tvd",
                "calibrated_probability",
                "tvd"
            ]
        ].to_string(
            index=False
        )
    )

    print(
        "\n=== QShield analysis completed ==="
    )