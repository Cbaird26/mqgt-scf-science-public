# MQGT-SCF public science archive

The current software change is the [Gate-1 EMP-01 reconciliation](GATE1_RECONCILIATION.md).
It corrects the N0 baseline sign and analyzer failure handling, adds independent
control references, and tests the corrected interferometric equations.
Experimental analysis remains blocked pending the laboratory preregistration
decisions in [the draft addendum](EMP01_PREREGISTRATION_DRAFT.json).

Published archive: [Zenodo record 22738328, v302](https://zenodo.org/records/22738328).
Version family: [concept DOI 10.5281/zenodo.14019809](https://doi.org/10.5281/zenodo.14019809).
The Gate-1 changes are subsequent GitHub software revisions; they are not
already part of that frozen deposit.

```sh
python3 -B -m unittest -v test_emp01_gate1.py
python3 -B emp01_analyzer.py fixtures/emp01_gate1_synthetic.csv --synthetic
python3 -B verify_gate1_manifest.py
```

`PASS_SYNTHETIC` means the software checks passed on labelled simulated input.
It does not report an experiment. The archival PDFs, protocol, and original
synthetic CSV are preserved. Their proposed corrections are documented in the
Gate-1 note.

T-1's eight-digit target and T-3's first-principles derivation remain open.
The repository's existing T-1/T-3 workflow has a known T-1 failure; the
dedicated Gate-1 workflow verifies only the new software checks.
