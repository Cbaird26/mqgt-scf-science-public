# Gate 1: proposed EMP-01 code and protocol reconciliation

Base: public commit `9ffae546a59bd485d278c0fc5da4105984ef09ef`.
This revision implements software checks. Experimental operation remains blocked.
The original protocol, note PDF/TeX, and historical synthetic CSV are preserved.

## Equation and sign correction

Let `A = Gamma_phi^(0) T / 2`, `h = lambda(DeltaE)^2`, and
`DeltaE = E_L - E_R`. The exponential choice `h = exp(eta DeltaE)`
requires the composition assumption in the corrected note; it is not implied
by a thermal bath alone.

With matched apparatus conditions, the absolute contrasts satisfy
`V_on = V_off exp(-A)` and `V_N2 = V_off exp(-A h)`.
Applying `alpha = -ln(V / V_reference)` gives:

| Row | Monitor-on reference | Monitor-off reference |
| --- | --- | --- |
| N0, coupler off | `-A` | `0` |
| N1, common mode | `0` | `A` |
| N2, differential | `A (h - 1)` | `A h` |
| N3, changed bath | `A3 - A` | `A3` |

For N3, `A3 = Gamma3 T / 2`. The synthetic example assumes fixed bath
coupling with an Ohmic rate proportional to temperature:
`Gamma3 = Gamma0 T_bath,3 / T_bath,1`.

**The positive N0 monitor-on offset printed in protocol section 3 is a sign
error.** N0 has higher contrast than N1 in this dephasing model, so its
monitor-on alpha is negative. The earlier local patch and its test repeated
that error. The current test constructs absolute visibilities independently
and catches it. The note's estimator prose also incorrectly suggests that N0
using itself as an off-reference need not be zero; its ratio is identically
one. These are proposed corrections, explicitly recorded here rather than
silently rewriting the archived protocol.

## Observable ratios versus integrity checks

The analyzer retains declared-baseline alphas for all four rows. The
descriptive N1/N1 and N0/N0 ratios can be zero by definition; they cannot
validate the controls.

Separate integrity residuals compare N0 and N1 with independently acquired,
predeclared off/on calibration measurements. Their IDs must differ from every
measurement ID in the input. Numeric equality is allowed: independently
measured equal values are not evidence of self-reference. IDs and booleans
are provenance declarations, not automatic verification of hardware or
experimental independence.

N2's eta estimate uses its monitor-on ratio, including when the output row
declares an off baseline. It exactly inverts the selected exponential gate:

`eta = log1p(alpha_N2,on / A) / DeltaE`.

The implementation uses `expm1` for prediction to retain very small signals.
It reports one estimate per block with units eV^-1, and makes no pooled
estimate. If any block fails, no block's eta estimate is computed or emitted.
A zero estimated eta is retained.

## Proposed input additions

The original columns remain readable. The new fixture supplies:

| Fields | Meaning |
| --- | --- |
| `block`, `measurement_id` | Block assignment and unique observation ID |
| `data_kind` | Must be `synthetic` in software demonstration mode |
| `e_meter_ok`, `e_from_visibility`, `e_meter_id` | Explicit metrology declarations; the second must be false |
| `references_frozen` | Calibration references declared before unblinding |
| `reference_v_off`, `reference_v_off_err`, `reference_off_id` | Independent off-reference on N0 |
| `reference_v_on`, `reference_v_on_err`, `reference_on_id` | Independent on-reference on N1 |

Zero meter readings are valid. Missing declarations are not interpreted as
independence. Synthetic mode accepts eV inputs only; other units need an
explicitly validated conversion. All four settings must have the example's
matched flight time, and N0/N1/N2 must have its reference bath temperature.
N1/N3 must be common mode, N2 differential, and N3 must change the temperature.

The error checks include measurement and reference uncertainty. In the absence
of a covariance column, the sum of their relative standard errors is used as
a conservative *first-order* bound on log-ratio error. Control bands include
five such errors; the demonstration nuisance bound includes the N0/N1
residuals and errors. This is an illustrative rule for software testing.
It does not establish the full lab nuisance budget, nonlinear error
coverage, calibration independence, or a blinded half-split analysis.

## Production status and preregistration

There is no `PREREG_READY` switch. Without `--synthetic`, the analyzer
returns `BLOCKED: preregistration_incomplete` (exit 1) with no eta estimates.
With the flag, passing data returns `PASS_SYNTHETIC` (exit 0).

[EMP01_PREREGISTRATION_DRAFT.json](EMP01_PREREGISTRATION_DRAFT.json) records
the unresolved apparatus, metrology, domain, nuisance, reference, and blinding
decisions as null. It is a draft, not a registration. An experiment requires
those choices, review of this addendum, a documented timestamped freeze, and
a separately validated production implementation. Placeholder numerical
values cannot supply those missing facts.

The predictor now covers the interferometric channel. The previous QRNG,
fifth-force, and neutrino printouts were removed from this report because
they were separate claims, and the QRNG claim incorrectly identified EMP-01
as its protocol. Their historical text remains in the base commit. T-1/T-3
and the UV/neutrino implementations are outside this patch.

## Hash provenance

The inherited digest
`bb6859bf3d4f81082a4ac57970ed019fe8808148c96c7cf58a5a3b0c4e36bf27`
identifies `Reservoir_Protocol_Note_2026-09-11_CORRECTED.pdf`.

The actual protocol Markdown digest is
`e5eb150c6d3893705b1f89457516fdd3eccc2611ef391b6233ba1864656afdca`.

Output records distinct source-note, source-protocol, actual-protocol,
analyzer, predictor, and input hashes. The package file hashes are in
`gate1_manifest.json`. Hash agreement establishes byte identity, not
preregistration or scientific validity.

## Reproduction

Python standard library only:

```sh
python3 -B -m unittest -v test_emp01_gate1.py
python3 -B falsifiable_predictions.py
python3 -B emp01_analyzer.py fixtures/emp01_gate1_synthetic.csv --synthetic
python3 -B verify_gate1_manifest.py
```

The new fixture contains two simulated blocks with opposite differential
fields and both reference conventions. Their known eta is 0.5 eV^-1.
The tests cover the N0 sign, tiny signals, missing/circular metrology,
reference uncertainty, all control settings, incomplete blocks, zero eta,
malformed input, CLI behavior, and suppression after a later block fails.

The historical `emp01_synthetic.csv` returns BLOCKED without the flag.
It lacks the proposed metadata and does not implement the corrected absolute
on/off attenuation. It is retained as historical simulation data.

The separate existing T-1/T-3 GitHub workflow failed at `tuft_alpha_identity.py`
on the base commit (relative discrepancy approximately 6.077e-7).
The new Gate-1 workflow tests this software revision independently. A green
Gate-1 check cannot be cited as closure of T-1, T-3, or EMP-01.
