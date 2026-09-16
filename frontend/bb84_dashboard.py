import os
import sys

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)


# ============================================================
# BB84 IMPORTS
# ============================================================

from cryptography.bb84 import (
    generate_bits,
    generate_bases,
    prepare_qubits,
    measure_qubits,
    intercept_resend_attack,
    sift_key,
    calculate_qber
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="QShield - BB84",
    page_icon="🔐",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("🔐 QShield — BB84 Quantum Cryptography")

st.markdown(
    """
    ### Quantum Key Distribution Security Analysis

    This module demonstrates the **BB84 quantum key distribution
    protocol** and evaluates the effect of an **intercept-resend
    eavesdropping attack** using Quantum Bit Error Rate (QBER).
    """
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("BB84 Configuration")

num_qubits = st.sidebar.slider(
    "Number of Qubits",
    min_value=16,
    max_value=256,
    value=32,
    step=16
)

scenario = st.sidebar.selectbox(
    "Security Scenario",
    [
        "Normal Channel",
        "Intercept-Resend Attack"
    ]
)


# ============================================================
# RUN BB84
# ============================================================

if st.button(
    "▶ Run BB84 Analysis",
    use_container_width=True
):

    # --------------------------------------------------------
    # Alice
    # --------------------------------------------------------

    alice_bits = generate_bits(
        num_qubits
    )

    alice_bases = generate_bases(
        num_qubits
    )

    states = prepare_qubits(
        alice_bits,
        alice_bases
    )

    # --------------------------------------------------------
    # Eve
    # --------------------------------------------------------

    if scenario == "Intercept-Resend Attack":

        eve_bases = generate_bases(
            num_qubits
        )

        (
            eve_bits,
            received_states
        ) = intercept_resend_attack(
            states,
            eve_bases
        )

    else:

        eve_bases = None
        eve_bits = None

        received_states = states

    # --------------------------------------------------------
    # Bob
    # --------------------------------------------------------

    bob_bases = generate_bases(
        num_qubits
    )

    bob_bits = measure_qubits(
        received_states,
        bob_bases
    )

    # --------------------------------------------------------
    # SIFTING
    # --------------------------------------------------------

    (
        alice_key,
        bob_key,
        matching_positions
    ) = sift_key(
        alice_bits,
        alice_bases,
        bob_bits,
        bob_bases
    )

    # --------------------------------------------------------
    # QBER
    # --------------------------------------------------------

    qber = calculate_qber(
        alice_key,
        bob_key
    )

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    st.session_state["bb84_qber"] = qber
    st.session_state["bb84_key_length"] = len(
        alice_key
    )

    st.session_state["bb84_alice_key"] = alice_key
    st.session_state["bb84_bob_key"] = bob_key

    st.session_state["bb84_scenario"] = scenario


# ============================================================
# DISPLAY CURRENT RESULT
# ============================================================

if "bb84_qber" in st.session_state:

    qber = st.session_state["bb84_qber"]

    key_length = st.session_state[
        "bb84_key_length"
    ]

    current_scenario = st.session_state[
        "bb84_scenario"
    ]

    st.divider()

    st.subheader("Security Assessment")

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "QBER",
            f"{qber * 100:.2f}%"
        )

    with col2:

        st.metric(
            "Sifted Key Length",
            f"{key_length} bits"
        )

    with col3:

        st.metric(
            "Security Threshold",
            "11%"
        )

    with col4:

        if qber >= 0.11:

            st.metric(
                "Status",
                "⚠️ ANOMALOUS"
            )

        else:

            st.metric(
                "Status",
                "✅ NORMAL"
            )

    # --------------------------------------------------------
    # Security status
    # --------------------------------------------------------

    if qber >= 0.11:

        st.error(
            "🚨 HIGH QBER — Possible eavesdropping detected."
        )

        st.write(
            "The measured QBER exceeds the 11% "
            "BB84 security threshold."
        )

    else:

        st.success(
            "✅ LOW QBER — Quantum channel appears secure."
        )

        st.write(
            "The measured QBER is below the "
            "11% security threshold."
        )

    # --------------------------------------------------------
    # Scenario
    # --------------------------------------------------------

    st.info(
        f"Current scenario: **{current_scenario}**"
    )


# ============================================================
# STATISTICAL RESULTS
# ============================================================

st.divider()

st.subheader(
    "📊 Statistical BB84 Evaluation"
)

results_file = os.path.join(
    PROJECT_ROOT,
    "experiments",
    "bb84_evaluation_results.csv"
)

if os.path.exists(results_file):

    df = pd.read_csv(
        results_file
    )

    df["qber_percent"] = (
        df["qber"] * 100
    )

    normal = df[
        df["scenario"] == "normal"
    ]["qber_percent"]

    eve = df[
        df["scenario"] == "intercept_resend"
    ]["qber_percent"]

    # --------------------------------------------------------
    # Statistical metrics
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Normal Avg QBER",
            f"{normal.mean():.2f}%"
        )

    with col2:

        st.metric(
            "Eve Avg QBER",
            f"{eve.mean():.2f}%"
        )

    with col3:

        detection_rate = (
            df[
                df["scenario"]
                == "intercept_resend"
            ]["detected"]
            .mean()
            * 100
        )

        st.metric(
            "Attack Detection",
            f"{detection_rate:.2f}%"
        )

    with col4:

        false_positive_rate = (
            df[
                df["scenario"]
                == "normal"
            ]["detected"]
            .mean()
            * 100
        )

        st.metric(
            "False Positive Rate",
            f"{false_positive_rate:.2f}%"
        )

    # --------------------------------------------------------
    # Histogram
    # --------------------------------------------------------

    st.subheader(
        "QBER Distribution"
    )

    fig = plt.figure(
        figsize=(10, 5)
    )

    plt.hist(
        normal,
        bins=20,
        alpha=0.7,
        label="Normal Channel"
    )

    plt.hist(
        eve,
        bins=20,
        alpha=0.7,
        label="Intercept-Resend Attack"
    )

    plt.axvline(
        11,
        linestyle="--",
        linewidth=2,
        label="11% Security Threshold"
    )

    plt.xlabel(
        "QBER (%)"
    )

    plt.ylabel(
        "Number of Trials"
    )

    plt.title(
        "BB84 QBER Distribution"
    )

    plt.legend()

    plt.tight_layout()

    st.pyplot(
        fig
    )

else:

    st.warning(
        "Statistical results file not found. "
        "Run bb84_evaluation.py first."
    )


# ============================================================
# INTERPRETATION
# ============================================================

st.divider()

st.subheader(
    "🧠 QShield Interpretation"
)

st.markdown(
    """
    **BB84 Security Logic**

    1. Alice generates random bits and bases.
    2. Alice prepares BB84 quantum states.
    3. Bob measures using randomly selected bases.
    4. Alice and Bob keep only matching-basis measurements.
    5. QShield calculates QBER.
    6. QBER above the security threshold indicates a
       potentially compromised quantum channel.

    **Intercept-resend attack:** Eve measures the transmitted
    states and resends replacement states. When Eve chooses the
    wrong basis, she introduces errors that can be detected
    through QBER.
    """
)