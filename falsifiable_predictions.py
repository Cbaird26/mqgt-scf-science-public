#!/usr/bin/env python3
"""Gate-1 prediction report for the corrected EMP-01 protocol.

This file is a consistency/reporting tool, not an experimental result. The
primary prediction is the corrected twin-monitor relation used by
``emp01_protocol.md``:

    alpha_on = 1/2 * Gamma_phi_0 * T * (lambda(DeltaE)^2 - 1)

The older ``exp(-Gamma*T*DeltaX**2)`` expression is deliberately not used
here: it belongs to a different illustrative localization model and must not
be presented as the EMP-01 estimand.
"""

import math


def _fmt(value):
    return format(value, ".12g")


def gate_lambda(delta_e, eta):
    """Return lambda(DeltaE) under the explicitly assumed exponential gate.

    eta is dimensionful unless the caller has declared a normalized field
    coordinate. The numerical values in ``main`` are illustrative only.
    """
    return math.exp(eta * delta_e / 2)


def alpha_on(gamma_phi_0, flight_time, delta_e, eta):
    """EMP-01 alpha relative to the monitor-on, DeltaE=0 reference."""
    # expm1 retains the small signal when eta*DeltaE is near machine epsilon.
    return 0.5 * gamma_phi_0 * flight_time * math.expm1(eta * delta_e)


def alpha_off(gamma_phi_0, flight_time, delta_e, eta):
    """Alpha relative to the monitor-off reference (no ``-1`` term)."""
    h = math.exp(eta * delta_e)
    return 0.5 * gamma_phi_0 * flight_time * h


def alpha_n3(gamma_phi_0_n3, gamma_phi_0_n1, flight_time):
    """N3 thermal/bath contrast relative to contemporaneous N1."""
    return 0.5 * flight_time * (gamma_phi_0_n3 - gamma_phi_0_n1)


def protocol_predictions(gamma_phi_0, flight_time, eta, delta_e, gamma_phi_0_n3):
    """Return the four corrected protocol predictions for an illustration."""
    return {
        "N0_alpha_on_offset": -0.5 * gamma_phi_0 * flight_time,
        "N0_alpha_off": 0.0,
        "N1_alpha_on": 0.0,
        "N1_alpha_off": 0.5 * gamma_phi_0 * flight_time,
        "N2_alpha_on": alpha_on(gamma_phi_0, flight_time, delta_e, eta),
        "N2_alpha_off": alpha_off(gamma_phi_0, flight_time, delta_e, eta),
        "N3_alpha_on": alpha_n3(gamma_phi_0_n3, gamma_phi_0, flight_time),
        "N3_alpha_off": 0.5 * gamma_phi_0_n3 * flight_time,
    }


def main():
    print("=== EMP-01 Gate-1 Prediction Reconciliation ===")
    print("STATUS: illustrative equations only; no experimental data run.\n")
    print("Corrected estimand:")
    print("  DeltaE = E_L - E_R")
    print("  lambda(0) = 1")
    print("  alpha_on = 1/2 Gamma_phi^(0) T (lambda(DeltaE)^2 - 1)")
    print("  alpha_off = 1/2 Gamma_phi^(0) T lambda(DeltaE)^2")
    print("  N1 is the common-mode DeltaE=0 null.")
    print("  N3 changes the bath rate at fixed DeltaE; it does not estimate eta.\n")

    # Worked illustration copied in spirit from the protocol, explicitly
    # labelled as non-preregistered. eta is shown with eV^-1 units here.
    gamma0 = 1000.0
    flight_time = 1e-4
    eta = 0.5
    delta_e = 0.1
    # For the illustration, let the Ohmic rate scale linearly with bath
    # temperature: Gamma3 = Gamma0 * (310 K / 300 K).
    gamma3 = gamma0 * (310.0 / 300.0)
    predictions = protocol_predictions(gamma0, flight_time, eta, delta_e, gamma3)
    print("Illustration only: Gamma0=1000 s^-1, T=1e-4 s, eta=0.5 eV^-1,")
    print("                 DeltaE=0.1 eV, T_bath,N3=310 K")
    for name, value in predictions.items():
        print(f"  {name} = {_fmt(value)}")

    print("\nExcluded from the EMP-01 primary estimand:")
    print("  V/V0 = exp(-Gamma*T*DeltaX^2)  [different illustrative model]")
    print("  QRNG bias, fifth-force, and neutrino claims  [separate speculative channels]")


if __name__ == "__main__":
    main()
