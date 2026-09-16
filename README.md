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
