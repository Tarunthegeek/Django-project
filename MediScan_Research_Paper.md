# MediScan: Privacy-Preserving Localized AI Inference Platform for Clinical Risk Assessment

## CONTENTS

**1 Introduction**
  1.1 Motivation
  1.2 Contributions
  1.3 Report Organization

**2 Related Work**
  2.1 Cloud-Based AI in Healthcare
  2.2 Healthcare Data Privacy Regulations
  2.3 Gaps Addressed by This Work

**3 Problem Formulation**
  3.1 System Model
  3.2 Global Optimization Objective
  3.3 Privacy Constraints

**4 Localized Inference Framework**
  4.1 Standalone Inference Paradigm
  4.2 The Diagnostic Algorithm
  4.3 Handling Heterogeneous Clinical Data

**5 Cryptographic Security Layer**
  5.1 Privacy Threat Model
  5.2 The SHA-256 Cryptographic Mechanism
  5.3 PII Masking & Data Scrubbing
  5.4 Immutable Audit Logging

**6 Machine Learning Models**
  6.1 Model Selection Rationale
  6.2 Probabilistic Logistic Regression
  6.3 Gradient Boosting (Deprecation Rationale)
  6.4 Feature Extraction & Explainability

**7 System Architecture**
  7.1 Architectural Overview
  7.2 Database Tier (Data Store)
  7.3 Logic Tier (Django Engine)
  7.4 Presentation Tier (Web Dashboard)

**8 Implementation**
  8.1 Backend Stack
  8.2 Core Inference Engine
  8.3 Security Module
  8.4 Role-Based Access Control (RBAC)

**9 Dataset Generation**
  9.1 Synthetic Clinical Data Framework
  9.2 Dataset Distribution

**10 Mathematical Derivations**
  10.1 Base and Component Risk Functions
  10.2 Synergistic and Behavioral Modifiers
  10.3 Cumulative Risk Equation
  10.4 Probability Conversion (Sigmoid Anchor)
  10.5 Cryptographic Hash Pipeline

**11 Experimental Evaluation**
  11.1 Experimental Setup
  11.2 Model Accuracy & Precision
  11.3 ROC-AUC Performance
  11.4 System Latency

**12 Security Analysis**
  12.1 Threat Model Assumption
  12.2 Resistance to Database Exfiltration
  12.3 Transport Layer Security

**13 Scalability Analysis**
  13.1 Storage Footprint Optimization
  13.2 Horizontal Scalability

**14 Future Research Directions**
  14.1 Wearable Device Integration
  14.2 Federated Learning Extensions
  14.3 Homomorphic Encryption
  14.4 EMR System Integration

**15 Conclusion**

**16 System Interfaces (Screenshots Annexure)**

---

## 1. Introduction

### 1.1 Motivation
Electronic Health Records (EHRs) and clinical diagnostics generate immense volumes of clinically valuable data. Machine learning (ML) models trained on such data have demonstrated remarkable diagnostic performance. However, deploying these models in clinical settings faces a severe paradox: the APIs and cloud infrastructure required to run high-performance AI models fundamentally conflict with patient privacy laws. Centralizing or transmitting patient data raises serious legal compliance issues and creates concentrated attack surfaces for adversarial actors.

### 1.2 Contributions
This report presents MediScan, an end-to-end platform that integrates localized AI into a highly secure, deployable system. Our specific contributions are:
1. **Localized Inference Architecture:** We designed a complete standalone ML inference pipeline that requires zero external network calls, completely eliminating third-party interception risks.
2. **Cryptographic Data Pipeline:** We integrated SHA-256 hashing into the inference lifecycle, ensuring raw medical inputs are scrubbed from memory immediately after processing.
3. **Probabilistic Clinical Modeling:** We implemented a Logistic Regression engine anchored to strict medical thresholds, providing smooth, scientifically grounded risk curves.
4. **Production-Grade Implementation:** We provided a complete implementation using Django, Scikit-Learn, and SQLite, featuring a modern Glassmorphism dashboard with robust Role-Based Access Control.

### 1.3 Report Organization
Section 2 reviews related work. Section 3 defines the problem setting. Section 4 presents the inference framework. Section 5 details the security layer. Section 6 discusses the ML models. Section 7 describes the system architecture. Section 8 details the implementation. Section 9 outlines dataset generation. Section 10 details the core mathematical formulas. Section 11 presents experimental results. Section 12 provides a security analysis. Section 13 analyzes scalability. Section 14 outlines future research. Section 15 concludes.

---

## 2. Related Work

### 2.1 Cloud-Based AI in Healthcare
The foundational approach to deploying ML in healthcare has relied heavily on cloud-based APIs (e.g., AWS SageMaker). While offering immense computational power, they require transmitting raw Protected Health Information (PHI) outside of the hospital firewall, exposing endpoints to data interception.

### 2.2 Healthcare Data Privacy Regulations
HIPAA’s Privacy Rule establishes categories of PHI and permits de-identification through strict standards. Compliance with these regulatory frameworks is a design requirement for MediScan. Our architecture satisfies the data minimization, purpose limitation, and storage limitation principles by completely eschewing raw data persistence.

### 2.3 Gaps Addressed by This Work
Existing platforms tend to focus either on heavy cryptographic primitives (which suffer from immense latency) or completely ignore deployment security in favor of model accuracy. MediScan addresses this gap by providing a lightweight, instantly deployable system that marries high-accuracy tabular ML with zero-knowledge database principles.

---

## 3. Problem Formulation

### 3.1 System Model
We consider a local clinical environment holding private patient inference requests $X \in \mathbb{R}^d$, where $d$ is a 7-dimensional feature vector representing clinical measurements (Age, BMI, Blood Pressure, Glucose, Cholesterol, Smoking Status, Activity Level).

### 3.2 Global Optimization Objective
The central goal of the system is to output a reliable probability $P(Y=1 \mid X)$ indicating the likelihood of severe cardiovascular/metabolic risk, utilizing a pre-trained model $w^*$ that minimizes empirical risk, without ever storing $X$.

### 3.3 Privacy Constraints
Under our threat model, we assume an internal database breach. The formal privacy requirement is that given full access to the persisted database, an adversary cannot reconstruct the original clinical vector $X$ or associate it with a patient identity.

---

## 4. Localized Inference Framework

### 4.1 Standalone Inference Paradigm
Unlike cloud-reliant systems, MediScan utilizes a localized inference paradigm. The pre-trained model parameters are serialized and stored entirely on the host machine. When a request is made, the evaluation occurs in local RAM, entirely bypassing the public internet.

### 4.2 The Diagnostic Algorithm
Upon form submission, the local framework normalizes the user input array and passes it through the pre-compiled `.pkl` model to retrieve a probabilistic output array representing healthy vs. critical outcomes.

### 4.3 Handling Heterogeneous Clinical Data
To mitigate the effects of varying input scales (e.g., Age ranges vs. Cholesterol ranges), the system relies on a `StandardScaler` fitted during the training phase to strictly normalize inputs before inference execution.

---

## 5. Cryptographic Security Layer

### 5.1 Privacy Threat Model
In standard applications, submitting form data results in direct database insertion. An adversary gaining access to this table immediately breaches HIPAA by exposing raw clinical metrics.

### 5.2 The SHA-256 Cryptographic Mechanism
MediScan intercepts the payload in RAM. The raw vector is concatenated into a singular byte-string and passed through the SHA-256 cryptographic hash function. Because SHA-256 is fundamentally non-reversible, a database breach yields no usable medical data.

### 5.3 PII Masking & Data Scrubbing
Any identifiable metadata (such as names) is scrubbed via regex masking before processing (e.g., converting "John Doe" to `J*** D***`).

### 5.4 Immutable Audit Logging
The database stores only the 64-character hash alongside the generated model probability, execution latency, and a UTC timestamp, creating an immutable, privacy-preserving audit log.

---

## 6. Machine Learning Models

### 6.1 Model Selection Rationale
In clinical decision support, interpretability and gradient smoothness are critical. Clinicians need to understand why a model produces a given prediction.

### 6.2 Probabilistic Logistic Regression
MediScan utilizes Logistic Regression (LR). LR provides a convex loss landscape and outputs probabilities via the Sigmoid function, ensuring that incremental changes in biometrics result in smooth, proportional changes in calculated risk.

### 6.3 Gradient Boosting (Deprecation Rationale)
Initial iterations utilizing Gradient Boosting Classifiers were deprecated. Tree-based models suffered from "binary jumping"—where a minimal input perturbation (e.g., BMI shifting from 29.9 to 30.0) resulted in erratic shifts from 10% to 90% risk probability.

### 6.4 Feature Extraction & Explainability
To provide actionable intelligence, MediScan extracts the absolute weights of the model coefficients (`coef_`) multiplied by the normalized input vector. This allows the dashboard to dynamically render the "Top Contributing Factors" for every patient.

---

## 7. System Architecture

### 7.1 Architectural Overview
The MediScan platform adopts a cleanly separated Model-View-Controller (MVC) architecture.

### 7.2 Database Tier (Data Store)
A strictly structured SQLite database restricted to immutable audit logs and hashed inputs, completely decoupled from raw application logic.

### 7.3 Logic Tier (Django Engine)
The core Django framework managing API routing, template rendering, and Scikit-Learn pipeline execution.

### 7.4 Presentation Tier (Web Dashboard)
A real-time web dashboard featuring a cyber-clinical aesthetic using Glassmorphism. The primary Result Banner utilizes dynamic color shifting (Emerald, Yellow, Orange, Red) based on the calculated probability.

---

## 8. Implementation

### 8.1 Core Technology Stack
MediScan is built upon a robust, independent technology stack to guarantee maximum local performance and security without relying on cloud-hosted SaaS tools.

*   **Programming Languages:** Python 3.11, JavaScript (ES6+), HTML5, CSS3.
*   **Web Framework:** Django 4.2 (Python) - Handles complex URL routing, server-side template rendering, and session-based authentication.
*   **Machine Learning Engine:** Scikit-Learn (`sklearn`) - Powers the `LogisticRegression` inference model, `StandardScaler` normalization pipelines, and the `.pkl` serialization/deserialization logic. NumPy (`numpy`) is utilized for high-speed matrix and array calculations.
*   **Database Management:** SQLite 3 - Operates as the lightweight, purely localized, serverless RDBMS to securely store the SHA-256 Hashes and Audit Logs.
*   **Frontend Design System:** Tailwind CSS - Provides utility-first styling classes to construct the fully responsive, dynamic Glassmorphism User Interface without heavy CSS bundles.
*   **Security Primitives:** Python's native `hashlib` library handles the 256-bit cryptographic payload obfuscation, while Django's native authentication system handles CSRF (Cross-Site Request Forgery) protection.

### 8.2 Core Inference Engine
Upon receiving an HTTP request, the `pipeline.py` module:
1. Validates input bounds.
2. Hashes the payload.
3. Executes `model.predict_proba()`.
4. Computes top features via coefficient weighting.
5. Returns the context dictionary to the template engine.

### 8.3 Security Module
The application enforces strict data validation and HTML entity sanitization to prevent XSS (Cross-Site Scripting) and character encoding vulnerabilities.

### 8.4 Role-Based Access Control (RBAC)
Hospital nodes authenticate using Django's session framework. Access is restricted using custom decorators (`@approved_required`). New accounts are sandboxed until an Administrator explicitly reviews them.

---

## 9. Dataset Generation

### 9.1 Synthetic Clinical Data Framework
Due to the unavailability of unrestricted PHI, MediScan's model is trained on a mathematically generated synthetic dataset of $N=5,000$ profiles.

### 9.2 Dataset Distribution
The final generated dataset achieves a near 50/50 split between Healthy and At-Risk profiles, preventing class-imbalance bias during model training. The logic was anchored tightly to established clinical thresholds, as detailed in Section 10.

---

## 10. Mathematical Derivations

### 10.1 Base and Component Risk Functions
The individual risk factors are modeled using strict clinical thresholds to map metabolic readings to objective risk weights.

**Base Age Risk:**
> $R_{base}(Age) = \left( \frac{Age}{100} \right) \times 0.20$

**Non-Linear BMI Risk (Piecewise U-Curve):**
> $R_{BMI}(BMI) = \begin{cases} 
0.10, & \text{if } BMI < 18.5 \text{ (Underweight)} \\
0.00, & \text{if } 18.5 \le BMI \le 25 \text{ (Normal)} \\
0.15, & \text{if } 25 < BMI < 30 \text{ (Overweight)} \\
0.30, & \text{if } BMI \ge 30 \text{ (Obese)}
\end{cases}$

**Blood Pressure Risk (Piecewise Threshold):**
> $R_{BP}(BP) = \begin{cases} 
0.00, & \text{if } BP < 120 \text{ (Normal)} \\
0.10, & \text{if } 120 \le BP < 140 \text{ (Prehypertension)} \\
0.25, & \text{if } BP \ge 140 \text{ (Hypertension)}
\end{cases}$

**Fasting Glucose Risk (Piecewise Threshold):**
> $R_{Glu}(Glucose) = \begin{cases} 
0.00, & \text{if } Glucose < 100 \text{ (Normal)} \\
0.10, & \text{if } 100 \le Glucose \le 125 \text{ (Prediabetes)} \\
0.30, & \text{if } Glucose > 125 \text{ (Diabetes)}
\end{cases}$

**Cholesterol Risk (Piecewise Threshold):**
> $R_{Chol}(Cholesterol) = \begin{cases} 
0.00, & \text{if } Cholesterol < 200 \text{ (Normal)} \\
0.10, & \text{if } 200 \le Cholesterol < 240 \text{ (Borderline)} \\
0.20, & \text{if } Cholesterol \ge 240 \text{ (High)}
\end{cases}$

### 10.2 Synergistic and Behavioral Modifiers
The model explicitly handles behavioral interventions, compounding negative behavior (smoking at an advanced age) and rewarding protective behavior (physical activity).

**Smoking Risk ($S$ is 0 for No, 1 for Yes):**
> $R_{Smk}(S) = S \times 0.15$

**Compound Age-Smoking Synergy Risk:**
> $R_{Syn}(S, Age) = \begin{cases} 
0.20, & \text{if } S = 1 \text{ and } Age > 50 \\
0.00, & \text{otherwise}
\end{cases}$

**Activity Protection Modifier ($A$ is activity level from 0 to 10):**
> $P_{Act}(A) = \left( \frac{A}{10} \right) \times 0.15$

### 10.3 Cumulative Risk Equation
The total underlying clinical risk used to generate the ground-truth labels is mathematically defined as the linear sum of all individual components:
> $R_{total} = R_{base} + R_{BMI} + R_{BP} + R_{Glu} + R_{Chol} + R_{Smk} + R_{Syn} - P_{Act}$

### 10.4 Probability Conversion (Sigmoid Anchor)
To convert the raw accumulated risk points into a smooth probability percentage suitable for training labels, a modified Logistic Sigmoid function was applied, anchored to a strict baseline threshold of 0.45:
> $P(Y=1 \mid X) = \frac{1}{1 + e^{-15 \times (R_{total} - 0.45)}}$

### 10.5 Cryptographic Hash Pipeline
For the privacy-preserving data logging mechanism, all raw clinical inputs are concatenated into a single string and permanently obfuscated using the SHA-256 cryptographic algorithm before being saved to the database.
> $Hash = \text{SHA-256}(Age \parallel BMI \parallel BP \parallel Glucose \parallel Cholesterol \parallel Smoking \parallel Activity)$

---

## 11. Experimental Evaluation

### 11.1 Experimental Setup
The model was trained on 80% of the synthetic dataset and evaluated on a 20% holdout test set using K-fold validation.

### 11.2 Model Accuracy & Precision
The Logistic Regression model achieved an **87.0%** overall classification accuracy on unseen holdout data.

### 11.3 ROC-AUC Performance
The model recorded an ROC-AUC Score of **0.9484**, demonstrating an exceptionally high ability to distinguish between safe and at-risk metabolic profiles.

### 11.4 System Latency
Because MediScan bypasses cloud APIs and runs entirely in memory, end-to-end inference latency consistently benchmarks under **15 milliseconds**.

---

## 12. Security Analysis

### 12.1 Threat Model Assumption
We assume an adversarial actor successfully exfiltrates the entire `.sqlite3` database file from the host server.

### 12.2 Resistance to Database Exfiltration
The adversary acquires only: `[id, user_id, hash, risk_score, timestamp]`. Without the original input variables, mapping the 64-character SHA-256 hashes back to human biometrics is computationally infeasible.

### 12.3 Transport Layer Security
While inference is local, local network transmission (from Nurse workstation to Host Server) is protected via CSRF tokens and secure session cookies.

---

## 13. Scalability Analysis

### 13.1 Storage Footprint Optimization
By discarding raw clinical inputs, the database footprint is massively reduced. A single record consumes approximately 150 bytes. One Million patient records consume less than 150 MB of storage space, allowing decades of operation without enterprise cloud storage.

### 13.2 Horizontal Scalability
Because the model inference relies on a static `.pkl` file in memory, the application is entirely stateless. It can be horizontally scaled infinitely across hospital load balancers.

---

## 14. Future Plans & Roadmap

While MediScan successfully proves the concept of localized, privacy-preserving AI, future iterations of the platform are planned to expand its real-world utility in a clinical environment.

### 14.1 Wearable Device & IoT Integration
Developing a secure, localized API bridge to ingest real-time continuous biometric data. This would allow the platform to automatically pull metrics like resting heart rate, sleep quality, and blood oxygen (SpO2) directly from FDA-approved smartwatches and continuous glucose monitors, rather than relying on manual form entry.

### 14.2 Federated Learning Ecosystem
Currently, the model is trained centrally on synthetic data. A major future plan is to transition the standalone architecture into a **Cross-Silo Federated Learning** ecosystem. This would allow multiple decentralized hospital networks to collaboratively train a massive global AI model using their local data, without ever actually transmitting or sharing the raw patient datasets with a central server.

### 14.3 Multi-Disease Expansion
Expanding the AI engine beyond cardiovascular and metabolic risks to include parallel Logistic Regression pipelines for Oncology (Breast Cancer detection via tabular FNA metrics), Nephrology (Chronic Kidney Disease), and Neurology (Stroke prediction). 

### 14.4 Advanced Security: Multi-Factor Authentication (MFA)
While the current platform uses strict Django-based Role-Based Access Control, a planned security enhancement is the integration of Time-based One-Time Passwords (TOTP). This will require all clinical Administrators to use Google Authenticator or hardware keys before they can access the immutable Audit Logs.

### 14.5 EMR/EHR System Integration
To eliminate dual data-entry for nurses and doctors, future plans include building secure, HL7/FHIR compliant bridges. This would allow MediScan to seamlessly integrate with existing Electronic Health Record (EHR) systems like Epic or Cerner, pulling the required 7 metrics directly from the patient's main file.

---

## 15. Conclusion
The MediScan platform successfully bridges the gap between advanced artificial intelligence and stringent healthcare privacy requirements. By replacing vulnerable cloud-based architectures with an entirely localized, cryptographically secured inference engine, the project demonstrates that clinical facilities can leverage powerful predictive analytics without exposing themselves to data breaches. The successful implementation of Logistic Regression, combined with an accessible, dynamic Glassmorphism interface, results in a tool that is not only secure but immediately actionable for medical professionals.

---

## 16. System Interfaces (Screenshots Annexure)

*Please insert the following screenshots to complete the final report formatting:*

**[ 📸 INSERT SCREENSHOT 1: The Login / Registration UI ]**
*(Caption: The secure authentication barrier preventing unauthorized access to the AI pipeline.)*

**[ 📸 INSERT SCREENSHOT 2: The Inference Form ]**
*(Caption: The clinical input mechanism where users enter their metrics.)*

**[ 📸 INSERT SCREENSHOT 3: High/Critical Risk Banner ]**
*(Caption: The dynamic UI showcasing the probability score, Top Contributing Factors extraction, and actionable medical advice. Tip: Input Age 58, BMI 34, BP 165, Smoker to get a Critical Red screen!)*

**[ 📸 INSERT SCREENSHOT 4: The Admin Audit Log ]**
*(Caption: Proof of Privacy — The immutable database log showing that only SHA-256 hashes are stored, while raw inputs are permanently discarded.)*
