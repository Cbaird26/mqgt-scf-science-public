# EMP-01 Preregistered Interferometric Protocol
## For the MQGT–SCF Rate-Modulated GKSL Sector

**Version:** 1.0 (corrected edition, 11 September 2026)  
**Hash:** `sha256:bb6859bf3d4f81082a4ac57970ed019fe8808148c96c7cf58a5a3b0c4e36bf27` (corrected note PDF)  
**Status:** Preregistered — not yet run. All analysis predicates frozen.

---

## 1. Apparatus Specification (Frozen)

| Parameter | Value | Unit | Notes |
|-----------|-------|------|-------|
| Interferometer type | Mach–Zehnder (optical or matter-wave) | — | Two-path |
| Path separation Δx | [TBD by lab] | m | Must satisfy ℓ_c ≪ Δx |
| Monitor arm flight time T | [TBD by lab] | s | Identical on both arms |
| Pointer monitor | Twin monitors (one per arm) | — | Identical, differential readout |
| Monitor coupling | Place-3: λ(ΔE) on which-path projector | — | ΔE = E_L − E_R |
| Bath | Thermal bosonic | — | Ohmic J(ω)=η_bath ω e^(−ω/ω_c) |
| Temperature T_bath | [TBD by lab] | K | Must be stable; monitored for N3 |
| Scalar field E | Independent actuator + meter | eV | SI-convertible units |
| Detector | Photon/atom counting, phase scan | — | N_±(ϕ) = ½N_tot(1±V cos ϕ) |

**Coupling Hamiltonian (corrected):**
```
H_SR = λ(ΔE) |L⟩⟨L| ⊗ B,   B = Σ_q (g_q b_q + g_q^* b_q^†)
```
with ΔE ≡ E(x_L) − E(x_R), λ(0) = 1.

---

## 2. Four Run Types (Preregistered)

| ID | Coupler | Scalar Pattern | Place-3 Prediction for α |
|----|---------|----------------|---------------------------|
| N0 | Off | Lab as found | α = 0 (monitor-off baseline V_QM^(off)) |
| N1 | On | Common-mode ΔE = 0 | α = 0 (monitor-on, E=0 reference V_QM^(on)) |
| N2 | On | Differential E_L = E_0+δE, E_R = E_0 | α = ½Γ_φ^(0)T(λ(ΔE)²−1) |
| N3 | On | δE = 0, bath T or η_bath changed | α follows Γ_φ^(0)(T_bath), not new η |

---

## 3. Estimator & Baseline Declaration

- **Primary baseline (default):** Monitor-on, ΔE=0 (row N1).  
  `V̂_QM = V̂_N1`, `α̂ = −ln(V̂/V̂_N1)`.  
  Row N1 is the null by construction (λ(0)=1).

- **Alternative baseline (optional, declared per row):** Monitor-off (row N0).  
  `V̂_QM = V̂_N0`, `α̂ = −ln(V̂/V̂_N0)`.  
  Then `α̂_N2 = ½Γ_φ^(0)T λ(ΔE)²` (no −1).  
  **Baseline choice must be recorded per row in the input table.**

- **N0 as coupler-off offset meter:**  
  Expected `α̂_N0 = ½Γ_φ^(0)T` (positive offset from monitor-on reference).  
  If N0 baseline used, N0 itself is the reference (α=0 by definition).

---

## 4. Power Analysis (Pre-registered)

Linearized signal for small x = η ΔE:
```
α ≃ ½ Γ_φ^(0) T η ΔE
```

Shot-noise idealization (V≈1, N_tot total counts):
```
Var(α̂) ≃ 1/N_tot
```

Detection at significance z:
```
N_tot ≥ 4 z² / (Γ_φ^(0) T η ΔE)²
```

**Worked illustration only (not the final numbers):**
- Γ_φ^(0) = 10³ s⁻¹
- T = 10⁻⁴ s
- |η ΔE| ∼ 10⁻²
- α ∼ 5×10⁻⁴
- N_tot ≳ 4×10⁸ for z = 5

**Final N_tot, z, η, ΔE must be declared before unblinding N2.**

---

## 5. Nuisance Budget (Pre-registered)

Systematic contributions to σ_α that must be measured from N0/N1 residuals:
- Source drift between N0 and N2
- Pointing and overlap fluctuations
- Coupler-on thermal load (caught by N3)
- Path-length wander mistaken for contrast loss (always scan ϕ)
- Actuator systematics (coil Zeeman, orientation wander)
- Post-hoc cuts

Budget inequality:
```
σ_α,sys² + σ_α,stat² ≤ (α_min / z)²
```
where α_min is the smallest Place-3 signal claimed to matter.

---

## 6. Kill-Plot (Preregistered)

| Axis | Specification |
|------|---------------|
| Horizontal | Independently metered E_L − E_R (ΔE), with coupler-off flag at 0 |
| Vertical | α̂ with fit-covariance error bars |
| Symbols | N0 (▲), N1 (●), N2 (■), N3 (◆) |

**Survival criteria (all must hold):**
1. N0 sits on its declared baseline band (monitor-off: α≈0 or named offset).
2. N1 sits on 0 (monitor-on, ΔE=0 null) inside preregistered band.
3. N2 is monotone in ΔE, consistent with single λ(ΔE)²−1 (or measured h(ΔE)).
4. N3 scales with T_bath (or measured J(ω→0)) at fixed ΔE.
5. Blinded half-split (frozen before N2 unblinding) does not move slope outside preregistered interval.

**Death conditions (any one kills Place-3):**
- N0 already slumps (coupler-off contrast loss).
- N1 tracks N2 (common-mode mimics differential).
- N2 is a post-hoc blob fitted after the fact.
- N3 is silent while N2 "sees" η.
- Contrast moves with actuator current when coupler is capped (optical/mechanical decoupling).

---

## 7. Analyzer Fail-Closed Predicate

The analyzer **must print FAIL and must not emit an η estimate** if any predicate is true:

| # | Predicate | Notes |
|---|-----------|-------|
| 1 | Phase not scanned (phase_scanned = 0) | Mandatory fringe scan |
| 2 | Any N2 row with coupler = 0 | Coupler must be on for signal |
| 3 | Missing independent E metrology, or E computed from V̂ | Circular inference forbidden |
| 4 | \|α̂_N0\| > α_N0^max (preregistered band) | Coupler-off integrity |
| 5 | \|α̂_N1\| > α_CM^max (preregistered null band) | Common-mode null integrity |
| 6 | Inequality (budget) not satisfied from N0/N1 residuals | Nuisance budget exceeded |

**On FAIL:** Print FAIL and first failed predicate. Do not print slope.

---

## 8. Independent E Metrology (Required)

| Requirement | Specification |
|-------------|---------------|
| Actuator | Named device (coil, piezo, optical, etc.) with SI-convertible output |
| Meter | Independent device (NV center, atomic clock, SQUID, etc.) |
| Units | eV or SI (V/m, T, etc.) with traceable calibration |
| Timing | Synchronous with contrast acquisition |
| Blinding | Actuator and meter readings frozen before contrast unblinding |

**E must not be inferred from V̂.** Circular inference = automatic FAIL.

---

## 9. Data & Code Availability

- **Protocol hash:** This document (SHA-256 above) frozen at preregistration.
- **Analysis code:** `emp01_analyzer.py` (to be deposited with same hash).
- **Data format:** CSV with columns: `row_id, coupler, E_L, E_R, E_unit, T, T_bath, N_tot, V_hat, V_hat_err, baseline, phase_scanned`.
- **Repository:** [TBD — Zenodo deposit upon preregistration]

---

## 10. Corrections Applied (from 11 Sep 2026 note)

| Issue | Original | Corrected |
|-------|----------|-----------|
| Common-mode null | Single monitor, λ(E) on L only | Twin monitors, λ(ΔE) with ΔE = E_L−E_R |
| Baseline ambiguity | "if desired" E=0 clause | Explicit V_QM^(on) vs V_QM^(off); N1 is null |
| Factor of 2 in Γ_φ^(0) | 2π η_bath k_B T | 4π η_bath k_B T (coherence rate = 2π η_bath k_B T) |

---

**End of Preregistered Protocol.**  
**Next step:** Deposit to OSF/Zenodo with frozen hash. Execute only from frozen sheet.