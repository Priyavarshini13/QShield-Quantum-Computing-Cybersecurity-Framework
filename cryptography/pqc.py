import time

from pqcrypto import InvalidSignatureError
from pqcrypto.kem import ml_kem_768
from pqcrypto.sign import ml_dsa_65


# ============================================================
# ML-KEM-768
# ============================================================

def run_ml_kem():

    print("=" * 65)
    print("QSHIELD - ML-KEM-768")
    print("=" * 65)

    print("\nPurpose:")
    print("Post-quantum key encapsulation")

    print("\nStandard:")
    print("NIST FIPS 203")

    print("\nParameter set:")
    print("ML-KEM-768")

    # --------------------------------------------------------
    # Key Generation
    # --------------------------------------------------------

    print("\n[1] Generating ML-KEM key pair...")

    start = time.perf_counter()

    public_key, secret_key = ml_kem_768.keygen()

    keygen_time = time.perf_counter() - start

    print("    Key pair generated successfully.")

    # --------------------------------------------------------
    # Encapsulation
    # --------------------------------------------------------

    print("\n[2] Encapsulating shared secret...")

    start = time.perf_counter()

    ciphertext, sender_secret = ml_kem_768.encaps(public_key)

    encaps_time = time.perf_counter() - start

    print("    Ciphertext generated successfully.")
    print("    Shared secret generated.")

    # --------------------------------------------------------
    # Decapsulation
    # --------------------------------------------------------

    print("\n[3] Decapsulating shared secret...")

    start = time.perf_counter()

    receiver_secret = ml_kem_768.decaps(
        secret_key,
        ciphertext
    )

    decaps_time = time.perf_counter() - start

    print("    Shared secret recovered successfully.")

    # --------------------------------------------------------
    # Shared Secret Verification
    # --------------------------------------------------------

    print("\n[4] Shared secret verification")

    verification = sender_secret == receiver_secret

    if verification:
        print("    RESULT: SUCCESS")
        print("    Sender and receiver derived the same shared secret.")
    else:
        print("    RESULT: FAILURE")
        print("    Shared secrets do not match.")

    # --------------------------------------------------------
    # ML-KEM Sizes
    # --------------------------------------------------------

    print("\nML-KEM-768 Sizes:")
    print(
        f"    Public key       : "
        f"{ml_kem_768.PUBLIC_KEY_SIZE} bytes"
    )

    print(
        f"    Secret key       : "
        f"{ml_kem_768.SECRET_KEY_SIZE} bytes"
    )

    print(
        f"    Ciphertext       : "
        f"{ml_kem_768.CIPHERTEXT_SIZE} bytes"
    )

    print(
        f"    Shared secret    : "
        f"{ml_kem_768.SHARED_SECRET_SIZE} bytes"
    )

    # --------------------------------------------------------
    # Performance
    # --------------------------------------------------------

    print("\nPerformance:")
    print(
        f"    Key generation   : "
        f"{keygen_time * 1000:.3f} ms"
    )

    print(
        f"    Encapsulation    : "
        f"{encaps_time * 1000:.3f} ms"
    )

    print(
        f"    Decapsulation    : "
        f"{decaps_time * 1000:.3f} ms"
    )

    return {
        "algorithm": "ML-KEM-768",
        "standard": "NIST FIPS 203",
        "public_key_size": ml_kem_768.PUBLIC_KEY_SIZE,
        "secret_key_size": ml_kem_768.SECRET_KEY_SIZE,
        "ciphertext_size": ml_kem_768.CIPHERTEXT_SIZE,
        "shared_secret_size": ml_kem_768.SHARED_SECRET_SIZE,
        "keygen_time_ms": keygen_time * 1000,
        "encaps_time_ms": encaps_time * 1000,
        "decaps_time_ms": decaps_time * 1000,
        "verification": verification,
    }


# ============================================================
# ML-DSA-65
# ============================================================

def run_ml_dsa():

    print("\n")
    print("=" * 65)
    print("QSHIELD - ML-DSA-65")
    print("=" * 65)

    print("\nPurpose:")
    print("Post-quantum digital signatures")

    print("\nStandard:")
    print("NIST FIPS 204")

    print("\nParameter set:")
    print("ML-DSA-65")

    message = b"QShield Post-Quantum Security Test"

    # --------------------------------------------------------
    # Key Generation
    # --------------------------------------------------------

    print("\n[1] Generating ML-DSA key pair...")

    start = time.perf_counter()

    public_key, secret_key = ml_dsa_65.keygen()

    keygen_time = time.perf_counter() - start

    print("    Key pair generated successfully.")

    # --------------------------------------------------------
    # Signing
    # --------------------------------------------------------

    print("\n[2] Signing message...")

    start = time.perf_counter()

    signature = ml_dsa_65.sign(
        secret_key,
        message
    )

    sign_time = time.perf_counter() - start

    print("    Signature generated successfully.")

    # --------------------------------------------------------
    # Signature Verification
    # --------------------------------------------------------

    print("\n[3] Verifying signature...")

    start = time.perf_counter()

    try:

        # pqcrypto 1.0.0 returns None when verification succeeds.
        ml_dsa_65.verify(
            public_key,
            message,
            signature
        )

        valid = True

    except InvalidSignatureError:

        valid = False

    verify_time = time.perf_counter() - start

    print(f"    Valid signature: {valid}")

    # --------------------------------------------------------
    # Tampered Message Test
    # --------------------------------------------------------

    tampered_message = b"QShield Tampered Message"

    print("\n[4] Testing tampered message...")

    try:

        ml_dsa_65.verify(
            public_key,
            tampered_message,
            signature
        )

        tampered_valid = True

    except InvalidSignatureError:

        tampered_valid = False

    print(
        f"    Tampered verification: "
        f"{tampered_valid}"
    )

    if valid and not tampered_valid:

        print("    RESULT: SUCCESS")
        print(
            "    Signature correctly rejected "
            "the tampered message."
        )

    else:

        print("    RESULT: FAILURE")

    # --------------------------------------------------------
    # ML-DSA Sizes
    # --------------------------------------------------------

    print("\nML-DSA-65 Sizes:")

    print(
        f"    Public key       : "
        f"{ml_dsa_65.PUBLIC_KEY_SIZE} bytes"
    )

    print(
        f"    Secret key       : "
        f"{ml_dsa_65.SECRET_KEY_SIZE} bytes"
    )

    print(
        f"    Signature        : "
        f"{ml_dsa_65.SIGNATURE_SIZE} bytes"
    )

    # --------------------------------------------------------
    # Performance
    # --------------------------------------------------------

    print("\nPerformance:")

    print(
        f"    Key generation   : "
        f"{keygen_time * 1000:.3f} ms"
    )

    print(
        f"    Signing          : "
        f"{sign_time * 1000:.3f} ms"
    )

    print(
        f"    Verification     : "
        f"{verify_time * 1000:.3f} ms"
    )

    return {
        "algorithm": "ML-DSA-65",
        "standard": "NIST FIPS 204",
        "public_key_size": ml_dsa_65.PUBLIC_KEY_SIZE,
        "secret_key_size": ml_dsa_65.SECRET_KEY_SIZE,
        "signature_size": ml_dsa_65.SIGNATURE_SIZE,
        "keygen_time_ms": keygen_time * 1000,
        "sign_time_ms": sign_time * 1000,
        "verify_time_ms": verify_time * 1000,
        "signature_valid": valid,
        "tampered_signature_valid": tampered_valid,
    }


# ============================================================
# QShield PQC Summary
# ============================================================

def print_comparison(kem_results, dsa_results):

    print("\n")
    print("=" * 65)
    print("QSHIELD - POST-QUANTUM CRYPTOGRAPHY SUMMARY")
    print("=" * 65)

    # --------------------------------------------------------
    # ML-KEM
    # --------------------------------------------------------

    print("\nML-KEM-768")
    print("-" * 65)

    print(
        f"Public Key       : "
        f"{kem_results['public_key_size']} bytes"
    )

    print(
        f"Secret Key       : "
        f"{kem_results['secret_key_size']} bytes"
    )

    print(
        f"Ciphertext       : "
        f"{kem_results['ciphertext_size']} bytes"
    )

    print(
        f"Shared Secret    : "
        f"{kem_results['shared_secret_size']} bytes"
    )

    print(
        f"Key Generation   : "
        f"{kem_results['keygen_time_ms']:.3f} ms"
    )

    print(
        f"Encapsulation    : "
        f"{kem_results['encaps_time_ms']:.3f} ms"
    )

    print(
        f"Decapsulation    : "
        f"{kem_results['decaps_time_ms']:.3f} ms"
    )

    print(
        f"Verification     : "
        f"{kem_results['verification']}"
    )

    # --------------------------------------------------------
    # ML-DSA
    # --------------------------------------------------------

    print("\nML-DSA-65")
    print("-" * 65)

    print(
        f"Public Key       : "
        f"{dsa_results['public_key_size']} bytes"
    )

    print(
        f"Secret Key       : "
        f"{dsa_results['secret_key_size']} bytes"
    )

    print(
        f"Signature        : "
        f"{dsa_results['signature_size']} bytes"
    )

    print(
        f"Key Generation   : "
        f"{dsa_results['keygen_time_ms']:.3f} ms"
    )

    print(
        f"Signing          : "
        f"{dsa_results['sign_time_ms']:.3f} ms"
    )

    print(
        f"Verification     : "
        f"{dsa_results['verify_time_ms']:.3f} ms"
    )

    print(
        f"Signature Valid  : "
        f"{dsa_results['signature_valid']}"
    )

    print(
        f"Tampered Valid   : "
        f"{dsa_results['tampered_signature_valid']}"
    )

    # --------------------------------------------------------
    # Security Role
    # --------------------------------------------------------

    print("\nSecurity Role")
    print("-" * 65)

    print(
        "ML-KEM-768 : "
        "Post-quantum key establishment"
    )

    print(
        "ML-DSA-65  : "
        "Post-quantum digital signatures"
    )

    # --------------------------------------------------------
    # QShield Integration
    # --------------------------------------------------------

    print("\nQShield Integration")
    print("-" * 65)

    print(
        "BB84       : "
        "Quantum Key Distribution"
    )

    print(
        "ML-KEM     : "
        "Post-Quantum Key Encapsulation"
    )

    print(
        "ML-DSA     : "
        "Post-Quantum Digital Signatures"
    )

    print(
        "Shor       : "
        "Public-Key Quantum Threat Analysis"
    )

    print(
        "Grover     : "
        "Symmetric-Key Quantum Threat Analysis"
    )


# ============================================================
# Main
# ============================================================

def main():

    print("\n")
    print("=" * 65)
    print("QSHIELD - POST-QUANTUM CRYPTOGRAPHY MODULE")
    print("ML-KEM-768 + ML-DSA-65")
    print("=" * 65)

    # --------------------------------------------------------
    # Run ML-KEM
    # --------------------------------------------------------

    kem_results = run_ml_kem()

    # --------------------------------------------------------
    # Run ML-DSA
    # --------------------------------------------------------

    dsa_results = run_ml_dsa()

    # --------------------------------------------------------
    # Final Summary
    # --------------------------------------------------------

    print_comparison(
        kem_results,
        dsa_results
    )

    print("\n")
    print("=" * 65)
    print("QSHIELD PQC MODULE COMPLETED")
    print("=" * 65)


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()