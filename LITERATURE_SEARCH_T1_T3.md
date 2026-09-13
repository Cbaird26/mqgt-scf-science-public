# Literature Search Summary for T-1 and T-3

## T-1: α⁻¹ Volume-Ratio Identity (Hopf Fibration S¹→S⁹→CP⁴)

### Current TUFT Formula (from audit Section 3.1, Eq. 11)
```
α⁻¹ = (9/(8π⁴)) × (π⁵/1920)^(1/4) = 137.036082448...
```
CODATA 2022: α⁻¹ = 137.035999177(21)
Current deviation: 8.327×10⁻⁵ (≈ 3,970σ)

### Target
Achieve ≥8 correct digits (rel. dev. < 10⁻⁸)

### Key References from Corpus

1. **J. L. Nielsen**, "The Topological Unified Field Theory on the Complex Hopf Fibration" (2026)
   - Source: `371648` in corpus, arXiv/historical
   - Defines Hopf fibration S¹ → S²ⁿ⁺¹ → CPⁿ with n=4 (S¹→S⁹→CP⁴)
   - Formula Eq. (11): α⁻¹ = (9/(8π⁴)) × (π⁵/1920)^(1/4)

2. **M. Reuter & F. Saueressig**, "Renormalization Group Flow of Quantum Gravity in the Einstein-Hilbert Truncation", arXiv:hep-th/0110054
   - Referenced for FRG methodology

3. **D. Litim**, "On fixed points of quantum gravity", arXiv:hep-th/0606044
   - FRG methodology reference

4. **D. Benedetti**, "Asymptotic safety goes on shell", arXiv:1107.3110

### Required Correction for T-1
The current formula gives 6 correct digits. Need to derive the exact volume-ratio identity for:
```
Vol(S¹) × Vol(S⁹) / Vol(CP⁴) × (topological factor)
```
Where:
- Vol(S¹) = 2π
- Vol(S⁹) = 2π⁵/12 = π⁵/12 (with standard round metric)
- Vol(CP⁴) = π⁴/24
- Hopf fibration structure: S¹ → S⁹ → CP⁴

The factor 1920 in the current formula suggests a combination of volumes and topological invariants (Chern classes, Euler characteristics). The missing 2 digits likely come from:
- Exact Euler characteristic of CP⁴: χ(CP⁴) = 5
- Pontryagin classes of S⁹
- Exact Hopf invariant normalization
- Possible π⁴ vs π⁵ factors from Euler class integration

### Literature to Search
- **Borel & Serre**, "Corners and Arithmetic Groups" - volume of symmetric spaces
- **Berger**, "A Panoramic View of Riemannian Geometry" - volumes of spheres/CPⁿ
- **Gilkey**, "Invariance Theory, the Heat Equation, and the Atiyah-Singer Index Theorem"
- **Atiyah & Singer**, "The Index of Elliptic Operators" - spectral geometry of Hopf fibrations
- **Freed & Uhlenbeck**, "Instantons and Four-Manifolds" - Chern classes of Hopf bundles

---

## T-3: S⁷ Beltrami Spectral Determinant (S7, S7' Constants)

### Current TUFT Constants (from audit Eq. 17)
```
dφ_univ = α × exp(-α ζ(3)·13/(24π) - α² ζ(5)/(4π²) - α³ S7/56 - α⁴ S7'/16)
S7 = 1.748452 (coefficient of α³/56)
S7' = 0.41364  (coefficient of α⁴/16)
```

These are quoted as "paper-quoted spectral constants" - not derived in the paper.

### Beltrami Operator on S⁷
The Beltrami operator B = ⋆d on differential forms on S⁷.
- Eigenvalues related to Hodge Laplacian on p-forms
- Spectral determinant det'(B) = exp(-ζ'_B(0))
- Heat kernel expansion: Tr(e^{-tB²}) ~ (4πt)^(-7/2) Σ a_k t^k
- a_4 coefficient determines ζ'_B(0) for spectral determinant

### Required Computation for T-3
Compute the spectral determinant of the Beltrami operator on S⁷ (round metric) to derive:
- S7 = coefficient of α³/56 in universal phase
- S7' = coefficient of α⁴/16 in universal phase

### Key References for T-3

1. **Dowker**, "Heat Kernel Coefficients for the Laplacian on Spheres" - a_k coefficients on Sⁿ
2. **Gilkey**, "Invariance Theory..." - heat kernel coefficients for Hodge Laplacian on forms
3. **Kirsten**, "Spectral Functions in Mathematics and Physics" - spectral determinants on spheres
4. **Dowker & Kirsten**, "Heat Kernel Coefficients for the Laplacian on Spheres" - explicit a_k on Sⁿ
5. **Ray & Singer**, "R-Torsion and the Laplacian on Riemannian Manifolds" - analytic torsion
6. **Cheeger & Müller**, "Analytic Torsion and R-Torsion" - relation to spectral determinants
7. **Bismut & Zhang**, "An Extension of a Theorem by Cheeger and Müller" - analytic torsion

### Specific Heat Kernel Coefficients Needed
For Beltrami operator B = ⋆d on S⁷ acting on p-forms:
- The operator B² = Δ_H (Hodge Laplacian) on forms
- Spectral determinant: det'(B) = exp(-½ ζ'_Δ(0))
- a_4 coefficient for Hodge Laplacian on p-forms on S⁷
- a_4 = (1/360) ∫ (5R² - 2R_{ij}R^{ij} + 2R_{ijkl}R^{ijkl}) + ... (for scalar)
- For forms: need the form-degree-dependent a_4 coefficients

### Literature Search Queries
- "Beltrami operator S^7 spectral determinant"
- "heat kernel coefficients Beltrami operator sphere"
- "Beltrami operator S^7 heat kernel a_4"
- "spectral determinant Beltrami operator sphere"
- "Ray-Singer torsion S^7"
- "analytic torsion 7-sphere Beltrami"
- "zeta function Beltrami operator sphere"
- "spectral determinant Hodge Laplacian forms sphere"

### Known Results (from literature)
- **Dowker (1975)**: Heat kernel coefficients for scalar Laplacian on Sⁿ
- **Gilkey (1995)**: Heat kernel for Hodge Laplacian on forms
- **Kirsten & McKane (2003)**: Functional determinants on Sⁿ
- **Dowker & Kirsten (1999)**: Heat kernel coefficients for Laplace-type operators on Sⁿ

### Computational Approach
The S7, S7' constants likely come from:
1. Spectral zeta function of Beltrami on S⁷: ζ_B(s) = Σ λ_i^{-s}
2. Derivative at s=0: ζ'_B(0) → log det'(B)
3. Expansion in α gives S7, S7' as coefficients in the effective action

The coefficients 1/56 and 1/16 suggest they come from:
- 1/56 = 1/(7×8) - possibly from dimension 7 and form degree
- 1/16 = 1/4² - possibly from (1/4)² in portal convention

---

## Search Strategy

### Immediate Actions
1. **arXiv search**: "Beltrami operator S^7 spectral determinant" OR "heat kernel Beltrami S^7"
2. **MathSciNet/ADS search**: "spectral determinant Beltrami operator sphere"
3. **Check**: Dowker & Kirsten papers on heat kernel coefficients on Sⁿ
4. **Check**: Gilkey's "Invariance Theory" for a_4 on Sⁿ for forms
5. **Check**: Kirsten's book "Spectral Functions..." for explicit S⁷ determinants

### Expected Outcome
The S7, S7' constants are likely standard results in spectral geometry:
- S7 = (some combination of ζ(7), π⁻⁶, etc.)
- S7' = (combination of ζ(9), π⁻⁸, etc.)
or they come from specific heat kernel coefficients a_4 for the Beltrami operator on S⁷.

The Hopf volume ratio for α⁻¹ likely has a known exact formula in the math literature on Hopf fibrations and classifying spaces, possibly involving:
- Vol(S⁹)/Vol(S¹)Vol(CP⁴) with exact topological factors
- Euler characteristic of CP⁴ = 5
- Pontryagin numbers of S⁹

---

## Next Steps
1. **Search arXiv** for the above queries
2. **Check MathSciNet** for relevant papers
5. **Contact spectral geometry experts** if needed
6. **Implement computation** once formulas are found
6. **Update T-1, T-3 gates** with derived formulas