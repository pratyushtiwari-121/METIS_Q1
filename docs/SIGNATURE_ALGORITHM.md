# Quantum Digital Signature (QDS) Algorithm & Verification Protocol

## 1. Protocol Overview

Mentis-Q implements a full **Quantum Digital Signature (QDS)** scheme based on quantum public-key distribution via teleportation, symmetric multi-verifier state storage, and projective measurement verification.

Unlike classical digital signatures (e.g., RSA, ECDSA) whose security relies on unproven computational complexity assumptions vulnerable to Shor's algorithm, QDS security is grounded in the **fundamental laws of quantum mechanics** (the No-Cloning Theorem and the uncertainty principle of non-orthogonal quantum states).

```
                            [ Alice (Signer) ]
                                    │
           ┌────────────────────────┴────────────────────────┐
           ▼                                                 ▼
[ Bell Pair Teleportation ]                       [ Classical Keygen ]
Public Keys: |ψ_{b,i}⟩ ∈ {Pauli Alphabet}         Private Keys: (basis, bit)
           │                                                 │
           ▼                                                 ▼
[ Verifier Quantum Memories ]                     [ Signature Release ]
Bob & Charlie store |ψ⟩ states                    Alice transmits (basis, bit) + SHA-256
           │                                                 │
           └────────────────────────┬────────────────────────┘
                                    ▼
                      [ Projective Verification ]
                  Measure stored states in claimed basis
                  Calculate Mismatch Rate: m = N_err / L
                                    │
               ┌────────────────────┴────────────────────┐
               ▼                                         ▼
         m ≤ s_a (Accept)                         m > s_a (Reject)
```

---

## 2. Pauli Alphabet & Key Generation

### A. The Six Pauli Eigenstates Alphabet
The public quantum states are selected from the six eigenstates of the three mutually unbiased Pauli operators ($\sigma_z, \sigma_x, \sigma_y$):

| Basis | Bit | State Label | State Vector $|\psi\rangle$ | Bloch Coordinates $(r_x, r_y, r_z)$ |
|:---:|:---:|:---:|:---:|:---:|
| $Z$ (Computational) | 0 | $\|0\rangle$ | $\begin{pmatrix} 1 \\ 0 \end{pmatrix}$ | $(0, 0, 1)$ |
| $Z$ (Computational) | 1 | $\|1\rangle$ | $\begin{pmatrix} 0 \\ 1 \end{pmatrix}$ | $(0, 0, -1)$ |
| $X$ (Hadamard / Diagonal) | 0 | $\|+\rangle$ | $\frac{1}{\sqrt{2}}\begin{pmatrix} 1 \\ 1 \end{pmatrix}$ | $(1, 0, 0)$ |
| $X$ (Hadamard / Diagonal) | 1 | $\|-\rangle$ | $\frac{1}{\sqrt{2}}\begin{pmatrix} 1 \\ -1 \end{pmatrix}$ | $(-1, 0, 0)$ |
| $Y$ (Circular) | 0 | $\|+i\rangle$ | $\frac{1}{\sqrt{2}}\begin{pmatrix} 1 \\ i \end{pmatrix}$ | $(0, 1, 0)$ |
| $Y$ (Circular) | 1 | $\|-i\rangle$ | $\frac{1}{\sqrt{2}}\begin{pmatrix} 1 \\ -i \end{pmatrix}$ | $(0, -1, 0)$ |

Every state is normalized ($\langle\psi|\psi\rangle = 1$) and satisfies the eigenvalue relation $\sigma_k |\psi\rangle = (-1)^b |\psi\rangle$.

### B. Private and Public Key Construction
For a configurable security parameter $L$ (default $L = 64$ or $L = 128$ qubit copies) and for each possible future message bit $b \in \{0, 1\}$:

1. **Private Key ($\text{SK}_b$)**:
   Alice draws $L$ independent, uniformly distributed random pairs:
   $$\text{SK}_b = \left\{ (\text{basis}_{b, i}, \text{bit}_{b, i}) \right\}_{i=1}^{L}, \quad \text{where } \text{basis}_{b,i} \in \{Z, X, Y\}, \; \text{bit}_{b,i} \in \{0, 1\}$$
2. **Public Key ($\text{PK}_b$)**:
   The corresponding sequence of $L$ quantum states:
   $$\text{PK}_b = \left\{ |\psi(\text{basis}_{b, i}, \text{bit}_{b, i})\rangle \right\}_{i=1}^{L}$$

The total private key consists of $\text{SK} = (\text{SK}_0, \text{SK}_1)$, and the total public key consists of $\text{PK} = (\text{PK}_0, \text{PK}_1)$.

---

## 3. Quantum Public Key Distribution (QPKD) via Teleportation

To distribute quantum public keys to multiple verifiers (Bob and Charlie) without direct physical state transport, Alice uses **quantum teleportation** supported by shared Einstein-Podolsky-Rosen (EPR) Bell pairs:

1. **Entanglement Sharing**:
   For each position $i \in \{1, \dots, L\}$, an entangled Bell pair $|\Phi^+\rangle = \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$ is prepared, with qubit $A$ given to Alice and qubit $B$ sent to Verifier $V_k$.
2. **Bell State Measurement (BSM)**:
   Alice performs a joint projective measurement on the public key qubit $|\psi\rangle$ and her Bell qubit $A$ in the Bell basis:
   $$\{|\Phi^+\rangle, |\Phi^-\rangle, |\Psi^+\rangle, |\Psi^-\rangle\}$$
   yielding classical outcome bits $(c_0, c_1) \in \{0, 1\}^2$.
3. **Classical Feedforward & Pauli Correction**:
   Alice transmits $(c_0, c_1)$ over an authenticated classical channel to Verifier $V_k$.
   Verifier $V_k$ applies the corresponding Pauli correction operator to qubit $B$:
   $$U_{\text{correction}} = X^{c_1} Z^{c_0}$$
   Recovering the exact state: $|\psi_{\text{out}}\rangle = |\psi\rangle$ (in the noiseless regime, $F = 1.0$).
4. **Quantum Memory Storage**:
   Each verifier securely stores their individual sequence of received states in modeled local quantum memory registers $\mathcal{M}_{V_k}^{(0)}$ and $\mathcal{M}_{V_k}^{(1)}$.

---

## 4. Signing Protocol

When Alice wishes to sign a classical message $M \in \{0, 1\}^*$:

1. **Cryptographic Binding**:
   Alice calculates the message digest:
   $$H = \text{SHA-256}(M)$$
2. **Bit Mapping**:
   The least significant bit $b = \text{int}(H[-1], 16) \pmod 2 \in \{0, 1\}$ (or block-wise bit mapping) determines which key component is signed.
3. **Classical Signature Release**:
   Alice releases the classical string $\text{SK}_b$:
   $$\text{Sig}(M) = \left( b, \; \text{SK}_b, \; H \right)$$
   Alice's signature is entirely classical at transmission time, allowing instantaneous broadcasting over standard classical networks.

---

## 5. Verification Protocol

When Verifier $V_k$ receives $(M, \text{Sig}(M))$:

1. **Cryptographic Binding Verification**:
   The verifier independently computes $H' = \text{SHA-256}(M)$ and verifies that $H' == H$ and $b' == b$. If invalid, verification immediately halts with rejection.
2. **Projective Quantum Measurement**:
   For each position $i = 1, \dots, L$:
   - The verifier retrieves the stored quantum state $|\phi_i\rangle$ from memory $\mathcal{M}_{V_k}^{(b)}$.
   - The verifier measures $|\phi_i\rangle$ in the claimed basis $\text{basis}_{b,i} \in \{Z, X, Y\}$.
   - Measurement yields outcome bit $r_i \in \{0, 1\}$.
   - If $r_i \neq \text{bit}_{b,i}$, an error (mismatch) is recorded:
     $$e_i = \begin{cases} 1, & \text{if } r_i \neq \text{bit}_{b,i} \\ 0, & \text{if } r_i = \text{bit}_{b,i} \end{cases}$$
3. **Mismatch Rate Calculation**:
   The empirical mismatch rate $m$ across all $L$ positions is:
   $$m = \frac{1}{L} \sum_{i=1}^{L} e_i$$

---

## 6. Configurable Dual-Threshold Decision Framework

To prevent both false rejections under physical channel noise and repudiation/forgery attacks, Mentis-Q employs a dual-threshold framework:

$$0 \le s_a < s_v < 0.50$$

- **$s_a$ (Acceptance Threshold, default $0.100$)**:
  Signatures with $m \le s_a$ are declared **VALID** and accepted.
- **$s_v$ (Verification Threshold, default $0.250$)**:
  Signatures with $m > s_v$ are declared **REJECTED / ATTACK DETECTED**.
- **Middle Zone ($s_a < m \le s_v$)**:
  Signatures falling into the intermediate band cannot be guaranteed against repudiation or transferability disputes between verifiers. In Mentis-Q, the middle zone triggers **DISPUTE / REJECTION** to guarantee strict verifier consensus.

### Threshold Properties
- **Honest Noiseless Case**: Under ideal conditions ($p_h = 0$), $m = 0.0 \le s_a \implies 100\%$ acceptance.
- **Honest Noisy Channel**: For channel error rate $p_h < s_a$ (e.g. $p_h = 0.02$), honest signatures remain accepted with high probability.
- **Random Guess Forgery**: An adversary guessing bases and bits uniformly at random incurs an expected error of $\mathbb{E}[m] = 0.50 \gg s_v \implies$ rejected.
- **Measure-and-Guess Forgery**: An adversary measuring public key copies in a single basis incurs an expected error of $\mathbb{E}[m] = 1/3 \approx 0.3333 > s_v \implies$ rejected.
