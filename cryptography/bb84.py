import random


# ============================================================
# QSHIELD - BB84 QUANTUM KEY DISTRIBUTION
# ============================================================

SECURITY_THRESHOLD = 0.11


# ============================================================
# GENERATE RANDOM BITS
# ============================================================

def generate_bits(length):
    """Generate a random binary sequence."""

    if length <= 0:
        raise ValueError(
            "Length must be greater than zero."
        )

    return [
        random.randint(0, 1)
        for _ in range(length)
    ]


# ============================================================
# GENERATE RANDOM BASES
# ============================================================

def generate_bases(length):
    """
    Generate random BB84 bases.

    0 = Rectilinear (+)
    1 = Diagonal (x)
    """

    if length <= 0:
        raise ValueError(
            "Length must be greater than zero."
        )

    return [
        random.randint(0, 1)
        for _ in range(length)
    ]


# ============================================================
# PREPARE QUBITS
# ============================================================

def prepare_qubits(
    bits,
    bases
):
    """
    Represent BB84 quantum states.

    State representation:
        bit=0, basis=0 -> |0>
        bit=1, basis=0 -> |1>
        bit=0, basis=1 -> |+>
        bit=1, basis=1 -> |->
    """

    if len(bits) != len(bases):

        raise ValueError(
            "Bits and bases must have equal length."
        )

    qubits = []

    for bit, basis in zip(
        bits,
        bases
    ):

        qubits.append(
            {
                "bit": bit,
                "basis": basis
            }
        )

    return qubits


# ============================================================
# MEASURE QUBITS
# ============================================================

def measure_qubits(
    qubits,
    measurement_bases
):
    """
    Measure BB84 states.

    If measurement basis matches preparation basis,
    the original bit is recovered.

    If the bases differ, the result is random.
    """

    if len(qubits) != len(
        measurement_bases
    ):

        raise ValueError(
            "Qubit and measurement-basis lengths "
            "must be equal."
        )

    measured_bits = []

    for qubit, measurement_basis in zip(
        qubits,
        measurement_bases
    ):

        original_bit = qubit["bit"]
        original_basis = qubit["basis"]

        if (
            measurement_basis
            == original_basis
        ):

            measured_bits.append(
                original_bit
            )

        else:

            measured_bits.append(
                random.randint(0, 1)
            )

    return measured_bits


# ============================================================
# INTERCEPT-RESEND ATTACK
# ============================================================

def intercept_resend_attack(
    qubits,
    eve_bases=None
):
    """
    Simulate an intercept-resend attack.

    Eve measures each qubit using a random basis and
    resends the resulting state to Bob.
    """

    length = len(qubits)

    if eve_bases is None:

        eve_bases = generate_bases(
            length
        )

    if len(eve_bases) != length:

        raise ValueError(
            "Eve bases must match qubit length."
        )

    eve_bits = measure_qubits(
        qubits,
        eve_bases
    )

    resent_qubits = prepare_qubits(
        eve_bits,
        eve_bases
    )

    return resent_qubits


# ============================================================
# SIFT KEY
# ============================================================

def sift_key(
    alice_bits,
    alice_bases,
    bob_bits,
    bob_bases
):
    """
    Keep only positions where Alice and Bob used
    the same basis.
    """

    if not (
        len(alice_bits)
        == len(alice_bases)
        == len(bob_bits)
        == len(bob_bases)
    ):

        raise ValueError(
            "All BB84 sequences must have equal length."
        )

    alice_key = []
    bob_key = []

    matching_indices = []

    for index in range(
        len(alice_bits)
    ):

        if (
            alice_bases[index]
            == bob_bases[index]
        ):

            alice_key.append(
                alice_bits[index]
            )

            bob_key.append(
                bob_bits[index]
            )

            matching_indices.append(
                index
            )

    return (
        alice_key,
        bob_key,
        matching_indices
    )


# ============================================================
# CALCULATE QBER
# ============================================================

def calculate_qber(
    alice_key,
    bob_key
):
    """
    Calculate Quantum Bit Error Rate.
    """

    if len(alice_key) != len(bob_key):

        raise ValueError(
            "Alice and Bob keys must have equal length."
        )

    if len(alice_key) == 0:

        return 0.0

    errors = sum(
        a != b
        for a, b in zip(
            alice_key,
            bob_key
        )
    )

    return (
        errors
        / len(alice_key)
    )


# ============================================================
# RUN BB84
# ============================================================

def run_bb84(
    length=32,
    use_eve=False
):
    """
    Execute a complete BB84 protocol simulation.

    Returns
    -------
    dict
        Structured BB84 analysis result.
    """

    if length <= 0:

        raise ValueError(
            "Length must be greater than zero."
        )

    # --------------------------------------------------------
    # Alice
    # --------------------------------------------------------

    alice_bits = generate_bits(
        length
    )

    alice_bases = generate_bases(
        length
    )

    prepared_qubits = prepare_qubits(
        alice_bits,
        alice_bases
    )

    # --------------------------------------------------------
    # Optional Eve
    # --------------------------------------------------------

    if use_eve:

        transmitted_qubits = (
            intercept_resend_attack(
                prepared_qubits
            )
        )

    else:

        transmitted_qubits = (
            prepared_qubits
        )

    # --------------------------------------------------------
    # Bob
    # --------------------------------------------------------

    bob_bases = generate_bases(
        length
    )

    bob_bits = measure_qubits(
        transmitted_qubits,
        bob_bases
    )

    # --------------------------------------------------------
    # Sifting
    # --------------------------------------------------------

    (
        alice_key,
        bob_key,
        matching_indices
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
    # Security decision
    # --------------------------------------------------------

    if qber > SECURITY_THRESHOLD:

        status = "ANOMALOUS"

    else:

        status = "NORMAL"

    # --------------------------------------------------------
    # Return structured result
    # --------------------------------------------------------

    return {

        "protocol":
            "BB84",

        "length":
            length,

        "use_eve":
            use_eve,

        "alice_bits":
            alice_bits,

        "alice_bases":
            alice_bases,

        "bob_bases":
            bob_bases,

        "bob_bits":
            bob_bits,

        "alice_key":
            alice_key,

        "bob_key":
            bob_key,

        "matching_indices":
            matching_indices,

        "qber":
            qber,

        "qber_percent":
            qber * 100,

        "sifted_key_length":
            len(alice_key),

        "security_threshold":
            SECURITY_THRESHOLD,

        "status":
            status,

        "attack_detected":
            qber > SECURITY_THRESHOLD
    }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 65)
    print(
        "QSHIELD - BB84 QUANTUM KEY DISTRIBUTION"
    )
    print("=" * 65)

    LENGTH = 32

    # --------------------------------------------------------
    # Normal BB84
    # --------------------------------------------------------

    print()
    print("NORMAL CHANNEL")

    result = run_bb84(
        length=LENGTH,
        use_eve=False
    )

    print(
        f"Qubits: "
        f"{result['length']}"
    )

    print(
        f"Sifted key length: "
        f"{result['sifted_key_length']}"
    )

    print(
        f"QBER: "
        f"{result['qber_percent']:.2f}%"
    )

    print(
        f"Security status: "
        f"{result['status']}"
    )

    # --------------------------------------------------------
    # Eve
    # --------------------------------------------------------

    print()
    print("INTERCEPT-RESEND ATTACK")

    result = run_bb84(
        length=LENGTH,
        use_eve=True
    )

    print(
        f"Qubits: "
        f"{result['length']}"
    )

    print(
        f"Sifted key length: "
        f"{result['sifted_key_length']}"
    )

    print(
        f"QBER: "
        f"{result['qber_percent']:.2f}%"
    )

    print(
        f"Security status: "
        f"{result['status']}"
    )

    print()
    print("=" * 65)