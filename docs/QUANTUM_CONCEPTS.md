# Quantum Physics & Mathematical Foundations of Quantum Digital Signatures (QDS)

> **CORE PRINCIPLE: 100% PHYSICS & MATHEMATICS — ZERO ARTIFICIAL INTELLIGENCE / MACHINE LEARNING**  
> Cyber threat detection, verification, and channel diagnostics in this framework are strictly derived from **quantum information theory, operator mechanics, spectral decomposition, projective measurements, and classical concentration inequalities**. No neural networks, black-box heuristics, or statistical ML models are utilized.

---

## Table of Contents
1. [Pure States and Superposition](#1-pure-states-and-superposition)
2. [Bloch Sphere Geometry](#2-bloch-sphere-geometry)
3. [Density Operators & Mixed States](#3-density-operators--mixed-states)
4. [Quantum Invariants: Purity & von Neumann Entropy](#4-quantum-invariants-purity--von-neumann-entropy)
5. [Distinguishability: Quantum Trace Distance vs Classical TVD](#5-distinguishability-quantum-trace-distance-vs-classical-tvd)
6. [Quantum Teleportation & Feed-Forward Corrections](#6-quantum-teleportation--feed-forward-corrections)
7. [Quantum Channels & Kraus Operator Decomposition](#7-quantum-channels--kraus-operator-decomposition)
8. [Quantum State Tomography (QST)](#8-quantum-state-tomography-qst)
9. [Non-Locality: Bell States & CHSH Inequality](#9-non-locality-bell-states--chsh-inequality)
10. [Fundamental Security Theorems: No-Cloning & Intercept-Resend](#10-fundamental-security-theorems-no-cloning--intercept-resend)
11. [Statistical Anomaly Detection via Hoeffding's Inequality](#11-statistical-anomaly-detection-via-hoeffdings-inequality)
12. [Post-Quantum Cryptography (PQC) vs Quantum Digital Signatures (QDS)](#12-post-quantum-cryptography-pqc-vs-quantum-digital-signatures-qds)

---

## 1. Pure States and Superposition

A pure single-qubit quantum state lives in a 2-dimensional complex Hilbert space $\mathcal{H}_2 \cong \mathbb{C}^2$:

$$|\psi\rangle = \alpha|0\rangle + \beta|1\rangle = \begin{pmatrix} \alpha \\ \beta \end{pmatrix}$$

where probability amplitudes $\alpha, \beta \in \mathbb{C}$ satisfy the normalization constraint:

$$\langle\psi|\psi\rangle = |\alpha|^2 + |\beta|^2 = 1$$

In our framework, the sender (Alice) deterministically generates $(\theta, \phi)$ from the cryptographically secure SHA-256 digest $h = \text{SHA256}(M)$ of the signed document:

$$\alpha = \cos\left(\frac{\theta}{2}\right), \quad \beta = e^{i\phi}\sin\left(\frac{\theta}{2}\right)$$

---

## 2. Bloch Sphere Geometry

Any pure single-qubit state corresponds to a point on the surface of the unit sphere $S^2$:

$$\vec{r} = (r_x, r_y, r_z) = (\sin\theta\cos\phi, \; \sin\theta\sin\phi, \; \cos\theta)$$

The Euclidean Bloch displacement between expected state $\vec{r}_{\text{exp}}$ and observed state $\vec{r}_{\text{obs}}$ is:

$$D_{\text{Bloch}} = \|\vec{r}_{\text{exp}} - \vec{r}_{\text{obs}}\|_2 = \sqrt{(\Delta r_x)^2 + (\Delta r_y)^2 + (\Delta r_z)^2}$$

For pure states, $F(|\psi\rangle, |\phi\rangle) = \frac{1 + \vec{r}_1 \cdot \vec{r}_2}{2} = 1 - \frac{D_{\text{Bloch}}^2}{4}$.

---

## 3. Density Operators & Mixed States

When a quantum system is subject to environmental noise, eavesdropping, or statistical uncertainty, it cannot be described by a state vector. It must be described by a **density operator** $\rho \in \mathcal{L}(\mathcal{H})$ satisfying:
1. **Hermiticity**: $\rho = \rho^\dagger$
2. **Unit Trace**: $\text{Tr}(\rho) = 1$
3. **Positive Semi-Definiteness**: $\rho \ge 0 \iff \lambda_i \ge 0$

For any single-qubit state, the density matrix can be expanded in the Pauli basis $\{I, \sigma_x, \sigma_y, \sigma_z\}$:

$$\rho = \frac{1}{2}\left(I + r_x\sigma_x + r_y\sigma_y + r_z\sigma_z\right) = \frac{1}{2}\begin{pmatrix} 1 + r_z & r_x - i r_y \\ r_x + i r_y & 1 - r_z \end{pmatrix}$$

where $\vec{r} = (r_x, r_y, r_z) \in \mathbb{R}^3$ is the Bloch vector with $\|\vec{r}\| \le 1$.
- $\|\vec{r}\| = 1$: **Pure state** (on the sphere surface).
- $\|\vec{r}\| < 1$: **Mixed state** (in the sphere interior).
- $\|\vec{r}\| = 0$: **Maximally mixed state** $\rho = \frac{1}{2}I$.

---

## 4. Quantum Invariants: Purity & von Neumann Entropy

### Quantum Purity ($\gamma$)
Purity measures the degree of quantum coherence:

$$\gamma(\rho) = \text{Tr}(\rho^2) = \sum_i \lambda_i^2 = \frac{1 + \|\vec{r}\|^2}{2}$$

- Pure State: $\gamma = 1.0$
- Maximally Mixed State (qubit): $\gamma = 0.5$

### von Neumann Entropy ($S$)
The quantum analog of Shannon entropy:

$$S(\rho) = -\text{Tr}(\rho \log_2 \rho) = -\sum_{i=1}^d \lambda_i \log_2 \lambda_i$$

where $\lambda_i$ are the eigenvalues of $\rho$ (with $0 \log_2 0 \equiv 0$).
- Pure State: $S(\rho) = 0.0$ bits.
- Maximally Mixed State: $S(\rho) = 1.0$ bit.
- **Physical Cyber Defense Principle**: Any non-unitary eavesdropping or environmental decoherence strictly increases $S(\rho) > 0$ and decreases $\gamma(\rho) < 1.0$.

---

## 5. Distinguishability: Quantum Trace Distance vs Classical TVD

### Quantum Trace Distance ($D$)
The fundamental measure of physical distinguishability between two quantum states:

$$D(\rho, \sigma) = \frac{1}{2}\text{Tr}|\rho - \sigma| = \frac{1}{2}\text{Tr}\sqrt{(\rho - \sigma)^\dagger(\rho - \sigma)}$$

For single-qubit states with Bloch vectors $\vec{r}_\rho$ and $\vec{r}_\sigma$:

$$D(\rho, \sigma) = \frac{1}{2}\|\vec{r}_\rho - \vec{r}_\sigma\|_2$$

Trace distance bounds the maximum probability of distinguishing $\rho$ from $\sigma$ via any physical measurement:

$$P_{\text{distinguish}} = \frac{1}{2}(1 + D(\rho, \sigma))$$

### Total Variation Distance (TVD, $\Delta$)
Measures the distance between classical measurement probability mass functions $P$ and $Q$:

$$\Delta(P, Q) = \frac{1}{2}\sum_{x \in \{0, 1\}} |P(x) - Q(x)|$$

---

## 6. Quantum Teleportation & Feed-Forward Corrections

Alice transmits unknown state $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$ to Bob via pre-shared Bell pair $|\Phi^+\rangle_{AB} = \frac{|00\rangle + |11\rangle}{\sqrt{2}}$:

$$|\Psi_{0}\rangle = |\psi\rangle \otimes |\Phi^+\rangle_{AB} = \frac{1}{2}\sum_{c_0, c_1 \in \{0,1\}} |\text{Bell}_{c_1 c_0}\rangle \otimes (X^{c_1} Z^{c_0} |\psi\rangle)$$

Following Alice's Bell-state measurement resulting in classical bits $(c_1, c_0)$, Bob applies conditional unitary feed-forward corrections:

| Alice Outcome ($c_1, c_0$) | Bob's Collapsed State | Bob's Unitary Correction | Final Bob State |
|:---:|:---:|:---:|:---:|
| `00` | $\alpha\|0\rangle + \beta\|1\rangle$ | $I$ (Identity) | $\|\psi\rangle$ |
| `01` | $\alpha\|1\rangle + \beta\|0\rangle$ | $X$ (Bit Flip) | $\|\psi\rangle$ |
| `10` | $\alpha\|0\rangle - \beta\|1\rangle$ | $Z$ (Phase Flip) | $\|\psi\rangle$ |
| `11` | $\alpha\|1\rangle - \beta\|0\rangle$ | $X Z$ (Bit-Phase Flip) | $\|\psi\rangle$ |

---

## 7. Quantum Channels & Kraus Operator Decomposition

Any physical quantum operation or cyber attack channel $\mathcal{E}$ is modeled as a Completely Positive Trace-Preserving (CPTP) map with Kraus operators $\{K_i\}$ satisfying $\sum_i K_i^\dagger K_i = I$:

$$\mathcal{E}(\rho) = \sum_i K_i \rho K_i^\dagger$$

Our framework implements 6 physical quantum channels:
1. **Bit-Flip Channel**: $K_0 = \sqrt{1-p}I, \quad K_1 = \sqrt{p}X$
2. **Phase-Flip Channel**: $K_0 = \sqrt{1-p}I, \quad K_1 = \sqrt{p}Z$
3. **Bit-Phase-Flip Channel**: $K_0 = \sqrt{1-p}I, \quad K_1 = \sqrt{p}Y$
4. **Depolarizing Channel**: $\mathcal{E}(\rho) = (1-p)\rho + \frac{p}{3}(X\rho X + Y\rho Y + Z\rho Z) = (1-\frac{4}{3}p)\rho + \frac{4}{3}p\frac{I}{2}$
5. **Amplitude Damping ($T_1$ decay)**: $K_0 = \begin{pmatrix} 1 & 0 \\ 0 & \sqrt{1-\gamma} \end{pmatrix}, \quad K_1 = \begin{pmatrix} 0 & \sqrt{\gamma} \\ 0 & 0 \end{pmatrix}$
6. **Phase Damping ($T_2$ dephasing)**: $K_0 = \begin{pmatrix} 1 & 0 \\ 0 & \sqrt{1-\lambda} \end{pmatrix}, \quad K_1 = \begin{pmatrix} 0 & 0 \\ 0 & \sqrt{\lambda} \end{pmatrix}$

---

## 8. Quantum State Tomography (QST)

To reconstruct an unknown density matrix $\rho$ without prior knowledge, the receiver performs projective measurements in three mutually unbiased bases:
- **Z-Basis**: Computational measurement $\{|0\rangle, |1\rangle\}$, expectation $\langle Z\rangle = P_Z(0) - P_Z(1)$.
- **X-Basis**: Rotated by Hadamard $H$, measurement $\{|+\rangle, |-\rangle\}$, expectation $\langle X\rangle = P_X(0) - P_X(1)$.
- **Y-Basis**: Rotated by $S^\dagger$ then $H$, measurement $\{|i\rangle, |-i\rangle\}$, expectation $\langle Y\rangle = P_Y(0) - P_Y(1)$.

Reconstructed density matrix:

$$\hat{\rho} = \frac{1}{2}\left(I + \hat{\langle X\rangle}\sigma_x + \hat{\langle Y\rangle}\sigma_y + \hat{\langle Z\rangle}\sigma_z\right)$$

---

## 9. Non-Locality: Bell States & CHSH Inequality

The Clauser-Horne-Shimony-Holt (CHSH) Bell test verifies quantum entanglement and detects untrusted channel tampering:

$$S_{\text{CHSH}} = \langle A_1 B_1 \rangle + \langle A_1 B_2 \rangle + \langle A_2 B_1 \rangle - \langle A_2 B_2 \rangle$$

- **Classical Local Hidden Variable (LHV) Bound**: $|S| \le 2$
- **Tsirelson's Quantum Bound**: $|S| \le 2\sqrt{2} \approx 2.8284$
- Measuring $S > 2$ proves non-classical entanglement; eavesdropping decoheres the state and collapses $S \le 2$.

---

## 10. Fundamental Security Theorems: No-Cloning & Intercept-Resend

### Wootters-Zurek No-Cloning Theorem
Unitary cloning of an unknown quantum state $|\psi\rangle$ is impossible:

$$U(|\psi\rangle \otimes |0\rangle) \ne |\psi\rangle \otimes |\psi\rangle$$

The optimal symmetric Universal Quantum Cloning Machine (UQCM, Bužek-Hillery bound) achieves a maximum cloning fidelity of:

$$F_{\text{cloning}} = \frac{5}{6} \approx 0.8333$$

Any adversary attempting to clone a quantum signature state introduces detectable perturbation with fidelity $F \le 5/6$.

### Intercept-Resend Eavesdropping
If Eve intercepts Alice's qubit and measures it in basis $B_E \in \{Z, X\}$ before re-sending:
- Probability of basis mismatch: $P(\text{mismatch}) = 0.5$
- Conditional error given mismatch: $P(\text{error}|\text{mismatch}) = 0.5$
- Minimum expected Quantum Bit Error Rate: $\text{QBER} = 0.25$ ($25\%$)

---

## 11. Statistical Anomaly Detection via Hoeffding's Inequality

Under finite empirical shot sampling ($N$ shots), empirical frequency $\hat{p}$ fluctuates around true mean $p^*$. Hoeffding's concentration inequality provides an analytical bound without distributional assumptions:

$$P(|\hat{p} - p^*| \ge \epsilon) \le 2\exp(-2N\epsilon^2)$$

For observed deviation $\epsilon = |\hat{p} - p^*|$ with $N$ shots:
- Upper bound on false alarm probability: $\alpha_{\text{bound}} = 2\exp(-2N\epsilon^2)$
- Statistical anomaly confidence: $C = 1 - \alpha_{\text{bound}}$
- Decision rule: If $\epsilon > \epsilon_{\text{threshold}}$ and $C \ge 99.0\%$, the signature is flagged as an active attack.

---

## 12. Post-Quantum Cryptography (PQC) vs Quantum Digital Signatures (QDS)

| Dimension | Classical Cryptography (RSA/ECDSA) | Post-Quantum Cryptography (NIST FIPS 204/205) | Quantum Digital Signatures (QDS) |
|---|---|---|---|
| **Security Foundation** | Computational (Factoring / DLOG) | Computational (Hard lattice/hash problems) | **Laws of Quantum Mechanics (Information-Theoretic)** |
| **Vulnerable to Quantum Computers?** | **YES** (Broken by Shor's Algorithm) | NO (Believed secure against known algorithms) | **NO (Physical No-Cloning theorem)** |
| **Side-Channel Susceptibility** | High (Power, timing, fault injection) | Moderate to High (Complex lattice polynomial ops) | **Negligible on state (Collapse upon unauthorized tap)** |
| **Hardware Requirements** | Standard CPU / ASIC | Standard CPU / Embedded chip | Quantum optical channel, Bell pairs, single-photon detectors |
| **Eavesdropping Detectability** | Undetectable during transit | Undetectable during transit | **Immediately detectable via QBER & decoherence** |
