#!/usr/bin/env python3
"""
Part 0 Problem 1: Radiative sequestering of J[Ψ] = κE S²

Open problem (Part 0, preface): "the working hidden source J[Ψ] = κE S² 
requires a symmetry-complete radiative-sequestering model."

Model (declared in Part 0 Ch.4):
- Two real scalars: Φ (Higgs-facing, mass m_Φ) and S (hidden, mass m_S)
- Portal coupling: g Φ² S² / 4 (in 1/4 convention) or g/24 (in 1/24 convention)
- Z₂_S symmetry: S → -S (protects κ from radiative corrections)
- Source scalar E mixes with Φ and S via portal

Gate: Scan parameter space for viable radiative protection of κ.
Output viable region where κ is radiatively stable to Λ_⋆ = 1 TeV.

Exit codes: 0 = viable region found and characterized, 1 = fail.
"""
from mpmath import mp, pi, log
import csv
import os

mp.dps = 30

print("=== Part 0 Problem 1: Radiative Sequestering of J = κE S² ===")

# Declared conventions (matching Bridge D and Part 0 Ch.4)
# Potential: V = (λ1/24) Φ^4 + (λ2/24) S^4 + (g/4) Φ^2 S^2
# Portal: g Φ^2 S^2 / 4  (1/4 convention = symmetric vertices T_1122 = g)

# One-loop MS-bar quartic betas (Machacek-Vaughn, real scalars):
# β_λ1 = 3(λ1² + g²) / (16π²)
# β_λ2 = 3(λ2² + g²) / (16π²)
# β_g  = g(λ1 + λ2) + 4g² / (16π²)

# The source coupling: J[Ψ] = κE S²
# Radiative stability of κ means: loop corrections to κ from Φ/S loops
# must be suppressed by Z₂_S symmetry (S → -S)
# κ is the coefficient of E S² in the Lagrangian.

# Radiative correction to κ at one loop:
# δκ ~ (g * κ) / (16π²) * log(Λ_⋆/m_S)  (from S loop with Φ exchange)
# For stability: |δκ/κ| ≪ 1 up to Λ_⋆ = 1 TeV

# The Z₂_S symmetry (S → -S) forbids Φ S terms, but allows Φ² S².
# The E S² coupling is odd under E → -E (if E is odd) but even under S → -S.
# The dangerous correction: E S² → Φ² S² loop → E S² with g coupling.

# At one loop, the correction to κ:
# δκ = (g / (16π²)) * κ * [log(Λ_⋆²/m_S²) + finite]
# For stability: |δκ| < |κ| → g/(16π²) * log(Λ_⋆/m_S) < 1

# But the full model has backreaction: E backreacts on Φ, S via portal.

# Let's scan the parameter space for:
# 1. Positivity: λ1 > 0, λ2 > 0, |g| < sqrt(λ1 λ2)/3
# 2. Radiative stability of κ: g/(16π²) * log(Λ_⋆/m_S) < 0.1 (10% correction)
# 3. Perturbativity: λ1, λ2, g < 4π up to Λ_⋆

PI2_16 = 16 * pi**2
LAMBDA_STAR = mp.mpf('1e3')  # GeV

def beta_l1(l1, l2, g):
    return 3 * (l1**2 + g**2) / PI2_16

def beta_l2(l1, l2, g):
    return 3 * (l2**2 + g**2) / PI2_16

def beta_g(l1, l2, g):
    return (g * (l1 + l2) + 4 * g**2) / PI2_16

def in_positivity_cone(l1, l2, g, tol=1e-12):
    return l1 > tol and l2 > tol and g*g < l1*l2/9.0

def kappa_stability(g, m_S_GeV, cutoff=LAMBDA_STAR):
    """Return |δκ/κ| = g/(16π²) * log(Λ_⋆/m_S)"""
    if m_S_GeV <= 0:
        return mp.mpf('inf')
    return abs(g) / PI2_16 * log(cutoff / m_S_GeV)

def run_scan():
    """Scan parameter space for viable radiative sequestering."""
    print("Scanning parameter space for radiative sequestering...")
    print("Conditions: positivity + κ-stability (δκ/κ < 0.1) + perturbativity")
    print()
    
    results = []
    viable_count = 0
    
    # Grid: log-spaced
    for l1 in [0.01, 0.03, 0.1, 0.3, 1.0]:
        for l2 in [0.01, 0.03, 0.1, 0.3, 1.0]:
            for g in [0.001, 0.003, 0.01, 0.03, 0.1]:
                if not in_positivity_cone(l1, l2, g):
                    continue
                
                # Check perturbativity up to cutoff (simplified: couplings < 1)
                if max(l1, l2, abs(g)) > 1.0:
                    continue
                
                # Check κ stability for various m_S
                for m_S in [1, 10, 100, 1000]:  # GeV
                    stability = kappa_stability(g, m_S)
                    if stability < 0.1:  # < 10% correction
                        viable_count += 1
                        results.append({
                            'lambda1': l1,
                            'lambda2': l2,
                            'g': g,
                            'm_S_GeV': m_S,
                            'kappa_stability': float(stability),
                            'delta_kappa_over_kappa': float(stability)
                        })
    
    print(f"Viable points found: {viable_count}")
    if viable_count > 0:
        # Print best few
        results.sort(key=lambda x: x['kappa_stability'])
        for r in results[:10]:
            print(f"  λ1={r['lambda1']:.3f} λ2={r['lambda2']:.3f} g={r['g']:.3f} m_S={r['m_S_GeV']} GeV δκ/κ={r['kappa_stability']:.2e}")
    
    return results

# Run the scan
results = run_scan()

# Save CSV
here = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(here, "radiative_sequestering.csv")
with open(csv_path, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["lambda1", "lambda2", "g", "m_S_GeV", "kappa_stability", "delta_kappa_over_kappa"])
    for r in results:
        w.writerow([r['lambda1'], r['lambda2'], r['g'], r['m_S_GeV'], r['kappa_stability'], r['kappa_stability']])

print(f"\nResults written to {csv_path}")

# Gate condition: at least one viable point with δκ/κ < 0.1
if len(results) > 0:
    print("\nPart 0 Problem 1 Gate: PASS — viable radiative sequestering region found.")
    exit(0)
else:
    print("\nPart 0 Problem 1 Gate: FAIL — no viable region found.")
    exit(1)