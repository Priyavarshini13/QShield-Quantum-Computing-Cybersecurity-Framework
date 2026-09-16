# QShield-Quantum-Computing-Cybersecurity-Framework
AI-powered cybersecurity framework for detecting anomalous quantum circuit behavior using machine learning, quantum behavioral analysis, BB84, and post-quantum cryptography.

# QShield — AI-Powered Cybersecurity for Quantum Computing

<p align="center">
  <b>A Quantum Computing Cybersecurity Framework using Machine Learning and Behavioral Analysis</b>
</p>

<p align="center">
  ⚛️ Quantum Computing &nbsp; | &nbsp; 🤖 Machine Learning &nbsp; | &nbsp; 🛡️ Cybersecurity &nbsp; | &nbsp; 🔐 Cryptography
</p>

---

## 📌 Overview

**QShield** is a software-based cybersecurity framework designed to analyze and protect **quantum computing workloads** from anomalous circuit behavior.

The framework combines **quantum circuit analysis, machine learning, behavioral analysis, simulated noise evaluation, quantum cryptography, and post-quantum cryptography** into a unified experimental platform.

QShield analyzes the structure and execution behavior of quantum circuits, generates synthetic circuit-level mutation scenarios, measures behavioral deviations using **Total Variation Distance (TVD)**, and uses a **Random Forest machine learning model** to distinguish normal and anomalous circuit behavior.

The project also evaluates security aspects of quantum algorithms, the BB84 quantum key distribution protocol, and post-quantum cryptographic algorithms.

---

## 🎯 Research Question

> **Can machine-learning-based behavioral analysis detect faults and security anomalies in quantum circuits under different noise and circuit-modification conditions?**

---

## 🚀 Objectives

- Analyze the structural properties of quantum circuits.
- Extract meaningful numerical features from quantum circuits.
- Generate synthetic circuit-level mutation scenarios.
- Compare ideal and modified quantum circuit behavior.
- Measure behavioral deviation using Total Variation Distance.
- Detect anomalous circuit behavior using machine learning.
- Evaluate detector behavior under simulated depolarizing noise.
- Study security behavior across different quantum algorithms.
- Evaluate BB84 quantum key distribution under attack and noise.
- Benchmark selected post-quantum cryptographic algorithms.
- Provide an interactive cybersecurity dashboard.

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │   Quantum Circuit   │
                    │       / QASM        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Circuit Analyzer   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Feature Extraction  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Attack / Mutation   │
                    │     Generation      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Quantum Simulation  │
                    │  + Noise Modeling   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Behavioral Analysis │
                    │        (TVD)        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   ML Anomaly        │
                    │     Detection       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Security Risk Score │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ FastAPI + Streamlit │
                    │     Dashboard       │
                    └─────────────────────┘
⚛️ Quantum Circuit Security

QShield analyzes quantum circuits using structural and behavioral characteristics.

Circuit Features

The framework extracts features including:

Number of qubits
Number of classical bits
Circuit depth
Total number of gates
H gates
X gates
Y gates
Z gates
CX gates
CZ gates
RX gates
RY gates
RZ gates
Measurement operations
Barrier operations
Total Variation Distance (TVD)
Simulated noise rate
🛡️ Synthetic Security Scenarios

QShield generates controlled circuit-level mutation scenarios to study anomalous behavior.

Supported Scenarios
Scenario	Description
Normal	Original quantum circuit
Gate Insertion	Inserts additional quantum gates
Gate Deletion	Removes eligible quantum operations
Gate Substitution	Replaces selected single-qubit gates
Multiple Gate Insertion	Inserts multiple additional gates

These scenarios are used as synthetic circuit-level attack/mutation experiments for evaluating the detection framework. They are not intended to represent every real-world quantum cybersecurity attack.

📊 Behavioral Analysis

Quantum circuits produce probabilistic measurement outcomes.

QShield compares the probability distributions produced by circuits and measures their behavioral difference using Total Variation Distance (TVD).

For two probability distributions \(P\) and \(Q\):

TVD(P,Q) = 1/2 × Σ |P(x) - Q(x)|

A larger TVD indicates a greater behavioral deviation between the reference and evaluated circuit.

QShield combines behavioral information with circuit-level features for anomaly detection.

🤖 Machine Learning

QShield uses a Random Forest Classifier for anomaly detection.

Model Input

The model uses circuit-level structural features together with:

TVD
Noise rate
Model Configuration
Algorithm       : Random Forest
Estimators      : 200
Random State     : 42
Class Weight     : Balanced
Validation       : 5-Fold GroupKFold
Grouping         : Circuit name

Circuit-level grouping is used so that circuits from the same benchmark are not randomly distributed between training and validation samples.

🧪 Model Evaluation

The current circuit-level cross-validation experiment produced:

Metric	Random Forest
Accuracy	87.87% ± 4.97%
Precision	92.63%
Recall	92.12%
F1 Score	92.32% ± 3.21%

The reported values are from 5-fold circuit-level GroupKFold cross-validation.

The standard deviations represent variation across the five validation folds.

🔍 Model Comparison

QShield also evaluates multiple classical machine learning models.

Model	Accuracy	Precision	Recall	F1 Score
Random Forest	87.87% ± 4.97%	92.63%	92.12%	92.32% ± 3.21%
SVM	84.33% ± 6.75%	92.05%	87.91%	89.88% ± 4.39%
Gradient Boosting	86.96% ± 4.92%	91.12%	92.65%	91.80% ± 3.27%
🌐 Noise Robustness

QShield evaluates detector behavior under simulated depolarizing noise.

Noise levels evaluated:

0.5%
1.0%
2.0%
3.0%
4.0%
5.0%

The calibrated noise robustness experiment produced:

Successful evaluations : 666
Noise levels           : 6
Overall attack detection : 90.15%
Overall false-positive rate : 16.67%

The noise robustness experiment uses circuits from the same QASMBench benchmark family used during dataset generation. Therefore, it is treated as a noise robustness evaluation, rather than an independent held-out generalization experiment.

⚛️ Quantum Algorithm Security

QShield includes security experiments for multiple quantum algorithms.

Implemented Algorithms
Grover's Search
Quantum Fourier Transform (QFT)
Quantum Phase Estimation (QPE)
Quantum Approximate Optimization Algorithm (QAOA)
Shor's Algorithm

The experiments examine how synthetic circuit modifications affect algorithm behavior.

🔎 Grover's Search

A small Grover search circuit is used to demonstrate quantum search behavior and evaluate the effect of circuit modifications.

The demonstration successfully identifies the selected target state.

🌊 Quantum Fourier Transform

QShield evaluates QFT behavior using a multi-qubit circuit and analyzes the resulting probability distribution.

Circuit modifications are evaluated through behavioral deviation and anomaly detection.

📐 Quantum Phase Estimation

QPE is implemented using a small educational circuit.

The experiment demonstrates phase estimation and evaluates how circuit modifications affect the resulting measurement distribution.

🧮 QAOA

QAOA is demonstrated using a small MaxCut problem.

The implementation evaluates the resulting candidate solutions and studies the effect of circuit modifications on algorithm behavior.

🔐 Shor's Algorithm

QShield contains an educational small-number implementation of Shor's period-finding concept.

The current implementation demonstrates factorization-related period finding for a small example and is not intended as a scalable implementation of Shor's algorithm.

🔐 BB84 Quantum Key Distribution

QShield includes a simulation of the BB84 Quantum Key Distribution protocol.

The framework evaluates:

Normal communication
Intercept-resend attack
Simulated channel noise
Noise combined with intercept-resend attack
Example Evaluation

For a 32-qubit simulation:

Normal Channel
QBER            : 0.00%
Security Status : NORMAL

Intercept-Resend Attack
QBER            : 33.33%
Security Status : ANOMALOUS
📡 BB84 Security Evaluation

Repeated experiments were performed to evaluate BB84 behavior.

The evaluation included:

1,000 normal trials
1,000 intercept-resend trials

Results:

Normal average QBER       : 0.00%
Normal false-positive rate: 0.00%

Eve average QBER          : 25.29%
Attack detection rate     : 91.70%

Additional experiments evaluate BB84 under simulated Pauli-channel noise.

🔒 Post-Quantum Cryptography

QShield also includes experiments with selected post-quantum cryptographic algorithms.

ML-KEM-768

Used for:

Key generation
Encapsulation
Decapsulation
Shared-secret verification

Example measured sizes:

Public Key      : 1184 bytes
Secret Key      : 2400 bytes
Ciphertext      : 1088 bytes
Shared Secret   : 32 bytes
ML-DSA-65

Used for:

Key generation
Digital signing
Signature verification
Tampered-message verification

Example measured sizes:

Public Key      : 1952 bytes
Secret Key      : 4032 bytes
Signature       : 3309 bytes

The implementation successfully verified valid signatures and rejected tampered signatures.

Benchmark timings are machine- and run-dependent and should not be interpreted as universal performance values.

⚠️ Quantum Threat Analysis

QShield includes a theoretical analysis of major cryptographic threats from quantum computing.

Public-Key Cryptography

Shor's algorithm provides a theoretical quantum threat to cryptographic systems based on:

Integer factorization
Discrete logarithms

This is relevant to cryptosystems such as:

RSA
ECC
Symmetric Cryptography

Grover's algorithm provides a quadratic speedup for unstructured search.

For AES-128, the theoretical quantum query complexity is approximately:

2^64

This analysis is theoretical and does not represent practical breaking of these cryptographic systems.

📚 Benchmark Dataset

QShield uses quantum benchmark circuits, including circuits from:

QASMBench

Repository:

https://github.com/pnnl/QASMBench

The benchmark circuits are used for circuit analysis, feature extraction, mutation experiments, and robustness evaluation.

Some benchmark circuits contain unsupported/custom instructions or extremely large gate counts. Such circuits are excluded from certain experiments when they cannot be safely or practically evaluated by the current implementation.

🖥️ Web Dashboard

QShield provides an interactive Streamlit dashboard backed by FastAPI.

Dashboard Sections
🏠 Overview
🛡️ Circuit Security
⚛️ Quantum Algorithms
🔐 BB84 Cryptography
🔒 Post-Quantum Cryptography
⚠️ Quantum Threat Analysis
📊 Research Results

The dashboard allows users to:

Upload QASM circuits
Analyze circuit structure
Select security scenarios
Run quantum simulations
Evaluate TVD
Generate anomaly predictions
View security risk scores
Explore research results
🚀 Installation
1. Clone the Repository
git clone https://github.com/Priyavarshini13/QShield.git
cd QShield
2. Create a Virtual Environment
Windows
python -m venv .venv
.venv\Scripts\activate
Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt
▶️ Running QShield
Run the FastAPI Backend

From the project root:

uvicorn backend.main:app --reload

The API will be available at:

http://127.0.0.1:8000

Interactive API documentation:

http://127.0.0.1:8000/docs
Run the Streamlit Dashboard

Open another terminal and activate the virtual environment.

streamlit run frontend/app.py

The dashboard will be available at:

http://localhost:8501
🧪 Running Experiments
Machine Learning Cross-Validation
python ml/cross_validation.py
Model Comparison
python ml/model_comparison.py
Security Evaluation
python experiments/run_security_evaluation.py
Noise Robustness
python experiments/noise_robustness_final.py
BB84 Evaluation
python experiments/bb84_evaluation.py
BB84 Noise Evaluation
python experiments/bb84_noise_evaluation.py
Post-Quantum Cryptography Benchmark
python experiments/pqc_benchmark.py
📁 Project Structure
QShield/
│
├── backend/
│   ├── api/
│   ├── services/
│   └── main.py
│
├── cryptography/
│   ├── __init__.py
│   ├── bb84.py
│   └── pqc.py
│
├── data/
│   ├── benchmarks/
│   ├── temp_benchmarks/
│   ├── dataset_generator.py
│   └── qshield_dataset.csv
│
├── experiments/
│   ├── plots/
│   ├── noise_robustness.py
│   ├── multicircuit_robustness.py
│   ├── run_security_evaluation.py
│   ├── bb84_evaluation.py
│   ├── bb84_noise_evaluation.py
│   ├── pqc_benchmark.py
│   └── ...
│
├── frontend/
│   ├── app.py
│   └── bb84_dashboard.py
│
├── ml/
│   ├── anomaly_detector.py
│   ├── qshield_detector.py
│   ├── cross_validation.py
│   └── model_comparison.py
│
├── quantum/
│   ├── basic_circuit.py
│   ├── circuit_analyzer.py
│   ├── feature_extractor.py
│   ├── behavior_comparator.py
│   ├── qasm_loader.py
│   └── algorithms/
│       ├── grover.py
│       ├── qft.py
│       ├── qpe.py
│       ├── qaoa.py
│       └── shor.py
│
├── security/
│   ├── attack_generator.py
│   └── noise_generator.py
│
├── tests/
│
├── README.md
└── requirements.txt
🧰 Technology Stack
Category	Technologies
Language	Python
Quantum Computing	Qiskit, Qiskit Aer
Machine Learning	Scikit-learn
Data Processing	NumPy, Pandas
Backend	FastAPI
Frontend	Streamlit
Cryptography	BB84, ML-KEM-768, ML-DSA-65
Visualization	Matplotlib
Version Control	Git, GitHub
Future Deployment	Docker
Database	PostgreSQL
🔬 Experimental Methodology

The overall experimental workflow is:

1. Load quantum benchmark circuit
             ↓
2. Analyze circuit structure
             ↓
3. Extract numerical features
             ↓
4. Generate normal / mutated variants
             ↓
5. Simulate circuit execution
             ↓
6. Apply simulated noise
             ↓
7. Calculate behavioral deviation
             ↓
8. Generate ML prediction
             ↓
9. Calculate security risk
             ↓
10. Record experimental results
📈 Research Evaluation

QShield evaluates several dimensions of quantum cybersecurity:

Evaluation	Purpose
ML Cross-Validation	Evaluate circuit-level generalization
Model Comparison	Compare classical ML approaches
Noise Robustness	Study detector behavior under simulated noise
Multicircuit Evaluation	Evaluate behavior across benchmark circuits
Algorithm Security	Study quantum algorithm modifications
BB84 Evaluation	Analyze QKD security
BB84 Noise Evaluation	Study QKD under simulated channel noise
PQC Benchmark	Evaluate selected post-quantum primitives
⚠️ Limitations

The current implementation has several limitations:

Circuit mutations are synthetic experimental scenarios, not a complete model of real-world quantum attacks.
Quantum execution is primarily performed using simulation.
Noise experiments use a simulated depolarizing noise model.
BB84 noise evaluation uses a simulated Pauli-channel representation rather than a full density-matrix quantum-channel model.
Some QASMBench circuits contain custom or unsupported instructions.
Very large benchmark circuits may exceed the project's current computational safety limits.
The current Shor implementation is an educational small-number demonstration.
The noise robustness experiment uses the same benchmark family as dataset generation and therefore should not be interpreted as an independent held-out benchmark.
The current risk-score calibration uses heuristic weighting rather than parameters learned through calibration optimization.
🔮 Future Work

Potential future improvements include:

Evaluation on additional quantum benchmark suites.
Hardware/QPU-based experiments.
More realistic quantum fault and attack models.
Advanced anomaly detection models.
Deep learning-based quantum circuit representation.
Graph neural networks for circuit analysis.
Quantum-specific adversarial testing.
Federated learning for distributed quantum workloads.
Real-time monitoring of quantum execution environments.
PostgreSQL-based experiment management.
Docker-based deployment.
Cloud-based quantum backend integration.
Expanded post-quantum cryptography evaluation.
Hardware-aware noise modeling.
📌 Project Status

Status: Research Prototype / Active Development

Current components include:

✅ Quantum circuit analyzer
✅ QASM circuit loader
✅ Feature extraction
✅ Synthetic mutation generation
✅ Quantum behavioral comparison
✅ ML anomaly detector
✅ Circuit-level cross-validation
✅ Noise robustness evaluation
✅ Multicircuit evaluation
✅ Quantum algorithm security experiments
✅ BB84 simulation and evaluation
✅ Post-quantum cryptography benchmark
✅ FastAPI backend
✅ Streamlit dashboard
👩‍💻 Author

Priyavarshini V

B.E. Computer Science and Engineering
Artificial Intelligence & Machine Learning

Sri Eshwar College of Engineering, Coimbatore

📄 License

This project is intended for academic, research, and educational purposes.

A formal open-source license can be added to the repository separately.

⭐ Acknowledgement

QShield is developed as an academic/research project exploring the intersection of:

Quantum Computing × Artificial Intelligence × Cybersecurity × Cryptography

The project aims to provide an experimental software framework for studying security challenges associated with quantum computing workloads.
