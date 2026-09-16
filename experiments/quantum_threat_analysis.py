import math


# ============================================================
# QSHIELD - QUANTUM CRYPTOGRAPHY THREAT ANALYSIS
# ============================================================


def rsa_threat_analysis():
    """
    Demonstrate the relationship between Shor's algorithm
    and RSA security.

    This is an educational security analysis.
    It does NOT attempt to factor a real-world RSA key.
    """

    print("=" * 65)
    print("QSHIELD - QUANTUM CRYPTOGRAPHY THREAT ANALYSIS")
    print("=" * 65)

    print("\n[1] RSA THREAT")

    print("\nClassical public-key algorithm:")
    print("RSA")

    print("\nSecurity assumption:")
    print("Integer factorization is computationally difficult.")

    print("\nQuantum threat:")
    print("Shor's algorithm can solve integer factorization")
    print("efficiently on a sufficiently capable fault-tolerant")
    print("quantum computer.")

    print("\nQShield Shor demonstration:")
    print("N = 15")
    print("a = 2")
    print("Period r = 4")

    print(
        "\nSecurity implication:"
    )

    print(
        "A sufficiently capable quantum computer could "
        "undermine the mathematical assumption behind RSA."
    )


def ecc_threat_analysis():
    """
    Demonstrate the relationship between Shor's algorithm
    and ECC security.
    """

    print("\n" + "=" * 65)
    print("ECC THREAT")
    print("=" * 65)

    print("\nClassical public-key algorithm:")
    print("Elliptic Curve Cryptography (ECC)")

    print("\nSecurity assumption:")
    print(
        "The elliptic-curve discrete logarithm problem "
        "is computationally difficult."
    )

    print("\nQuantum threat:")

    print(
        "Shor's algorithm provides a polynomial-time "
        "quantum approach to discrete logarithm problems."
    )

    print("\nSecurity implication:")

    print(
        "Sufficiently capable quantum computers could "
        "threaten ECC-based public-key cryptography."
    )


def symmetric_threat_analysis():
    """
    Demonstrate the different effect of Grover's algorithm
    on symmetric cryptography.
    """

    print("\n" + "=" * 65)
    print("SYMMETRIC CRYPTOGRAPHY THREAT")
    print("=" * 65)

    print("\nQuantum algorithm:")
    print("Grover's algorithm")

    print("\nTarget:")
    print("Unstructured search")

    print("\nSecurity implication:")

    print(
        "Grover's algorithm provides a quadratic speedup "
        "for brute-force search."
    )

    print(
        "\nTherefore, the effective brute-force security "
        "of an ideal n-bit symmetric key is approximately "
        "reduced from 2^n to 2^(n/2) quantum queries."
    )

    print("\nExample:")

    print(
        "128-bit symmetric key:"
    )

    print(
        "Classical search complexity: approximately 2^128"
    )

    print(
        "Quantum Grover search: approximately 2^64"
    )

    print(
        "\nThis is fundamentally different from the "
        "impact of Shor's algorithm on RSA/ECC."
    )


def compare_threats():
    """
    Compare major classical cryptographic families
    against quantum algorithms.
    """

    print("\n" + "=" * 65)
    print("QUANTUM THREAT COMPARISON")
    print("=" * 65)

    print(
        "\nAlgorithm        Classical Security Problem"
    )

    print(
        "RSA              Integer factorization"
    )

    print(
        "ECC              Discrete logarithm"
    )

    print(
        "AES              Key search"
    )

    print(
        "\nQuantum Algorithm"

    )

    print(
        "RSA  -> Shor's algorithm"
    )

    print(
        "ECC  -> Shor's algorithm"
    )

    print(
        "AES  -> Grover's algorithm"
    )


def main():

    rsa_threat_analysis()

    ecc_threat_analysis()

    symmetric_threat_analysis()

    compare_threats()

    print("\n" + "=" * 65)
    print("QSHIELD THREAT ANALYSIS COMPLETE")
    print("=" * 65)

    print(
        "\nConclusion:"
    )

    print(
        "Quantum computing creates different security "
        "impacts for public-key and symmetric cryptography."
    )


if __name__ == "__main__":

    main()