# Mentis-Q: Threat Model & Quantum Attack Vector Specifications

## 1. Threat Model & Adversarial Assumptions

In accordance with published Quantum Digital Signature (QDS) security frameworks (e.g., Gottesman & Chuang 2001, Clarke et al. 2012, Arrazola & Neduvath 2014), Mentis-Q defines an adversarial threat model with the following boundaries:

1. **Adversary Capabilities**:
   - The adversary (Eve) can intercept classical communications over the public channel.
   - Eve can interact with or measure quantum states during transmission, bounded by the **Wootters-Zurek No-Cloning Theorem**.
   - Eve possesses unbounded classical and quantum computational power to execute optimal measurements (POVMs) on intercepted states.
2. **Security Enclave**:
   - The signer's (Alice's) private key generator and internal state preparation hardware are physically trusted.
   - The verifiers' (Bob's and Charlie's) local quantum memory registries $\mathcal{M}$ are physically secure and isolated from unauthorized access prior to verification.
   - Authenticated classical channels are assumed for distribution coordination (e.g., Bell measurement feedforward).

---

## 2. Attack Vectors & Physical Derivations

Mentis-Q formally models and simulates 6 distinct attack vectors:

### Vector 1: Forgery by Random Guess
- **Adversarial Mechanism**: Eve attempts to forge a signature for bit $b$ without holding any public-key quantum states or knowledge of the private key. For each of the $L$ positions, Eve randomly guesses a basis $\text{basis}_i \in \{Z, X, Y\}$ and a bit value $\text{bit}_i \in \{0, 1\}$ uniformly with probability $1/6$.
- **Theoretical Derivation**:
  - Probability Eve guesses the correct basis: $P(\text{basis match}) = 1/3$. In this case, probability of bit mismatch is $P(\text{bit error} \mid \text{basis match}) = 1/2$ (since bit is drawn uniformly).
  - Probability Eve chooses a wrong basis: $P(\text{basis mismatch}) = 2/3$. By mutual unbiasedness of the Pauli bases, the projective measurement outcome is completely random: $P(\text{bit error} \mid \text{basis mismatch}) = 1/2$.
  - **Expected Per-Copy Mismatch**:
    $$\mathbb{E}[m] = \frac{1}{3}\left(\frac{1}{2}\right) + \frac{2}{3}\left(\frac{1}{2}\right) = \frac{1}{6} + \frac{2}{6} = \frac{1}{2} = 0.50 \quad (50.0\%)$$
- **Detection**: The measured mismatch rate $m \approx 0.50 \gg s_v = 0.250$.
- **Detector Fired**: `threshold` (Decision: `REJECT`).

---

### Vector 2: Forgery by Measure-and-Guess on Public-Key Copies
Eve holds or intercepts copies of the public-key quantum states $|\psi_{b,i}\rangle$ intended for a verifier and performs physical quantum measurements before Alice releases her private key:

#### Strategy A: Single-Basis Measurement
- **Mechanism**: Eve measures all $L$ intercepted states in a single fixed basis (e.g., computational basis $Z$).
- **Theoretical Derivation**:
  - Probability the state was prepared in basis $Z$: $1/3$. Eve's measurement is deterministic: error probability $= 0$.
  - Probability the state was prepared in $X$ or $Y$: $2/3$. By unbiasedness, Eve's measurement yields an uncorrelated bit: error probability $= 1/2$.
  - **Expected Per-Copy Mismatch**:
    $$\mathbb{E}[m] = \frac{1}{3}(0) + \frac{2}{3}\left(\frac{1}{2}\right) = \frac{1}{3} \approx 33.33\%$$
- **Detection**: Since $\mathbb{E}[m] \approx 0.3333 > s_v = 0.250$, single-basis measure-and-guess is reliably rejected.
- **Detector Fired**: `threshold`.

#### Strategy B: Optimal Multi-Basis POVM (Literature Bound)
- **Mechanism**: Eve performs an optimal unambiguous state discrimination or Minimum Error Positive Operator-Valued Measure (POVM) across the 3 mutually unbiased Pauli bases.
- **Cited Literature Assumption**:
  - *Reference*: Clarke et al., Nature Communications 3, 1174 (2012); Arrazola & Neduvath, Phys. Rev. A 90, 042318 (2014).
  - Under an optimal POVM on a single copy of an unknown state drawn uniformly from the 6 Pauli eigenstates, the maximum achievable probability of correctly identifying both basis and bit is bounded by:
    $$P_{\text{guess}}^{\max} \le \frac{1}{2}\left(1 + \frac{1}{\sqrt{3}}\right) \approx 78.87\%$$
  - Consequently, the minimal per-copy error probability is bounded from below:
    $$m_{\min} = 1 - P_{\text{guess}}^{\max} = \frac{1}{2}\left(1 - \frac{1}{\sqrt{3}}\right) \approx 21.13\%$$
- **Detection**: Because the acceptance threshold is calibrated at $s_a = 0.100 < 0.2113$, any signature constructed from optimal POVM measurements will exhibit an empirical mismatch rate exceeding $s_a$ with high probability (governed by the Hoeffding bound).
- **Detector Fired**: `threshold`.

---

### Vector 3: Impersonation Attack
- **Mechanism**: A rogue entity claiming to be Alice generates a signature using arbitrary or synthetic quantum states without authentic pre-shared quantum public keys.
- **Detection**: When Bob measures his stored legitimate public-key states against the rogue classical private key claims, the projective outcomes are uncorrelated, yielding an empirical mismatch rate $m \approx 0.50 > s_v$.
- **Detector Fired**: `threshold`.

---

### Vector 4: Channel Manipulation & Intercept-Resend
- **Mechanism**: An active eavesdropper intercepts the distribution channel between Alice and Bob/Charlie, subjecting the flying qubits to:
  1. *Depolarizing Noise*: $\mathcal{E}(\rho) = (1 - p)\rho + \frac{p}{3}(X\rho X + Y\rho Y + Z\rho Z)$.
  2. *Intercept-Resend*: Eve intercepts each flying qubit, measures it in an arbitrary basis, and resends a reconstructed state to Bob.
- **Physical Consequence**: Intercept-resend collapses quantum superposition states, inducing a minimum Quantum Bit Error Rate of $\text{QBER} \ge 25\%$, which Bob immediately detects during channel characterization or verification.
- **Detector Fired**: `threshold`.

---

### Vector 5: Replay Attack (Database Nonce Store)
- **Mechanism**: Eve eavesdrops on a valid signed transaction $(M, \text{Sig}(M), \text{nonce})$ transmitted by Alice, captures the message and classical signature, and subsequently resubmits the exact same signature in a subsequent transaction attempt.
- **Countermeasure & Detection**:
  - The backend maintains an SQLite-backed transactional nonce registry table: `qds_nonces`.
  - Each signature is bound to a cryptographically random `nonce`, a `key_id`, a `signature_id`, an issuance timestamp, and a Time-To-Live expiration window (`expires_at`, default 300 seconds).
  - **First Submission**: Evaluated, marked `is_consumed = TRUE`, and accepted.
  - **Second Submission**: When the replayed nonce is queried, the system detects `is_consumed == TRUE`. The transaction is immediately aborted with a high-severity security audit event logged to `logs`.
- **Detector Fired**: `nonce` (Decision: `REJECT`).

---

### Vector 6: Unauthorized Verification & Sliding-Window Rate Limiting
- **Mechanism**: An adversary repeatedly queries the verification endpoint with perturbed messages or crafted state guesses in an effort to extract private key parameters through side-channel timing or statistical leakage.
- **Countermeasure & Detection**:
  - **Verifier Token Registry (`qds_verifiers`)**: Each valid verifier must present a cryptographic API authorization token. Unregistered verifier IDs or invalid tokens are rejected with HTTP 403 / `detector_fired = "authorization"`.
  - **Sliding-Window Rate Limiter (`qds_rate_limits`)**: Tracks client requests within a continuous time window (e.g., maximum 5 verification requests per 60-second window per client IP/ID).
  - Exceeding the rate limit immediately triggers access lockout and flags a high-priority security alert.
- **Detector Fired**: `rate-limit` (Decision: `REJECT`).

---

## 3. Threat Classification & Detector Routing

Every verification attempt in Mentis-Q is processed through a deterministic detector dispatch pipeline:

| Detector | Trigger Condition | Primary Action | Default Threat Score |
|:---:|:---:|:---:|:---:|
| **`authorization`** | Client token missing or unverified in `qds_verifiers` | Immediate HTTP 403 abort | 1.00 (Critical) |
| **`rate-limit`** | Client exceeds allowed request count in sliding window | Client lockout for TTL window | 0.95 (Critical) |
| **`nonce`** | Nonce expired or already marked `is_consumed` in `qds_nonces` | Abort replay transaction | 0.90 (High) |
| **`threshold`** | Projective measurement mismatch rate $m > s_a$ ($m > 0.100$) | Reject signature for bit $b$ | Scaled by $m$ (Medium to High) |
