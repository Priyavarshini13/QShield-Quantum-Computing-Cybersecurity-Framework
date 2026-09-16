import sys
from pathlib import Path

import pandas as pd
from qiskit import qasm2
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# ============================================================
# QASMBench PATH
# ============================================================


QASMBENCH_ROOT = (
    PROJECT_ROOT
    / "data"
    / "temp_benchmarks"
    / "QASMBench-master"
)

# Main benchmark folder
QASMBENCH_SMALL = QASMBENCH_ROOT / "small"

# Fallback in case your QASMBench structure is different
DATA_BENCHMARKS = PROJECT_ROOT / "data" / "benchmarks"

# ============================================================
# OUTPUT
# ============================================================

OUTPUT_DIR = PROJECT_ROOT / "experiments"

OUTPUT_FILE = (
    OUTPUT_DIR / "security_evaluation_results.csv"
)

# ============================================================
# SETTINGS
# ============================================================

SHOTS = 200

NOISE_RATE = 0.01

MAX_CIRCUITS = 30

# ============================================================
# IMPORT QSHIELD MODULES
# ============================================================

sys.path.insert(0, str(PROJECT_ROOT))

from security.attack_generator import (
    gate_insertion,
    gate_deletion,
    gate_substitution,
    multiple_gate_insertion,
)

from quantum.feature_extractor import extract_features

from quantum.behavior_comparator import calculate_tvd

from ml.qshield_detector import (
    train_model,
    FEATURES,
)


# ============================================================
# ATTACK TYPES
# ============================================================

ATTACKS = {
    "normal": None,
    "gate_insertion": gate_insertion,
    "gate_deletion": gate_deletion,
    "gate_substitution": gate_substitution,
    "multiple_gate_insertion": multiple_gate_insertion,
}


# ============================================================
# FIND QASM CIRCUITS
# ============================================================

def find_qasm_files():
    """
    Automatically find QASM circuits from QASMBench small/.

    Falls back to data/benchmarks/ if QASMBench is not found.
    """

    if QASMBENCH_SMALL.exists():

        files = list(
            QASMBENCH_SMALL.rglob("*.qasm")
        )

        print(
            f"Using QASMBench small directory:"
        )

        print(
            f"  {QASMBENCH_SMALL}"
        )

    elif QASMBENCH_ROOT.exists():

        files = list(
            QASMBENCH_ROOT.rglob("*.qasm")
        )

        print(
            "QASMBench small/ directory not found."
        )

        print(
            "Searching entire QASMBench-master directory."
        )

    else:

        files = list(
            DATA_BENCHMARKS.rglob("*.qasm")
        )

        print(
            "QASMBench-master not found."
        )

        print(
            "Using data/benchmarks instead."
        )

    files = sorted(files)

    # Remove duplicates
    unique_files = []

    seen = set()

    for file in files:

        absolute_path = file.resolve()

        if absolute_path not in seen:

            seen.add(absolute_path)

            unique_files.append(file)

    return unique_files[:MAX_CIRCUITS]


# ============================================================
# NOISE MODEL
# ============================================================

def create_noise_model(error_rate):

    noise_model = NoiseModel()

    single_qubit_error = depolarizing_error(
        error_rate,
        1,
    )

    two_qubit_error = depolarizing_error(
        min(error_rate * 2, 1.0),
        2,
    )

    # Single-qubit gates
    noise_model.add_all_qubit_quantum_error(
        single_qubit_error,
        [
            "x",
            "y",
            "z",
            "h",
            "rx",
            "ry",
            "rz",
        ],
    )

    # Two-qubit gates
    noise_model.add_all_qubit_quantum_error(
        two_qubit_error,
        [
            "cx",
            "cz",
        ],
    )

    return noise_model


# ============================================================
# RUN CIRCUIT
# ============================================================

def run_circuit(
    circuit,
    noise_model=None,
):

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


# ============================================================
# EXTRACT FEATURE VECTOR
# ============================================================

def prepare_features(circuit, tvd):

    features = extract_features(circuit)

    features["tvd"] = tvd

    # IMPORTANT:
    # Return a DataFrame so sklearn keeps feature names.
    feature_vector = pd.DataFrame(
        [
            {
                feature: features.get(
                    feature,
                    0,
                )
                for feature in FEATURES
            }
        ],
        columns=FEATURES,
    )

    return feature_vector, features


# ============================================================
# EVALUATE ONE CIRCUIT
# ============================================================

def evaluate_circuit(
    circuit_path,
    attack_name,
    attack_function,
    model,
    noise_model,
):

    print(
        f"  → {circuit_path.name} | {attack_name}"
    )

    # --------------------------------------------------------
    # LOAD ORIGINAL CIRCUIT
    # --------------------------------------------------------

    original = qasm2.load(
        str(circuit_path)
    )

    # --------------------------------------------------------
    # APPLY ATTACK
    # --------------------------------------------------------

    if attack_function is None:

        modified = original.copy()

    else:

        modified = attack_function(
            original.copy()
        )

    # --------------------------------------------------------
    # IDEAL EXECUTION
    # --------------------------------------------------------

    ideal_counts = run_circuit(
        original
    )

    # --------------------------------------------------------
    # NOISY EXECUTION
    # --------------------------------------------------------

    observed_counts = run_circuit(
        modified,
        noise_model,
    )

    # --------------------------------------------------------
    # TVD
    # --------------------------------------------------------

    tvd = calculate_tvd(
        ideal_counts,
        observed_counts,
        SHOTS,
    )

    # --------------------------------------------------------
    # FEATURES
    # --------------------------------------------------------

    feature_vector, features = prepare_features(
        modified,
        tvd,
    )

    # --------------------------------------------------------
    # ML PREDICTION
    # --------------------------------------------------------

    prediction = model.predict(
        feature_vector
    )[0]

    probabilities = model.predict_proba(
        feature_vector
    )[0]

    classes = list(
        model.classes_
    )

    if 1 in classes:

        anomaly_probability = probabilities[
            classes.index(1)
        ]

    else:

        anomaly_probability = 0.0

    # --------------------------------------------------------
    # RISK SCORE
    # --------------------------------------------------------

    risk_score = (
        float(anomaly_probability)
        * 100
    )

    # --------------------------------------------------------
    # RISK LEVEL
    # --------------------------------------------------------

    if risk_score < 30:

        risk_level = "LOW"

    elif risk_score < 70:

        risk_level = "MEDIUM"

    else:

        risk_level = "HIGH"

    # --------------------------------------------------------
    # CIRCUIT INFORMATION
    # --------------------------------------------------------

    original_qubits = (
        original.num_qubits
    )

    original_depth = (
        original.depth()
    )

    modified_depth = (
        modified.depth()
    )

    original_gates = (
        len(original.data)
    )

    modified_gates = (
        len(modified.data)
    )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    return {
        "circuit": circuit_path.name,

        "attack_type": attack_name,

        "noise_rate": NOISE_RATE,

        "num_qubits": original_qubits,

        "original_depth": original_depth,

        "modified_depth": modified_depth,

        "original_gates": original_gates,

        "modified_gates": modified_gates,

        "tvd": round(
            float(tvd),
            4,
        ),

        "prediction": int(
            prediction
        ),

        "anomaly_probability": round(
            float(anomaly_probability),
            4,
        ),

        "risk_score": round(
            risk_score,
            2,
        ),

        "risk_level": risk_level,

        "status": "SUCCESS",
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("QSHIELD SECURITY EVALUATION")
    print("=" * 70)
    print()

    # --------------------------------------------------------
    # OUTPUT DIRECTORY
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # FIND CIRCUITS
    # --------------------------------------------------------

    circuits = find_qasm_files()

    print()

    print(
        f"Found {len(circuits)} QASM circuits."
    )

    print()

    if not circuits:

        print(
            "ERROR: No QASM circuits found."
        )

        print()

        print(
            "Check that QASMBench-master exists inside:"
        )

        print(
            PROJECT_ROOT
        )

        return

    # --------------------------------------------------------
    # TRAIN MODEL
    # --------------------------------------------------------

    print(
        "Training QShield ML model..."
    )

    model = train_model()

    print(
        "Model trained successfully."
    )

    print()

    # --------------------------------------------------------
    # CREATE NOISE
    # --------------------------------------------------------

    noise_model = create_noise_model(
        NOISE_RATE
    )

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    results = []

    success_count = 0

    failed_count = 0

    # --------------------------------------------------------
    # EVALUATE EACH CIRCUIT
    # --------------------------------------------------------

    for index, circuit_path in enumerate(
        circuits,
        start=1,
    ):

        print(
            f"[{index}/{len(circuits)}] "
            f"{circuit_path.name}"
        )

        for attack_name, attack_function in ATTACKS.items():

            try:

                result = evaluate_circuit(
                    circuit_path,
                    attack_name,
                    attack_function,
                    model,
                    noise_model,
                )

                results.append(result)

                success_count += 1

            except Exception as error:

                print(
                    f"    ⚠ Skipped: {error}"
                )

                failed_count += 1

                results.append(
                    {
                        "circuit": circuit_path.name,
                        "attack_type": attack_name,
                        "noise_rate": NOISE_RATE,
                        "num_qubits": "Not evaluated",
                        "original_depth": "Not evaluated",
                        "modified_depth": "Not evaluated",
                        "original_gates": "Not evaluated",
                        "modified_gates": "Not evaluated",
                        "tvd": "Not evaluated",
                        "prediction": "Not evaluated",
                        "anomaly_probability": "Not evaluated",
                        "risk_score": "Not evaluated",
                        "risk_level": "Not evaluated",
                        "status": f"FAILED: {error}",
                    }
                )

        print()

    # --------------------------------------------------------
    # SAVE CSV
    # --------------------------------------------------------

    dataframe = pd.DataFrame(
        results
    )

    dataframe.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    successful_results = dataframe[
        dataframe["status"] == "SUCCESS"
    ]

    print("=" * 70)
    print("EVALUATION COMPLETE")
    print("=" * 70)
    print()

    print(
        f"Circuits tested : {len(circuits)}"
    )

    print(
        f"Successful runs : {success_count}"
    )

    print(
        f"Failed runs     : {failed_count}"
    )

    print(
        f"Total runs      : {len(results)}"
    )

    print()

    # --------------------------------------------------------
    # ATTACK SUMMARY
    # --------------------------------------------------------

    if not successful_results.empty:

        print(
            "Detection summary:"
        )

        print()

        for attack_name in ATTACKS.keys():

            attack_results = successful_results[
                successful_results["attack_type"]
                == attack_name
            ]

            if len(attack_results) == 0:
                continue

            detected = (
                attack_results["prediction"]
                == 1
            ).sum()

            total = len(
                attack_results
            )

            detection_rate = (
                detected / total * 100
            )

            print(
                f"{attack_name:30}"
                f"{detection_rate:6.2f}% "
                f"({detected}/{total})"
            )

    print()

    # --------------------------------------------------------
    # CSV LOCATION
    # --------------------------------------------------------

    print(
        "Results saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print()


if __name__ == "__main__":

    main()