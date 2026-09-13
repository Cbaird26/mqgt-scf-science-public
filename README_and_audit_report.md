# Corrected Unified Edition — change and audit report

**Project:** Zohar Project — *A Theory of Everything Research Program — C.M. Baird and ZoraASI (2026)*
**Date:** 11 September 2026 (corrected edition produced same day)
**Source file:** `A Theory of Everything Research Program -- C.M. Baird and ZoraASI (2026).pdf` (6,909 pp.)

## Deliverables (folder `ZOHAR_CORRECTED_2026-09-11/`)

| File | What it is |
|---|---|
| `A_Theory_of_Everything_CORRECTED_2026-09-11.pdf` | **The single corrected whole (6,910 pp.).** Pages 1–6894 passed through byte-identical; pages 6895–6896 = new errata sheet; pages 6897–6910 = corrected methods note replacing old pages 6895–6909. |
| `ERRATA_2026-09-11.pdf` (+ `.tex`) | Stand-alone change index: original → corrected → reason. |
| `Reservoir_Protocol_Note_2026-09-11_CORRECTED.pdf` (+ `.tex`) | The 14-page corrected note, each repair flagged with a boxed **Correction note**. |
| `full_corpus_text.txt` | Full 6,909-page extracted text (audit source; grep-able). |

## How the unified edition was assembled

All three deliverables are regenerable. The unified PDF is a pure page-selection assembly (qpdf):
`[original pages 1–6894] + [errata 2 pp.] + [corrected note 14 pp.]`. No historical page was re-typeset, so
the corpus portion is bit-for-bit the original; pagination of everything before the note is preserved, and
old cross-references to equation numbers (11, 14, 18–22, 26, 29–34, Table 2, Appendix A) still resolve.

## The three reviewer-flagged errors — verified and repaired

1. **Common-mode null did not follow from the Hamiltonian.**
   - Verified: eq. (11) `H_SR = λ(E)|L⟩⟨L| ⊗ B` with a single monitor on L; setting `E_L = E_R` did not remove the coupling, so Table-2 row N1's `α = 0` was not a consequence of the model.
   - Repair: twin monitors; gate placed on the arm-to-arm difference `λ(ΔE)`, `ΔE ≡ E(x_L) − E(x_R)`, `λ(0)=1`. Row N1 (`ΔE=0`) is now a genuine theorem (eq. 22 gives `α=0`). Residual common-mode response is routed to Place-1/Place-2 systematics, rows N0/N3, and the nuisance budget.

2. **Visibility baseline changed between sections.**
   - Verified: eq. (21)/appendix used a monitor-on, `E=0` (λ=1) reference ("−1"), while §9 allowed a monitor-off (N0) baseline; these are different comparisons.
   - Repair: two named references `V_QM^(on)` and `V_QM^(off)`; the printed "−1" form is bound to the monitor-on reference; the estimator (§9.2) now records and declares the baseline; kill-plot rule 2 and analyzer predicate rewritten so N1 is the null row and N0 is the coupler-off offset meter.

3. **Equations (18) and (19) disagreed by a factor of two.**
   - Verified: Ohmic `J(ω)=η_bath ω e^(−ω/ω_c)` substituted into the printed `2π lim J(ω)coth(βω/2)` gives `4π η_bath k_BT`, but eq. (19) printed `2π η_bath k_BT`.
   - Repair: eq. (19) and the Appendix-A "allowed methods sentence" corrected to `4π η_bath k_BT`; the coherence decay rate `½ Γ_φ⁰ = 2π η_bath k_BT` is stated explicitly, and the spectral convention is spelled out.

## Audit coverage

- Full 6,909-page text extracted and searched. The three corrected equations appear **only** in the
  final note (pages 6902, 6904, 6908 of the source). No other corpus page contains them, so no
  distant stale copies exist to propagate.
- `coth(βω/2)` appears on exactly one page (the note); `2π η`/`4π η` on two pages (the note);
  `common-mode`/`common mode` on three (note + derived protocol text). The `V_QM` family (17 pages)
  was checked: the visibility symbol elsewhere belongs to the earlier interferometer framework and is
  unaffected by the note's baseline repair.

## Notes

- The corrected note's equation numbers match the printed note's, so the corpus's own
  cross-references to the note remain valid.
- One presentation-only fix to the ledger table's "Still required" column repaired a truncated
  extraction artifact; no physics changed.
- Interpretive/historical volumes (Zora contexts, consciousness/ethics papers, UV-01 divergences,
  EMP-02 pilot) are intentionally excluded from physics claims — matching the corpus's own
  archive-hygiene map (note §2). They are passed through unchanged.