import io

import pandas as pd
from fastapi import FastAPI, File, Form, UploadFile

from qiskit import qasm2

from quantum.feature_extractor import extract_features

from security.attack_generator import (
    gate_insertion,
    gate_deletion,
    gate_substitution,
    multiple_gate_insertion,
)

from ml.qshield_detector import (
    train_model,
    run_circuit,
    calculate_tvd,
    create_noise_model,
    calculate_noise_tvd_baseline,
    calculate_tvd_excess,
    calibrate_risk_score,
    SHOTS,
    FEATURES,
    get_risk_level,
)


# =========================================================
# QShield Simulation Safety Limits
# =========================================================

# These are application-level limits for the current
# local simulation environment.
#
# They are NOT universal limits of quantum computing.
#
# They are used to prevent extremely large circuits from
# causing excessive simulator memory consumption.

MAX_QUBITS = 20
MAX_GATES = 10000
MAX_DEPTH = 5000


# =========================================================
# Circuit Safety Validation
# =========================================================

def validate_circuit_for_simulation(circuit):
    """
    Validate whether a parsed quantum circuit is suitable
    for the current QShield local simulation environment.

    Returns:
        dict:
            valid  -> True/False
            message -> explanation
    """

    num_qubits = circuit.num_qubits
    total_gates = circuit.size()
    depth = circuit.depth()

    # -----------------------------------------------------
    # Qubit limit
    # -----------------------------------------------------

    if num_qubits > MAX_QUBITS:
        return {
            "valid": False,
            "error_type": "qubit_limit",
            "message": (
                f"Circuit contains {num_qubits} qubits. "
                f"QShield currently supports up to "
                f"{MAX_QUBITS} qubits for local simulation."
            ),
        }

    # -----------------------------------------------------
    # Gate limit
    # -----------------------------------------------------

    if total_gates > MAX_GATES:
        return {
            "valid": False,
            "error_type": "gate_limit",
            "message": (
                f"Circuit contains {total_gates} gates. "
                f"QShield currently supports up to "
                f"{MAX_GATES} gates."
            ),
        }

    # -----------------------------------------------------
    # Circuit depth limit
    # -----------------------------------------------------

    if depth > MAX_DEPTH:
        return {
            "valid": False,
            "error_type": "depth_limit",
            "message": (
                f"Circuit depth is {depth}. "
                f"QShield currently supports a maximum "
                f"depth of {MAX_DEPTH}."
            ),
        }

    # -----------------------------------------------------
    # Circuit passed
    # -----------------------------------------------------

    return {
        "valid": True,
        "error_type": None,
        "message": "Circuit passed simulation safety checks.",
    }


# =========================================================
# QShield FastAPI Application
# =========================================================

app = FastAPI(
    title="QShield API",
    description=(
        "AI-Powered Cybersecurity Framework "
        "for Quantum Computing Workloads"
    ),
    version="1.0.0",
)


# =========================================================
# Load ML Model
# =========================================================

print("Loading QShield ML model...")

try:

    MODEL = train_model()

    print("Random Forest model loaded successfully.")

except Exception as e:

    MODEL = None

    print(f"ML model loading failed: {e}")


# =========================================================
# Root
# =========================================================

@app.get("/")
def root():

    return {
        "project": "QShield",
        "status": "running",
        "message": "Quantum Security Analysis API",
    }


# =========================================================
# Health
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "QShield API",
        "ml_model": (
            "Random Forest"
            if MODEL is not None
            else "unavailable"
        ),
        "simulation_limits": {
            "max_qubits": MAX_QUBITS,
            "max_gates": MAX_GATES,
            "max_depth": MAX_DEPTH,
        },
    }


# =========================================================
# Analyze Uploaded QASM
# =========================================================

@app.post("/analyze")
async def analyze_circuit(
    file: UploadFile = File(...),
    attack_type: str = Form("normal"),
    noise_rate: float = Form(0.01),
):

    # -----------------------------------------------------
    # Validate file
    # -----------------------------------------------------

    if not file.filename:

        return {
            "status": "error",
            "error_type": "file",
            "message": "No file was provided.",
        }

    if not file.filename.lower().endswith(".qasm"):

        return {
            "status": "error",
            "error_type": "file",
            "message": "Please upload a .qasm file.",
        }

    # -----------------------------------------------------
    # Validate noise
    # -----------------------------------------------------

    if not 0 <= noise_rate <= 1:

        return {
            "status": "error",
            "error_type": "noise_rate",
            "message": "noise_rate must be between 0 and 1.",
        }

    # -----------------------------------------------------
    # Check model
    # -----------------------------------------------------

    if MODEL is None:

        return {
            "status": "error",
            "error_type": "model",
            "message": "ML model is not available.",
        }

    # -----------------------------------------------------
    # Read uploaded file
    # -----------------------------------------------------

    try:

        file_bytes = await file.read()

        qasm_text = file_bytes.decode("utf-8")

    except UnicodeDecodeError:

        return {
            "status": "error",
            "error_type": "file_encoding",
            "message": (
                "The uploaded QASM file is not valid UTF-8 text."
            ),
        }

    except Exception as e:

        return {
            "status": "error",
            "error_type": "file_read",
            "message": (
                f"Could not read QASM file: {str(e)}"
            ),
        }

    # -----------------------------------------------------
    # Check empty file
    # -----------------------------------------------------

    if not qasm_text.strip():

        return {
            "status": "error",
            "error_type": "empty_file",
            "message": "The uploaded QASM file is empty.",
        }

    # -----------------------------------------------------
    # Load QASM from uploaded content
    # -----------------------------------------------------

    try:

        qasm_stream = io.StringIO(qasm_text)

        original_circuit = qasm2.loads(
            qasm_stream.read()
        )

    except Exception as e:

        return {
            "status": "error",
            "error_type": "qasm_parse",
            "message": (
                f"Could not parse QASM file: {str(e)}"
            ),
        }

    # -----------------------------------------------------
    # Circuit Safety Check
    # -----------------------------------------------------

    safety_check = validate_circuit_for_simulation(
        original_circuit
    )

    if not safety_check["valid"]:

        return {
            "status": "error",
            "error_type": "circuit_safety",
            "reason": safety_check["error_type"],
            "message": safety_check["message"],
            "file": file.filename,
            "circuit": {
                "num_qubits": original_circuit.num_qubits,
                "depth": original_circuit.depth(),
                "total_gates": original_circuit.size(),
            },
            "simulation_limits": {
                "max_qubits": MAX_QUBITS,
                "max_gates": MAX_GATES,
                "max_depth": MAX_DEPTH,
            },
        }

    # -----------------------------------------------------
    # Original features
    # -----------------------------------------------------

    try:

        original_features = extract_features(
            original_circuit
        )

    except Exception as e:

        return {
            "status": "error",
            "error_type": "feature_extraction",
            "message": (
                f"Feature extraction failed: {str(e)}"
            ),
        }

    # -----------------------------------------------------
    # Select attack
    # -----------------------------------------------------

    attack = attack_type.lower().strip()

    try:

        if attack == "normal":

            variant_circuit = original_circuit.copy()

        elif attack == "gate_insertion":

            variant_circuit = gate_insertion(
                original_circuit
            )

        elif attack == "gate_deletion":

            variant_circuit = gate_deletion(
                original_circuit
            )

        elif attack == "gate_substitution":

            variant_circuit = gate_substitution(
                original_circuit
            )

        elif attack == "multiple_gate_insertion":

            variant_circuit = multiple_gate_insertion(
                original_circuit,
                number_of_gates=2,
            )

        else:

            return {
                "status": "error",
                "error_type": "attack_type",
                "message": (
                    "Unknown attack type. Use: "
                    "normal, gate_insertion, "
                    "gate_deletion, gate_substitution, "
                    "multiple_gate_insertion"
                ),
            }

    except Exception as e:

        return {
            "status": "error",
            "error_type": "attack_generation",
            "message": (
                f"Attack generation failed: {str(e)}"
            ),
        }

    # -----------------------------------------------------
    # Validate modified circuit
    # -----------------------------------------------------

    modified_safety_check = validate_circuit_for_simulation(
        variant_circuit
    )

    if not modified_safety_check["valid"]:

        return {
            "status": "error",
            "error_type": "modified_circuit_safety",
            "reason": modified_safety_check["error_type"],
            "message": (
                "The generated attack variant exceeds "
                "the QShield simulation limits."
            ),
            "details": modified_safety_check["message"],
            "circuit": {
                "num_qubits": variant_circuit.num_qubits,
                "depth": variant_circuit.depth(),
                "total_gates": variant_circuit.size(),
            },
            "simulation_limits": {
                "max_qubits": MAX_QUBITS,
                "max_gates": MAX_GATES,
                "max_depth": MAX_DEPTH,
            },
        }

    # -----------------------------------------------------
    # Ideal simulation
    # -----------------------------------------------------

    try:

        ideal_counts = run_circuit(
            original_circuit
        )

    except Exception as e:

        return {
            "status": "error",
            "error_type": "ideal_simulation",
            "message": (
                "The circuit could not be simulated in "
                "the current QShield environment."
            ),
            "details": str(e),
        }

    # -----------------------------------------------------
    # Create noise model
    # -----------------------------------------------------

    try:

        noise_model = create_noise_model(
            noise_rate
        )

    except Exception as e:

        return {
            "status": "error",
            "error_type": "noise_model",
            "message": (
                f"Noise model creation failed: {str(e)}"
            ),
        }

    # -----------------------------------------------------
    # Noisy simulation
    # -----------------------------------------------------

    try:

        observed_counts = run_circuit(
            variant_circuit,
            noise_model,
        )

    except Exception as e:

        return {
            "status": "error",
            "error_type": "quantum_simulation",
            "message": (
                "The quantum circuit could not be "
                "simulated safely by the current backend."
            ),
            "details": str(e),
        }

    # -----------------------------------------------------
    # TVD
    # -----------------------------------------------------

    try:

        tvd = calculate_tvd(
            ideal_counts,
            observed_counts,
        )

    except Exception as e:

        return {
            "status": "error",
            "error_type": "tvd",
            "message": (
                f"TVD calculation failed: {str(e)}"
            ),
        }

    # -----------------------------------------------------
    # Variant features
    # -----------------------------------------------------

    try:

        features = extract_features(
            variant_circuit
        )

        features["tvd"] = tvd

        features["noise_rate"] = noise_rate

    except Exception as e:

        return {
            "status": "error",
            "error_type": "feature_extraction",
            "message": (
                f"Feature extraction failed: {str(e)}"
            ),
        }

    # -----------------------------------------------------
    # ML input
    # -----------------------------------------------------

    try:

        input_data = pd.DataFrame(
            [features]
        )

        input_data = input_data[
            FEATURES
        ]

    except Exception as e:

        return {
            "status": "error",
            "error_type": "ml_input",
            "message": (
                f"ML input preparation failed: {str(e)}"
            ),
        }

    # -----------------------------------------------------
    # Prediction
    # -----------------------------------------------------

    try:

        prediction = MODEL.predict(
            input_data
        )[0]

        probabilities = MODEL.predict_proba(
            input_data
        )[0]

        normal_probability = probabilities[0]

        anomaly_probability = probabilities[1]

    except Exception as e:

        return {
            "status": "error",
            "error_type": "ml_prediction",
            "message": (
                f"ML prediction failed: {str(e)}"
            ),
        }

    # -----------------------------------------------------
    # Noise-aware Risk Calibration
    # -----------------------------------------------------

    try:

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
            noise_baseline,
        )

        risk_score = round(
            calibrated_probability * 100,
            2,
        )

        risk_level = get_risk_level(
            risk_score
        )

    except Exception as e:

        return {
            "status": "error",
            "error_type": "risk_calibration",
            "message": (
                f"Risk calibration failed: {str(e)}"
            ),
        }

    # -----------------------------------------------------
    # Detection
    # -----------------------------------------------------

    detection = (
        "ANOMALOUS"
        if prediction == 1
        else "NORMAL"
    )

    # -----------------------------------------------------
    # Circuit changes
    # -----------------------------------------------------

    depth_change = (
        variant_circuit.depth()
        - original_circuit.depth()
    )

    gate_change = (
        variant_circuit.size()
        - original_circuit.size()
    )

    # -----------------------------------------------------
    # Normalize counts for API response
    # -----------------------------------------------------

    def normalize_counts(counts):

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

    # -----------------------------------------------------
    # Final response
    # -----------------------------------------------------

    return {

        "status": "success",

        "project": "QShield",

        "file": file.filename,

        "analysis": {

            "attack_type": attack,

            "noise_rate": noise_rate,

            "detection": detection,

            "risk_level": risk_level,

            "risk_score": risk_score,

            "ml_model": "Random Forest",

            "anomaly_probability": round(
                anomaly_probability * 100,
                2,
            ),

            "normal_probability": round(
                normal_probability * 100,
                2,
            ),

            "noise_tvd_baseline": round(
                noise_baseline,
                4,
            ),

            "excess_tvd": round(
                excess_tvd,
                4,
            ),

            "calibrated_probability": round(
                calibrated_probability * 100,
                2,
            ),

            "tvd": round(
                tvd,
                4,
            ),
        },

        "original_circuit": {

            "num_qubits":
                original_circuit.num_qubits,

            "depth":
                original_circuit.depth(),

            "total_gates":
                original_circuit.size(),
        },

        "modified_circuit": {

            "num_qubits":
                variant_circuit.num_qubits,

            "depth":
                variant_circuit.depth(),

            "total_gates":
                variant_circuit.size(),
        },

        "circuit_changes": {

            "depth_change":
                depth_change,

            "gate_count_change":
                gate_change,
        },

        "features":
            features,

        "simulation": {

            "shots":
                SHOTS,

            "ideal_counts":
                normalize_counts(
                    ideal_counts
                ),

            "observed_counts":
                normalize_counts(
                    observed_counts
                ),
        },
    }