import os
import sys
import subprocess
import time

import pandas as pd
import streamlit as st


# ============================================================
# PROJECT CONFIGURATION
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


st.set_page_config(
    page_title="QShield",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SAFETY LIMITS
# ============================================================

MAX_QUBITS = 20
MAX_GATES = 10000
MAX_DEPTH = 5000


# ============================================================
# HELPER - RUN PYTHON SCRIPT
# ============================================================

def run_script(
    script_relative_path,
    timeout=300
):

    script_path = os.path.join(
        PROJECT_ROOT,
        script_relative_path
    )

    if not os.path.exists(script_path):

        return (
            "ERROR\n\n"
            f"Script not found:\n"
            f"{script_relative_path}"
        )

    try:

        env = os.environ.copy()

        # Windows UTF-8
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        result = subprocess.run(
            [
                sys.executable,
                script_path
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=timeout
        )

        output = ""

        if result.stdout:
            output += result.stdout

        if result.stderr:
            output += (
                "\n\n--- STDERR ---\n"
                + result.stderr
            )

        if result.returncode != 0:

            return (
                "ERROR\n\n"
                f"Exit code: "
                f"{result.returncode}\n\n"
                f"{output}"
            )

        return (
            output
            if output.strip()
            else "Script completed successfully."
        )

    except subprocess.TimeoutExpired:

        return (
            "ERROR\n\n"
            f"Script timed out after "
            f"{timeout} seconds."
        )

    except Exception as error:

        return (
            "ERROR\n\n"
            f"{type(error).__name__}: "
            f"{error}"
        )


# ============================================================
# DISPLAY SCRIPT OUTPUT
# ============================================================

def show_script_output(output):

    if output.startswith("ERROR"):

        st.error(
            "Execution failed."
        )

        st.code(
            output,
            language="text"
        )

    else:

        st.success(
            "Execution completed."
        )

        st.code(
            output,
            language="text"
        )


# ============================================================
# RISK MESSAGE
# ============================================================

def get_risk_message(
    risk_level
):

    if risk_level == "HIGH":

        return (
            "The circuit shows strong anomalous behavior. "
            "Inspect the workload before executing it on "
            "trusted quantum resources."
        )

    if risk_level == "MEDIUM":

        return (
            "The circuit shows moderate behavioral deviation. "
            "Further inspection is recommended."
        )

    return (
        "The circuit is currently classified as low risk "
        "under the selected simulation conditions."
    )


# ============================================================
# SAFE FILE NAME
# ============================================================

def safe_filename(
    filename
):

    return os.path.basename(
        filename
    )


# ============================================================
# CIRCUIT VALIDATION
# ============================================================

def validate_circuit(
    circuit
):

    try:

        qubits = circuit.num_qubits
        gates = circuit.size()
        depth = circuit.depth()

        if qubits > MAX_QUBITS:

            return (
                False,
                f"Circuit has {qubits} qubits. "
                f"GUI limit: {MAX_QUBITS}."
            )

        if gates > MAX_GATES:

            return (
                False,
                f"Circuit has {gates:,} gates. "
                f"GUI limit: {MAX_GATES:,}."
            )

        if depth > MAX_DEPTH:

            return (
                False,
                f"Circuit depth is {depth:,}. "
                f"GUI limit: {MAX_DEPTH:,}."
            )

        return True, ""

    except Exception as error:

        return (
            False,
            f"Validation failed: {error}"
        )


# ============================================================
# TRAIN MODEL
# ============================================================

@st.cache_resource
def get_qshield_model():

    from ml.qshield_detector import (
        train_model
    )

    return train_model()


# ============================================================
# FEATURE EXTRACTION
# ============================================================

def get_features(
    circuit
):

    from quantum.feature_extractor import (
        extract_features
    )

    return extract_features(
        circuit
    )


# ============================================================
# HEADER
# ============================================================

st.title(
    "🛡️ QShield"
)

st.subheader(
    "AI-Powered Cybersecurity Framework "
    "for Quantum Computing Workloads"
)

st.write(
    """
QShield combines quantum computing, machine learning,
cybersecurity, quantum cryptography, and post-quantum
cryptography into one security research platform.
"""
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "🛡️ QShield"
)

section = st.sidebar.radio(
    "Select Module",
    [
        "🏠 Overview",
        "🛡️ Circuit Security",
        "⚛️ Quantum Algorithms",
        "🔐 BB84 Cryptography",
        "🔒 Post-Quantum Cryptography",
        "⚠️ Quantum Threat Analysis",
        "📊 Research Results"
    ]
)

st.sidebar.divider()

st.sidebar.caption(
    "QShield Research Platform"
)

st.sidebar.caption(
    "Quantum Computing • ML • Cybersecurity • Cryptography"
)


# ============================================================
# OVERVIEW
# ============================================================

if section == "🏠 Overview":

    st.header(
        "🛡️ QShield Security Platform"
    )

    st.write(
        """
QShield analyzes quantum circuits, simulates security
attacks and noise, extracts behavioral features, and
uses machine learning for anomaly detection.
"""
    )

    st.subheader(
        "System Architecture"
    )

    st.code(
        """
Quantum Circuit
      ↓
Circuit Analyzer
      ↓
Feature Extraction
      ↓
Attack / Fault Generation
      ↓
Quantum Simulation
      ↓
ML Anomaly Detection
      ↓
Security Risk Score
      ↓
QShield Dashboard
""",
        language="text"
    )

    st.divider()

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    with col1:

        st.metric(
            "ML Model",
            "Random Forest"
        )

    with col2:

        st.metric(
            "Quantum Algorithms",
            "5"
        )

    with col3:

        st.metric(
            "Quantum Crypto",
            "BB84"
        )

    with col4:

        st.metric(
            "PQC",
            "ML-KEM + ML-DSA"
        )

    st.divider()

    st.subheader(
        "Implemented Components"
    )

    components = pd.DataFrame(
        {
            "Component": [
                "Quantum Circuit Security",
                "ML Anomaly Detection",
                "Attack Simulation",
                "Noise Robustness",
                "Grover",
                "QFT",
                "QPE",
                "QAOA",
                "Shor",
                "BB84",
                "ML-KEM-768",
                "ML-DSA-65",
                "Quantum Threat Analysis"
            ],
            "Status": [
                "Completed"
            ] * 13
        }
    )

    st.dataframe(
        components,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader(
        "Research Question"
    )

    st.info(
        """
Can machine-learning-based behavioral analysis detect
faults and security anomalies in quantum circuits under
different attack and noise conditions?
"""
    )


# ============================================================
# CIRCUIT SECURITY
# ============================================================

elif section == "🛡️ Circuit Security":

    st.header(
        "🛡️ Quantum Circuit Security"
    )

    st.write(
        """
Upload a valid OpenQASM 2 circuit. QShield generates the
selected security condition, simulates it under noise,
calculates TVD, extracts quantum features, and performs
ML anomaly detection.
"""
    )

    st.warning(
        f"""
Local simulation limits:
{MAX_QUBITS} qubits •
{MAX_GATES:,} gates •
{MAX_DEPTH:,} depth
"""
    )

    uploaded_file = st.file_uploader(
        "Upload QASM Circuit",
        type=["qasm"]
    )

    col1, col2 = st.columns(2)

    with col1:

        noise_rate = st.slider(
            "Noise Rate",
            min_value=0.0,
            max_value=0.05,
            value=0.02,
            step=0.005,
            format="%.3f"
        )

    with col2:

        attack = st.selectbox(
            "Security Condition",
            [
                "Normal",
                "Gate Insertion",
                "Gate Deletion",
                "Gate Substitution",
                "Multiple Gate Insertion"
            ]
        )

    if uploaded_file is None:

        st.info(
            "Upload a .qasm file to begin."
        )

    else:

        st.info(
            f"Selected circuit: "
            f"{uploaded_file.name}"
        )

        if st.button(
            "🔍 Analyze Circuit",
            type="primary"
        ):

            temp_directory = os.path.join(
                PROJECT_ROOT,
                "data",
                "temp_benchmarks"
            )

            os.makedirs(
                temp_directory,
                exist_ok=True
            )

            temp_path = os.path.join(
                temp_directory,
                safe_filename(
                    uploaded_file.name
                )
            )

            try:

                # ------------------------------------------------
                # Save uploaded QASM
                # ------------------------------------------------

                with open(
                    temp_path,
                    "wb"
                ) as file:

                    file.write(
                        uploaded_file.getbuffer()
                    )

                # ------------------------------------------------
                # Load circuit
                # ------------------------------------------------

                from quantum.qasm_loader import (
                    load_qasm_circuit
                )

                with st.spinner(
                    "Loading quantum circuit..."
                ):

                    circuit = load_qasm_circuit(
                        temp_path
                    )

                # ------------------------------------------------
                # Validate
                # ------------------------------------------------

                valid, message = (
                    validate_circuit(
                        circuit
                    )
                )

                if not valid:

                    st.error(
                        f"⚠️ Circuit rejected:\n\n"
                        f"{message}"
                    )

                else:

                    # ------------------------------------------------
                    # Circuit information
                    # ------------------------------------------------

                    st.subheader(
                        "Circuit Information"
                    )

                    col1, col2, col3 = (
                        st.columns(3)
                    )

                    with col1:

                        st.metric(
                            "Qubits",
                            circuit.num_qubits
                        )

                    with col2:

                        st.metric(
                            "Depth",
                            circuit.depth()
                        )

                    with col3:

                        st.metric(
                            "Total Gates",
                            circuit.size()
                        )

                    # ------------------------------------------------
                    # Model
                    # ------------------------------------------------

                    with st.spinner(
                        "Loading ML detector..."
                    ):

                        model = (
                            get_qshield_model()
                        )

                    # ------------------------------------------------
                    # Variants
                    # ------------------------------------------------

                    from ml.qshield_detector import (
                        create_variants,
                        analyze_variant
                    )

                    with st.spinner(
                        "Generating security condition..."
                    ):

                        variants = (
                            create_variants(
                                circuit
                            )
                        )

                    if attack not in variants:

                        st.error(
                            "Selected security condition "
                            "could not be generated."
                        )

                    else:

                        selected_variant = (
                            variants[attack]
                        )

                        # ------------------------------------------------
                        # Analysis
                        # ------------------------------------------------

                        with st.spinner(
                            "Running quantum security analysis..."
                        ):

                            result = (
                                analyze_variant(
                                    model,
                                    circuit,
                                    selected_variant,
                                    attack,
                                    noise_rate
                                )
                            )

                        st.success(
                            "✅ Security analysis completed."
                        )

                        st.divider()

                        # ------------------------------------------------
                        # Security metrics
                        # ------------------------------------------------

                        st.subheader(
                            "Security Assessment"
                        )

                        col1, col2, col3, col4 = (
                            st.columns(4)
                        )

                        with col1:

                            st.metric(
                                "Risk Score",
                                f"{result['risk_score']:.2f}/100"
                            )

                        with col2:

                            st.metric(
                                "Anomaly Probability",
                                f"{result['anomaly_probability']:.2f}%"
                            )

                        with col3:

                            st.metric(
                                "TVD",
                                f"{result['tvd']:.4f}"
                            )

                        with col4:

                            st.metric(
                                "Status",
                                result["status"]
                            )

                        # ------------------------------------------------
                        # Risk
                        # ------------------------------------------------

                        risk_level = (
                            result["risk_level"]
                        )

                        if risk_level == "HIGH":

                            st.error(
                                "🚨 HIGH RISK"
                            )

                        elif risk_level == "MEDIUM":

                            st.warning(
                                "⚠️ MEDIUM RISK"
                            )

                        else:

                            st.success(
                                "✅ LOW RISK"
                            )

                        st.write(
                            get_risk_message(
                                risk_level
                            )
                        )

                        st.divider()

                        # ------------------------------------------------
                        # Features
                        # ------------------------------------------------

                        st.subheader(
                            "🔬 Quantum Features"
                        )

                        try:

                            features = (
                                get_features(
                                    selected_variant
                                )
                            )

                            rows = []

                            for key, value in (
                                features.items()
                            ):

                                rows.append(
                                    {
                                        "Feature": key,
                                        "Value": value
                                    }
                                )

                            rows.extend(
                                [
                                    {
                                        "Feature": "TVD",
                                        "Value": result["tvd"]
                                    },
                                    {
                                        "Feature": "Noise Rate",
                                        "Value": noise_rate
                                    }
                                ]
                            )

                            feature_df = (
                                pd.DataFrame(
                                    rows
                                )
                            )

                            st.dataframe(
                                feature_df,
                                use_container_width=True,
                                hide_index=True
                            )

                        except Exception as error:

                            st.warning(
                                f"Feature display failed: "
                                f"{error}"
                            )

                        st.divider()

                        # ------------------------------------------------
                        # Detailed results
                        # ------------------------------------------------

                        st.subheader(
                            "📋 Analysis Details"
                        )

                        details = pd.DataFrame(
                            [
                                {
                                    "Parameter":
                                        "Security Condition",
                                    "Value":
                                        attack
                                },
                                {
                                    "Parameter":
                                        "Noise Rate",
                                    "Value":
                                        f"{noise_rate:.3f}"
                                },
                                {
                                    "Parameter":
                                        "Qubits",
                                    "Value":
                                        result["num_qubits"]
                                },
                                {
                                    "Parameter":
                                        "Circuit Depth",
                                    "Value":
                                        result["depth"]
                                },
                                {
                                    "Parameter":
                                        "Total Gates",
                                    "Value":
                                        result["total_gates"]
                                },
                                {
                                    "Parameter":
                                        "TVD",
                                    "Value":
                                        result["tvd"]
                                },
                                {
                                    "Parameter":
                                        "Noise TVD Baseline",
                                    "Value":
                                        result.get(
                                            "noise_tvd_baseline",
                                            "N/A"
                                        )
                                },
                                {
                                    "Parameter":
                                        "Excess TVD",
                                    "Value":
                                        result.get(
                                            "excess_tvd",
                                            "N/A"
                                        )
                                },
                                {
                                    "Parameter":
                                        "Normal Probability",
                                    "Value":
                                        f"{result['normal_probability']:.2f}%"
                                },
                                {
                                    "Parameter":
                                        "Anomaly Probability",
                                    "Value":
                                        f"{result['anomaly_probability']:.2f}%"
                                },
                                {
                                    "Parameter":
                                        "Risk Level",
                                    "Value":
                                        risk_level
                                }
                            ]
                        )

                        st.dataframe(
                            details,
                            use_container_width=True,
                            hide_index=True
                        )

                        st.divider()

                        # ------------------------------------------------
                        # Interpretation
                        # ------------------------------------------------

                        st.subheader(
                            "🧠 Security Interpretation"
                        )

                        if attack == "Normal":

                            st.info(
                                f"""
Normal circuit selected.

Noise rate:
{noise_rate:.3f}

Anomaly probability:
{result['anomaly_probability']:.2f}%

Risk score:
{result['risk_score']:.2f}/100

TVD:
{result['tvd']:.4f}
"""
                            )

                        else:

                            st.warning(
                                f"""
Security condition:
{attack}

Noise rate:
{noise_rate:.3f}

Anomaly probability:
{result['anomaly_probability']:.2f}%

Risk score:
{result['risk_score']:.2f}/100

TVD:
{result['tvd']:.4f}

The modified workload should be inspected before
execution on trusted quantum resources.
"""
                            )

            except Exception as error:

                st.error(
                    "❌ Circuit analysis failed."
                )

                st.exception(
                    error
                )

            finally:

                try:

                    if os.path.exists(
                        temp_path
                    ):

                        os.remove(
                            temp_path
                        )

                except Exception:

                    pass


# ============================================================
# QUANTUM ALGORITHMS
# ============================================================

elif section == "⚛️ Quantum Algorithms":

    st.header(
        "⚛️ Quantum Algorithm Security"
    )

    st.write(
        """
QShield provides demonstrations and security experiments
for five quantum algorithms.
"""
    )

    algorithm = st.selectbox(
        "Select Quantum Algorithm",
        [
            "Grover",
            "QFT",
            "QPE",
            "QAOA",
            "Shor"
        ]
    )

    descriptions = {

        "Grover":
            "Quantum search using amplitude amplification.",

        "QFT":
            "Quantum Fourier Transform demonstration.",

        "QPE":
            "Quantum Phase Estimation demonstration.",

        "QAOA":
            "QAOA demonstration using a MaxCut problem.",

        "Shor":
            "Educational period-finding demonstration "
            "illustrating the quantum threat to public-key "
            "cryptography."
    }

    st.info(
        descriptions[algorithm]
    )

    files = {

        "Grover": (
            "quantum/algorithms/grover.py",
            "experiments/grover_security.py"
        ),

        "QFT": (
            "quantum/algorithms/qft.py",
            "experiments/qft_security.py"
        ),

        "QPE": (
            "quantum/algorithms/qpe.py",
            "experiments/qpe_security.py"
        ),

        "QAOA": (
            "quantum/algorithms/qaoa.py",
            "experiments/qaoa_security.py"
        ),

        "Shor": (
            "quantum/algorithms/shor.py",
            "experiments/shor_security.py"
        )
    }

    normal_script, security_script = (
        files[algorithm]
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            f"▶ Run {algorithm}",
            type="primary",
            use_container_width=True
        ):

            with st.spinner(
                f"Running {algorithm}..."
            ):

                output = run_script(
                    normal_script
                )

            show_script_output(
                output
            )

    with col2:

        if st.button(
            "🛡️ Security Test",
            use_container_width=True
        ):

            with st.spinner(
                f"Running {algorithm} security test..."
            ):

                output = run_script(
                    security_script,
                    timeout=600
                )

            show_script_output(
                output
            )


# ============================================================
# BB84
# ============================================================

elif section == "🔐 BB84 Cryptography":

    st.header(
        "🔐 BB84 Quantum Key Distribution"
    )

    st.write(
        """
BB84 demonstrates quantum key distribution and
intercept-resend eavesdropping detection using QBER.
"""
    )

    col1, col2 = st.columns(2)

    with col1:

        qubits = st.slider(
            "Number of Qubits",
            16,
            256,
            32,
            16
        )

    with col2:

        scenario = st.selectbox(
            "Scenario",
            [
                "Normal Channel",
                "Intercept-Resend Attack"
            ]
        )

    if st.button(
        "🔐 Run BB84 Analysis",
        type="primary"
    ):

        try:

            from cryptography.bb84 import (
                run_bb84
            )

            use_eve = (
                scenario ==
                "Intercept-Resend Attack"
            )

            with st.spinner(
                "Running BB84..."
            ):

                result = run_bb84(
                    length=qubits,
                    use_eve=use_eve
                )

            if result is None:
                raise RuntimeError(
                    "run_bb84() returned None. "
                    "Please check cryptography/bb84.py."
                )

            if not isinstance(result, dict):
                raise TypeError(
                    f"run_bb84() must return a dictionary, "
                    f"but returned {type(result).__name__}."
                )

            qber = float(result["qber"])

            sifted_key_length = int(
                result["sifted_key_length"]
            )

            status = result.get(
                "status",
                "NORMAL" if qber <= 0.11 else "ANOMALOUS"
            )

            st.success(
                "BB84 execution completed."
            )

            col1, col2, col3 = (
                st.columns(3)
            )

            with col1:

                st.metric(
                    "QBER",
                    f"{qber * 100:.2f}%"
                )

            with col2:

                st.metric(
                    "Sifted Key",
                    sifted_key_length
                )

            with col3:

                st.metric(
                    "Threshold",
                    "11%"
                )

            if qber > 0.11:

                st.error(
                    "🚨 ANOMALOUS — "
                    "Possible eavesdropping detected."
                )

            else:

                st.success(
                    "✅ NORMAL — "
                    "QBER is below threshold."
                )

        except Exception as error:

            st.error(
                "❌ BB84 execution failed."
            )

            st.exception(
                error
            )

    st.divider()

    st.subheader(
        "📊 BB84 Statistical Evaluation"
    )

    path = os.path.join(
        PROJECT_ROOT,
        "experiments",
        "bb84_evaluation_results.csv"
    )

    if os.path.exists(path):

        try:

            df = pd.read_csv(
                path
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        except Exception as error:

            st.warning(
                f"Could not load BB84 results: "
                f"{error}"
            )

    else:

        st.info(
            "BB84 evaluation CSV not found."
        )

    st.subheader(
        "🌐 BB84 Noise Evaluation"
    )

    path = os.path.join(
        PROJECT_ROOT,
        "experiments",
        "bb84_noise_evaluation_results.csv"
    )

    if os.path.exists(path):

        try:

            df = pd.read_csv(
                path
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        except Exception as error:

            st.warning(
                f"Could not load BB84 noise results: "
                f"{error}"
            )

    else:

        st.info(
            "BB84 noise evaluation CSV not found."
        )


# ============================================================
# POST-QUANTUM CRYPTOGRAPHY
# ============================================================

elif section == "🔒 Post-Quantum Cryptography":

    st.header(
        "🔒 Post-Quantum Cryptography"
    )

    st.write(
        """
QShield demonstrates ML-KEM-768 for key encapsulation
and ML-DSA-65 for post-quantum digital signatures.
"""
    )

    tab1, tab2 = st.tabs(
        [
            "🔑 ML-KEM-768",
            "✍️ ML-DSA-65"
        ]
    )

    # ========================================================
    # ML-KEM
    # ========================================================

    with tab1:

        st.subheader(
            "ML-KEM-768"
        )

        st.write(
            "NIST FIPS 203"
        )

        if st.button(
            "🔑 Run ML-KEM-768",
            type="primary"
        ):

            try:

                from pqcrypto.kem import (
                    ml_kem_768
                )

                start = time.perf_counter()

                public_key, secret_key = (
                    ml_kem_768.keygen()
                )

                keygen_time = (
                    time.perf_counter()
                    - start
                ) * 1000

                start = time.perf_counter()

                ciphertext, sender_secret = (
                    ml_kem_768.encaps(
                        public_key
                    )
                )

                encaps_time = (
                    time.perf_counter()
                    - start
                ) * 1000

                start = time.perf_counter()

                receiver_secret = (
                    ml_kem_768.decaps(
                        secret_key,
                        ciphertext
                    )
                )

                decaps_time = (
                    time.perf_counter()
                    - start
                ) * 1000

                success = (
                    sender_secret
                    == receiver_secret
                )

                if success:

                    st.success(
                        "✅ Shared secret verification successful."
                    )

                else:

                    st.error(
                        "❌ Shared secret verification failed."
                    )

                col1, col2, col3, col4 = (
                    st.columns(4)
                )

                with col1:

                    st.metric(
                        "Public Key",
                        f"{ml_kem_768.PUBLIC_KEY_SIZE} B"
                    )

                with col2:

                    st.metric(
                        "Secret Key",
                        f"{ml_kem_768.SECRET_KEY_SIZE} B"
                    )

                with col3:

                    st.metric(
                        "Ciphertext",
                        f"{ml_kem_768.CIPHERTEXT_SIZE} B"
                    )

                with col4:

                    st.metric(
                        "Shared Secret",
                        f"{ml_kem_768.SHARED_SECRET_SIZE} B"
                    )

                col1, col2, col3 = (
                    st.columns(3)
                )

                with col1:

                    st.metric(
                        "Key Generation",
                        f"{keygen_time:.3f} ms"
                    )

                with col2:

                    st.metric(
                        "Encapsulation",
                        f"{encaps_time:.3f} ms"
                    )

                with col3:

                    st.metric(
                        "Decapsulation",
                        f"{decaps_time:.3f} ms"
                    )

            except Exception as error:

                st.error(
                    "❌ ML-KEM execution failed."
                )

                st.exception(
                    error
                )

    # ========================================================
    # ML-DSA
    # ========================================================

    with tab2:

        st.subheader(
            "ML-DSA-65"
        )

        st.write(
            "NIST FIPS 204"
        )

        if st.button(
            "✍️ Run ML-DSA-65",
            type="primary"
        ):

            try:

                from pqcrypto import (
                    InvalidSignatureError
                )

                from pqcrypto.sign import (
                    ml_dsa_65
                )

                message = (
                    b"QShield Post-Quantum Security Test"
                )

                start = time.perf_counter()

                public_key, secret_key = (
                    ml_dsa_65.keygen()
                )

                keygen_time = (
                    time.perf_counter()
                    - start
                ) * 1000

                start = time.perf_counter()

                signature = ml_dsa_65.sign(
                    secret_key,
                    message
                )

                sign_time = (
                    time.perf_counter()
                    - start
                ) * 1000

                start = time.perf_counter()

                try:

                    ml_dsa_65.verify(
                        public_key,
                        message,
                        signature
                    )

                    valid_signature = True

                except InvalidSignatureError:

                    valid_signature = False

                verify_time = (
                    time.perf_counter()
                    - start
                ) * 1000

                tampered_message = (
                    b"QShield Tampered Message"
                )

                try:

                    ml_dsa_65.verify(
                        public_key,
                        tampered_message,
                        signature
                    )

                    tampered_valid = True

                except InvalidSignatureError:

                    tampered_valid = False

                if valid_signature:

                    st.success(
                        "✅ Valid signature verified."
                    )

                else:

                    st.error(
                        "❌ Signature verification failed."
                    )

                if not tampered_valid:

                    st.success(
                        "✅ Tampering correctly detected."
                    )

                else:

                    st.error(
                        "❌ Tampered message was accepted."
                    )

                col1, col2, col3 = (
                    st.columns(3)
                )

                with col1:

                    st.metric(
                        "Public Key",
                        f"{ml_dsa_65.PUBLIC_KEY_SIZE} B"
                    )

                with col2:

                    st.metric(
                        "Secret Key",
                        f"{ml_dsa_65.SECRET_KEY_SIZE} B"
                    )

                with col3:

                    st.metric(
                        "Signature",
                        f"{ml_dsa_65.SIGNATURE_SIZE} B"
                    )

                col1, col2, col3 = (
                    st.columns(3)
                )

                with col1:

                    st.metric(
                        "Key Generation",
                        f"{keygen_time:.3f} ms"
                    )

                with col2:

                    st.metric(
                        "Signing",
                        f"{sign_time:.3f} ms"
                    )

                with col3:

                    st.metric(
                        "Verification",
                        f"{verify_time:.3f} ms"
                    )

            except Exception as error:

                st.error(
                    "❌ ML-DSA execution failed."
                )

                st.exception(
                    error
                )


# ============================================================
# QUANTUM THREAT ANALYSIS
# ============================================================

elif section == "⚠️ Quantum Threat Analysis":

    st.header(
        "⚠️ Quantum Threat Analysis"
    )

    st.write(
        """
This module explains the theoretical impact of quantum
algorithms on classical cryptographic assumptions.
"""
    )

    threat_table = pd.DataFrame(
        {
            "System": [
                "RSA",
                "ECC",
                "AES-128"
            ],
            "Security Assumption": [
                "Integer Factorization",
                "Discrete Logarithm",
                "Key Search"
            ],
            "Quantum Algorithm": [
                "Shor",
                "Shor",
                "Grover"
            ],
            "Impact": [
                "Strong quantum threat",
                "Strong quantum threat",
                "Quadratic search speedup"
            ]
        }
    )

    st.dataframe(
        threat_table,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    col1, col2, col3 = (
        st.columns(3)
    )

    with col1:

        st.metric(
            "RSA",
            "Shor"
        )

    with col2:

        st.metric(
            "ECC",
            "Shor"
        )

    with col3:

        st.metric(
            "AES-128",
            "≈ 2⁶⁴ Grover"
        )

    st.divider()

    if st.button(
        "⚠️ Run Detailed Analysis",
        type="primary"
    ):

        with st.spinner(
            "Running threat analysis..."
        ):

            output = run_script(
                "experiments/quantum_threat_analysis.py"
            )

        show_script_output(
            output
        )

    st.info(
        """
This is a theoretical security analysis. It is not a
demonstration of practically breaking RSA, ECC, or AES
with a real quantum computer.
"""
    )


# ============================================================
# RESEARCH RESULTS
# ============================================================

elif section == "📊 Research Results":

    st.header(
        "📊 QShield Research Results"
    )

    st.write(
        """
Experimental results generated by the QShield research
pipeline.
"""
    )

    # --------------------------------------------------------
    # Helper for result tables
    # --------------------------------------------------------

    def display_csv(
        title,
        relative_path
    ):

        st.subheader(
            title
        )

        path = os.path.join(
            PROJECT_ROOT,
            relative_path
        )

        if not os.path.exists(path):

            st.info(
                f"{relative_path} not found."
            )

            return

        try:

            df = pd.read_csv(
                path
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        except Exception as error:

            st.warning(
                f"Could not load {title}: "
                f"{error}"
            )

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    display_csv(
        "🤖 ML Model Comparison",
        "experiments/model_comparison_results.csv"
    )

    display_csv(
        "🔬 Cross-Validation",
        "experiments/cross_validation_results.csv"
    )

    
    display_csv(
        "🌐 Calibrated Noise Robustness",
        "experiments/noise_robustness_calibrated_results.csv"
    )

    display_csv(
        "🌐 Multicircuit Robustness",
        "experiments/multicircuit_robustness_results.csv"
    )

    display_csv(
        "🛡️ General Security Evaluation",
        "experiments/security_evaluation_results.csv"
    )

    display_csv(
        "⚛️ Grover Security",
        "experiments/grover_security_results.csv"
    )

    display_csv(
        "⚛️ QFT Security",
        "experiments/qft_security_results.csv"
    )

    display_csv(
        "⚛️ QPE Security",
        "experiments/qpe_security_results.csv"
    )

    display_csv(
        "⚛️ QAOA Security",
        "experiments/qaoa_security_results.csv"
    )

    display_csv(
        "⚛️ Shor Security",
        "experiments/shor_security_results.csv"
    )

    display_csv(
        "🔐 BB84 Evaluation",
        "experiments/bb84_evaluation_results.csv"
    )

    display_csv(
        "🔐 BB84 Noise Evaluation",
        "experiments/bb84_noise_evaluation_results.csv"
    )

    display_csv(
        "🔒 PQC Benchmark",
        "experiments/pqc_benchmark_results.csv"
    )

    st.divider()

    st.success(
        "QShield research dashboard loaded successfully."
    )