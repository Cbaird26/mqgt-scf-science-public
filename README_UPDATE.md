# Zenodo Update Package v1.0.4
**Based on:** Zenodo 22717352 (v1.0.3) → **Next version: v1.0.4**  
**Concept Record:** 14019809  
**Date:** 2026-09-13  

---

## What's New in v1.0.4

### 📄 New Scientific Papers (Phase 3 Complete)

| Paper | Files | Key Result |
|-------|-------|------------|
| **UV Completion** | `uv_completion.tex`, `uv_completion.pdf` | Asymptotic safety FP search in Bridge D truncation with `gN* = 1.7621271`. **91/91 trajectories flow to Gaussian FP in UV. No non-Gaussian FP found.** Gravity drives matter to Gaussian. |
| **Neutrino Portal** | `neutrino_portal.tex`, `neutrino_portal.pdf` | E-scalar Dirac mass portal for neutrino masses. **Exact match: Σm_ν = 0.05928 eV** via `L_ν = y_ν E ν̄_L ν_R` with `y_ν = 0.1976`, `⟨E⟩ = DETAE = 0.1 eV`. Natural Yukawa `y_ν ≈ 0.2`, predicts purely Dirac neutrinos. |

### 📦 Submission Packages (arXiv/Journal Ready)
- `UV_COMPLETION_SUBMISSION_PACKAGE.md` — Complete submission package for UV Completion paper
- `NEUTRINO_PORTAL_SUBMISSION_PACKAGE.md` — Complete submission package for Neutrino Portal paper

### 🔧 Updated Computational Scripts
All Phase 3 verification scripts included with outputs:
- `bridge_d_uv.py` / `bridge_d_uv_4scalar.py` — UV completion searches
- `neutrino_portal.py` — Neutrino portal derivation
- `tuft_s7_spectral.py` — S⁷ Beltrami spectral determinant (BLOCKED)
- `bridge_c_full_eta_extended.py` — Bridge C q-insertion verified
- All Phase 1/2 scripts with CSV outputs

---

## Files to Upload to Zenodo (New/Updated)

### New Files (not in v1.0.3)
```
uv_completion.tex              ← NEW
uv_completion.pdf              ← NEW
neutrino_portal.tex            ← NEW
neutrino_portal.pdf            ← NEW
UV_COMPLETION_SUBMISSION_PACKAGE.md  ← NEW
NEUTRINO_PORTAL_SUBMISSION_PACKAGE.md ← NEW
manifest_v2.json               ← NEW (this manifest)
README_UPDATE.md               ← NEW (this file)
```

### Existing Files (unchanged from v1.0.3)
- `A_Theory_of_Everything_CORRECTED_2026-09-11.pdf` (37 MB)
- `ERRATA_2026-09-11.pdf/.tex`
- `Reservoir_Protocol_Note_2026-09-11_CORRECTED.pdf/.tex`
- All Phase 1/2/3 scripts and CSV outputs

---

## Zenodo Upload Instructions

1. Go to https://zenodo.org/records/22717352
2. Click **"New version"** button
3. Upload **all files** from this folder (or drag the entire folder)
3. Update metadata:
   - **Title:** "A Theory of Everything" (same)
   - **Description:** Add "Phase 3 Complete: UV Completion and Neutrino Portal papers added..."
   - **Version:** v1.0.4 (auto-incremented)
   - **Keywords:** Add "Asymptotic Safety", "Neutrino Mass", "Dirac Portal", "UV Completion"
4. Publish

---

## Key Metadata for New Version
- **Concept DOI:** 10.5281/zenodo.14019809
- **This Version DOI:** Will be assigned on publish (e.g., 10.5281/zenodo.XXXXXXXX)
- **License:** CC-BY-4.0
- **Resource Type:** Journal article
- **Access Right:** Open

---

## Verification Checklist
- [ ] All new PDFs compile without errors
- [ ] LaTeX sources included for both papers
- [ ] Submission packages complete with metadata
- [ ] All computational scripts have outputs
- [ ] Manifest updated with new files
- [ ] Ready for Zenodo "New version" upload

---

**Ready for Zenodo upload.** Just drag this folder to zenodo.org/upload or use the "New version" button on record 22717352.
