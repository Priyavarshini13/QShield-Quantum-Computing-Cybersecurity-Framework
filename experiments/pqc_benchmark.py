import csv
import os
import statistics
import time

from pqcrypto.kem import ml_kem_768
from pqcrypto.sign import ml_dsa_65
from pqcrypto import InvalidSignatureError


# ============================================================
# Configuration
# ============================================================

TRIALS = 100

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

OUTPUT_FILE = os.path.join(
    PROJECT_ROOT,
    "experiments",
    "pqc_benchmark_results.csv"
)


# ============================================================
# ML-KEM-768 Benchmark
# ============================================================

def benchmark_ml_kem():

    results = []

    print("\n" + "=" * 65)
    print("ML-KEM-768 PERFORMANCE BENCHMARK")
    print("=" * 65)

    print(f"\nNumber of trials: {TRIALS}")

    for trial in range(1, TRIALS + 1):

        # ----------------------------------------------------
        # Key Generation
        # ----------------------------------------------------

        start = time.perf_counter()

        public_key, secret_key = ml_kem_768.keygen()

        keygen_time = (
            time.perf_counter() - start
        ) * 1000

        # ----------------------------------------------------
        # Encapsulation
        # ----------------------------------------------------

        start = time.perf_counter()

        ciphertext, sender_secret = ml_kem_768.encaps(
            public_key
        )

        encaps_time = (
            time.perf_counter() - start
        ) * 1000

        # ----------------------------------------------------
        # Decapsulation
        # ----------------------------------------------------

        start = time.perf_counter()

        receiver_secret = ml_kem_768.decaps(
            secret_key,
            ciphertext
        )

        decaps_time = (
            time.perf_counter() - start
        ) * 1000

        # ----------------------------------------------------
        # Verification
        # ----------------------------------------------------

        shared_secret_match = (
            sender_secret == receiver_secret
        )

        results.append({
            "trial": trial,
            "algorithm": "ML-KEM-768",
            "keygen_time_ms": keygen_time,
            "encaps_time_ms": encaps_time,
            "decaps_time_ms": decaps_time,
            "sign_time_ms": "",
            "verify_time_ms": "",
            "public_key_size": ml_kem_768.PUBLIC_KEY_SIZE,
            "secret_key_size": ml_kem_768.SECRET_KEY_SIZE,
            "ciphertext_size": ml_kem_768.CIPHERTEXT_SIZE,
            "signature_size": "",
            "shared_secret_size": ml_kem_768.SHARED_SECRET_SIZE,
            "verification": shared_secret_match,
        })

        if trial % 10 == 0:
            print(f"    Completed {trial}/{TRIALS} trials")

    return results


# ============================================================
# ML-DSA-65 Benchmark
# ============================================================

def benchmark_ml_dsa():

    results = []

    print("\n" + "=" * 65)
    print("ML-DSA-65 PERFORMANCE BENCHMARK")
    print("=" * 65)

    print(f"\nNumber of trials: {TRIALS}")

    message = b"QShield Post-Quantum Security Benchmark"

    for trial in range(1, TRIALS + 1):

        # ----------------------------------------------------
        # Key Generation
        # ----------------------------------------------------

        start = time.perf_counter()

        public_key, secret_key = ml_dsa_65.keygen()

        keygen_time = (
            time.perf_counter() - start
        ) * 1000

        # ----------------------------------------------------
        # Signing
        # ----------------------------------------------------

        start = time.perf_counter()

        signature = ml_dsa_65.sign(
            secret_key,
            message
        )

        sign_time = (
            time.perf_counter() - start
        ) * 1000

        # ----------------------------------------------------
        # Verification
        # ----------------------------------------------------

        start = time.perf_counter()

        try:

            ml_dsa_65.verify(
                public_key,
                message,
                signature
            )

            verification = True

        except InvalidSignatureError:

            verification = False

        verify_time = (
            time.perf_counter() - start
        ) * 1000

        results.append({
            "trial": trial,
            "algorithm": "ML-DSA-65",
            "keygen_time_ms": keygen_time,
            "encaps_time_ms": "",
            "decaps_time_ms": "",
            "sign_time_ms": sign_time,
            "verify_time_ms": verify_time,
            "public_key_size": ml_dsa_65.PUBLIC_KEY_SIZE,
            "secret_key_size": ml_dsa_65.SECRET_KEY_SIZE,
            "ciphertext_size": "",
            "signature_size": ml_dsa_65.SIGNATURE_SIZE,
            "shared_secret_size": "",
            "verification": verification,
        })

        if trial % 10 == 0:
            print(f"    Completed {trial}/{TRIALS} trials")

    return results


# ============================================================
# Save CSV
# ============================================================

def save_results(results):

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    fieldnames = [
        "trial",
        "algorithm",
        "keygen_time_ms",
        "encaps_time_ms",
        "decaps_time_ms",
        "sign_time_ms",
        "verify_time_ms",
        "public_key_size",
        "secret_key_size",
        "ciphertext_size",
        "signature_size",
        "shared_secret_size",
        "verification",
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(results)

    print("\nCSV saved:")
    print(OUTPUT_FILE)


# ============================================================
# Statistics
# ============================================================

def print_statistics(results):

    print("\n" + "=" * 65)
    print("PQC BENCHMARK SUMMARY")
    print("=" * 65)

    for algorithm in [
        "ML-KEM-768",
        "ML-DSA-65"
    ]:

        rows = [
            row
            for row in results
            if row["algorithm"] == algorithm
        ]

        print(f"\n{algorithm}")
        print("-" * 65)

        keygen = [
            float(row["keygen_time_ms"])
            for row in rows
        ]

        print(
            f"Key Generation : "
            f"{statistics.mean(keygen):.3f} ms "
            f"(avg)"
        )

        print(
            f"Key Generation : "
            f"{statistics.median(keygen):.3f} ms "
            f"(median)"
        )

        if algorithm == "ML-KEM-768":

            encaps = [
                float(row["encaps_time_ms"])
                for row in rows
            ]

            decaps = [
                float(row["decaps_time_ms"])
                for row in rows
            ]

            print(
                f"Encapsulation  : "
                f"{statistics.mean(encaps):.3f} ms "
                f"(avg)"
            )

            print(
                f"Decapsulation  : "
                f"{statistics.mean(decaps):.3f} ms "
                f"(avg)"
            )

            print(
                f"Public Key     : "
                f"{ml_kem_768.PUBLIC_KEY_SIZE} bytes"
            )

            print(
                f"Secret Key     : "
                f"{ml_kem_768.SECRET_KEY_SIZE} bytes"
            )

            print(
                f"Ciphertext     : "
                f"{ml_kem_768.CIPHERTEXT_SIZE} bytes"
            )

            print(
                f"Shared Secret  : "
                f"{ml_kem_768.SHARED_SECRET_SIZE} bytes"
            )

        else:

            signing = [
                float(row["sign_time_ms"])
                for row in rows
            ]

            verification = [
                float(row["verify_time_ms"])
                for row in rows
            ]

            print(
                f"Signing        : "
                f"{statistics.mean(signing):.3f} ms "
                f"(avg)"
            )

            print(
                f"Verification   : "
                f"{statistics.mean(verification):.3f} ms "
                f"(avg)"
            )

            print(
                f"Public Key     : "
                f"{ml_dsa_65.PUBLIC_KEY_SIZE} bytes"
            )

            print(
                f"Secret Key     : "
                f"{ml_dsa_65.SECRET_KEY_SIZE} bytes"
            )

            print(
                f"Signature      : "
                f"{ml_dsa_65.SIGNATURE_SIZE} bytes"
            )

        successful = sum(
            bool(row["verification"])
            for row in rows
        )

        success_rate = (
            successful / len(rows)
        ) * 100

        print(
            f"Successful Operations : "
            f"{successful}/{len(rows)} "
            f"({success_rate:.2f}%)"
        )


# ============================================================
# Main
# ============================================================

def main():

    print("\n")
    print("=" * 65)
    print("QSHIELD - POST-QUANTUM CRYPTOGRAPHY BENCHMARK")
    print("=" * 65)

    print("\nAlgorithms:")
    print("  1. ML-KEM-768")
    print("  2. ML-DSA-65")

    print(f"\nTrials per algorithm: {TRIALS}")

    # --------------------------------------------------------
    # ML-KEM
    # --------------------------------------------------------

    kem_results = benchmark_ml_kem()

    # --------------------------------------------------------
    # ML-DSA
    # --------------------------------------------------------

    dsa_results = benchmark_ml_dsa()

    # --------------------------------------------------------
    # Combine
    # --------------------------------------------------------

    all_results = (
        kem_results +
        dsa_results
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    save_results(all_results)

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    print_statistics(all_results)

    # --------------------------------------------------------
    # Completion
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("PQC BENCHMARK COMPLETED")
    print("=" * 65)

    print("\nOutput:")
    print("experiments/pqc_benchmark_results.csv")


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()