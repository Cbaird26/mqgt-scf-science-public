#!/usr/bin/env python3
"""EMP-01 proposed analyzer revision; experimental analysis remains blocked.

--synthetic enables a software check using declared illustrative settings.
PASS_SYNTHETIC is never an experimental PASS or a preregistration receipt.
See GATE1_RECONCILIATION.md for assumptions and the proposed schema.
Exit codes: 0 = PASS_SYNTHETIC, 1 = FAIL/BLOCKED, 2 = invalid input.
"""

import argparse
import csv
import hashlib
import json
import math
import sys
from collections import OrderedDict
from pathlib import Path

from falsifiable_predictions import alpha_n3

# This inherited digest identifies the NOTE PDF, not the protocol Markdown.
SOURCE_NOTE_SHA256 = "bb6859bf3d4f81082a4ac57970ed019fe8808148c96c7cf58a5a3b0c4e36bf27"
PROTOCOL_SHA256 = "e5eb150c6d3893705b1f89457516fdd3eccc2611ef391b6233ba1864656afdca"

# Illustrations only. There is deliberately no production-ready toggle.
SYNTHETIC_SETTINGS = {
    "gamma_phi_0": 1000.0,
    "flight_time": 1e-4,
    "bath_reference_K": 300.0,
    "alpha_N0_max": 1e-3,
    "alpha_CM_max": 1e-3,
    "alpha_offset_max": 1e-3,
    "alpha_N3_max": 1e-3,
    "alpha_min": 0.0025,
    "z": 5.0,
    "E_null_tolerance_eV": 1e-12,
}
REQUIRED_COLUMNS = {
    "row_id", "coupler", "E_L", "E_R", "E_unit", "T", "T_bath",
    "N_tot", "V_hat", "V_hat_err", "baseline", "phase_scanned",
}
FLOAT_FIELDS = ("E_L", "E_R", "T", "T_bath", "V_hat", "V_hat_err")
OPTIONAL_FLOAT_FIELDS = (
    "reference_v_on", "reference_v_on_err", "reference_v_off", "reference_v_off_err"
)
BOOLEAN_FIELDS = ("e_meter_ok", "e_from_visibility", "references_frozen")
TEXT_FIELDS = ("measurement_id", "reference_on_id", "reference_off_id", "e_meter_id")
ROW_IDS = ("N0", "N1", "N2", "N3")


def finite_float(value, field):
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be numeric") from exc
    if not math.isfinite(result):
        raise ValueError(f"{field} must be finite")
    return result


def optional_bool(value, field):
    if value == "":
        return None
    if value.lower() in {"1", "true", "yes"}:
        return True
    if value.lower() in {"0", "false", "no"}:
        return False
    raise ValueError(f"{field} must be true/false")


def load_input(csv_path):
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames
        if not headers or len(set(headers)) != len(headers):
            raise ValueError("CSV headers are missing or duplicated")
        missing = REQUIRED_COLUMNS - set(headers)
        if missing:
            raise ValueError(f"Missing columns: {sorted(missing)}")
        for line_number, raw in enumerate(reader, start=2):
            if None in raw or any(value is None for value in raw.values()):
                raise ValueError(f"line {line_number}: malformed CSV row")
            row = {key: value.strip() for key, value in raw.items()}
            if row["row_id"] not in ROW_IDS:
                raise ValueError(f"line {line_number}: unknown row_id")
            for field in ("coupler", "N_tot", "phase_scanned"):
                try:
                    row[field] = int(row[field])
                except ValueError as exc:
                    raise ValueError(f"line {line_number}: invalid {field}") from exc
            if row["coupler"] not in (0, 1) or row["phase_scanned"] not in (0, 1):
                raise ValueError("coupler and phase_scanned must be 0 or 1")
            if row["N_tot"] <= 0:
                raise ValueError("N_tot must be positive")
            for field in FLOAT_FIELDS:
                row[field] = finite_float(row[field], field)
            if row["T"] <= 0 or row["T_bath"] <= 0:
                raise ValueError("T and T_bath must be positive")
            # Unconstrained visibility fits can exceed one; no clipping.
            if row["V_hat"] <= 0 or row["V_hat_err"] < 0:
                raise ValueError("V_hat must be positive; V_hat_err non-negative")
            row["baseline"] = row["baseline"].lower()
            if row["baseline"] not in {"on", "off"}:
                raise ValueError("baseline must be on or off")
            row["block"] = row.get("block", "") or None
            row["data_kind"] = row.get("data_kind", "")
            for field in BOOLEAN_FIELDS:
                row[field] = optional_bool(row.get(field, ""), field)
            for field in TEXT_FIELDS:
                row[field] = row.get(field, "")
            for field in OPTIONAL_FLOAT_FIELDS:
                value = row.get(field, "")
                row[field] = finite_float(value, field) if value else None
                if row[field] is not None:
                    if field.endswith("_err") and row[field] < 0:
                        raise ValueError(f"{field} must be non-negative")
                    if not field.endswith("_err") and row[field] <= 0:
                        raise ValueError(f"{field} must be positive")
            rows.append(row)
    if not rows:
        raise ValueError("CSV contains no data rows")
    return rows


def group_blocks(rows):
    if any(row["block"] is not None for row in rows):
        if not all(row["block"] is not None for row in rows):
            raise ValueError("Either every row must declare block or none may")
        grouped = OrderedDict()
        for row in rows:
            grouped.setdefault(row["block"], []).append(row)
        blocks = list(grouped.values())
    else:
        if len(rows) % 4:
            raise ValueError("Rows without block must be a multiple of four")
        blocks = [rows[index:index + 4] for index in range(0, len(rows), 4)]
    for block in blocks:
        if len(block) != 4 or {row["row_id"] for row in block} != set(ROW_IDS):
            raise ValueError("Each block must contain exactly one of N0, N1, N2, N3")
    return blocks


def alpha(value, reference):
    if reference is None:
        return None
    # log1p for close contrasts, separate logs for very different scales.
    relative = (value - reference) / reference
    if abs(relative) < 0.5:
        return -math.log1p(relative)
    return math.log(reference) - math.log(value)


def log_error(value, error, reference, reference_error):
    if reference is None or reference_error is None:
        return None
    # Conservative first-order upper bound for unspecified covariance.
    return error / value + reference_error / reference


def analyze_block(block):
    by_id = {row["row_id"]: row for row in block}
    n0, n1, n2, n3 = (by_id[rid] for rid in ROW_IDS)
    result = {}
    for rid, row in by_id.items():
        ref = n1 if row["baseline"] == "on" else n0
        result["alpha_" + rid] = alpha(row["V_hat"], ref["V_hat"])
        result["alpha_" + rid + "_on"] = alpha(row["V_hat"], n1["V_hat"])
    # Descriptive self-ratios are never used as integrity tests.
    result["N0_null_residual"] = alpha(n0["V_hat"], n0["reference_v_off"])
    result["N1_null_residual"] = alpha(n1["V_hat"], n1["reference_v_on"])
    for rid, row, mode in (("N0", n0, "off"), ("N1", n1, "on")):
        result[rid + "_null_error"] = log_error(
            row["V_hat"], row["V_hat_err"],
            row["reference_v_" + mode], row["reference_v_" + mode + "_err"],
        )
    a0 = 0.5 * SYNTHETIC_SETTINGS["gamma_phi_0"] * n1["T"]
    result["N0_expected_on"] = -a0
    result["N0_offset_residual"] = result["alpha_N0_on"] + a0
    gamma3 = SYNTHETIC_SETTINGS["gamma_phi_0"] * n3["T_bath"] / n1["T_bath"]
    result["N3_expected_on"] = alpha_n3(gamma3, SYNTHETIC_SETTINGS["gamma_phi_0"], n1["T"])
    result["N3_bath_residual"] = result["alpha_N3_on"] - result["N3_expected_on"]
    result["N2_alpha_error"] = log_error(
        n2["V_hat"], n2["V_hat_err"], n1["V_hat"], n1["V_hat_err"]
    )
    if not all(value is None or math.isfinite(value) for value in result.values()):
        raise ValueError("Non-finite derived quantity")
    return result


def first_predicate(block, results, synthetic, measurement_ids):
    if not synthetic:
        return "preregistration_incomplete"
    if any(row["data_kind"] != "synthetic" for row in block):
        return "synthetic_data_declaration_required"
    by_id = {row["row_id"]: row for row in block}
    if any(row["phase_scanned"] != 1 for row in block):
        return "phase_not_scanned"
    for rid in ROW_IDS:
        if by_id[rid]["coupler"] != (0 if rid == "N0" else 1):
            return rid + "_coupler_invalid"
    for row in block:
        if row["E_unit"] != "eV":
            return "unsupported_E_units"
        if row["e_meter_ok"] is not True or not row["e_meter_id"]:
            return "missing_E_metrology"
        if row["e_from_visibility"] is not False:
            return "E_independence_unconfirmed"
        if not math.isclose(row["T"], SYNTHETIC_SETTINGS["flight_time"], rel_tol=1e-12):
            return "flight_time_settings_mismatch"
    for rid in ("N0", "N1", "N2"):
        if not math.isclose(by_id[rid]["T_bath"], SYNTHETIC_SETTINGS["bath_reference_K"],
                            rel_tol=1e-12):
            return "reference_bath_settings_mismatch"
    for rid in ("N1", "N3"):
        row = by_id[rid]
        if abs(row["E_L"] - row["E_R"]) > SYNTHETIC_SETTINGS["E_null_tolerance_eV"]:
            return rid + "_is_not_common_mode"
    n2 = by_id["N2"]
    if abs(n2["E_L"] - n2["E_R"]) <= SYNTHETIC_SETTINGS["E_null_tolerance_eV"]:
        return "N2_has_no_differential_E"
    if math.isclose(by_id["N3"]["T_bath"], by_id["N1"]["T_bath"], rel_tol=1e-12):
        return "N3_bath_unchanged"

    for rid, mode in (("N0", "off"), ("N1", "on")):
        row = by_id[rid]
        ref_id = row["reference_" + mode + "_id"]
        if not ref_id or ref_id in measurement_ids:
            return rid + "_independent_reference_required"
        if row["reference_v_" + mode] is None or row["reference_v_" + mode + "_err"] is None:
            return rid + "_reference_value_or_error_missing"
        if row["references_frozen"] is not True:
            return "reference_freeze_unconfirmed"

    z = SYNTHETIC_SETTINGS["z"]
    for rid, band in (("N0", "alpha_N0_max"), ("N1", "alpha_CM_max")):
        if abs(results[rid + "_null_residual"]) + z * results[rid + "_null_error"] > SYNTHETIC_SETTINGS[band]:
            return rid + "_null_band_exceeded"
    n0, n1, n3 = (by_id[rid] for rid in ("N0", "N1", "N3"))
    offset_err = log_error(n0["V_hat"], n0["V_hat_err"], n1["V_hat"], n1["V_hat_err"])
    if abs(results["N0_offset_residual"]) + z * offset_err > SYNTHETIC_SETTINGS["alpha_offset_max"]:
        return "N0_offset_band_exceeded"
    bath_err = log_error(n3["V_hat"], n3["V_hat_err"], n1["V_hat"], n1["V_hat_err"])
    if abs(results["N3_bath_residual"]) + z * bath_err > SYNTHETIC_SETTINGS["alpha_N3_max"]:
        return "N3_bath_band_exceeded"
    stat = max(1 / math.sqrt(n2["N_tot"]), results["N2_alpha_error"])
    # Demonstration-only bound: a real lab must specify its nuisance model.
    sys_bound = max(
        abs(results[rid + "_null_residual"]) + z * results[rid + "_null_error"]
        for rid in ("N0", "N1")
    )
    if math.hypot(stat, sys_bound) > SYNTHETIC_SETTINGS["alpha_min"] / z:
        return "budget_violated"
    a0 = 0.5 * SYNTHETIC_SETTINGS["gamma_phi_0"] * n2["T"]
    if results["alpha_N2_on"] <= -a0:
        return "exponential_gate_domain_invalid"
    return None


def estimate_eta(alpha_measured, delta_e, flight_time):
    """Invert the explicitly assumed exponential gate, including its -1."""
    a0 = 0.5 * SYNTHETIC_SETTINGS["gamma_phi_0"] * flight_time
    value = math.log1p(alpha_measured / a0) / delta_e
    if not math.isfinite(value):
        raise ValueError("Non-finite eta estimate")
    return value


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def process_file(csv_path, output_json=None, *, synthetic=False):
    if output_json and Path(output_json).resolve() == Path(csv_path).resolve():
        raise ValueError("Output must not overwrite the input CSV")
    rows = load_input(csv_path)
    blocks = group_blocks(rows)
    ids = [row["measurement_id"] for row in rows]
    if synthetic and (any(not value for value in ids) or len(set(ids)) != len(ids)):
        raise ValueError("Synthetic rows require unique measurement_id values")
    all_results = []
    for index, block in enumerate(blocks):
        values = analyze_block(block)
        predicate = first_predicate(block, values, synthetic, set(ids))
        all_results.append({
            "block_idx": index, "block": block[0]["block"],
            "fail": predicate is not None, "predicate": predicate,
            "eta_estimate_eV_inverse": None, **values,
        })
    overall_fail = any(result["fail"] for result in all_results)
    # Complete validation of every block precedes all parameter estimation.
    if not overall_fail:
        for block, result in zip(blocks, all_results):
            n2 = next(row for row in block if row["row_id"] == "N2")
            result["eta_estimate_eV_inverse"] = estimate_eta(
                result["alpha_N2_on"], n2["E_L"] - n2["E_R"], n2["T"]
            )
    root = Path(__file__).resolve().parent
    output = {
        "status": ("FAIL" if synthetic else "BLOCKED") if overall_fail else "PASS_SYNTHETIC",
        "mode": "synthetic" if synthetic else "experimental_blocked",
        "overall_fail": overall_fail,
        "first_failed_predicate": next((r["predicate"] for r in all_results if r["fail"]), None),
        "eta_estimates_eV_inverse": [] if overall_fail else [
            r["eta_estimate_eV_inverse"] for r in all_results
        ],
        "provenance": {
            "source_note_sha256": SOURCE_NOTE_SHA256,
            "source_protocol_sha256": PROTOCOL_SHA256,
            "actual_protocol_sha256": sha256_file(root / "emp01_protocol.md"),
            "analyzer_sha256": sha256_file(__file__),
            "predictor_sha256": sha256_file(root / "falsifiable_predictions.py"),
            "input_sha256": sha256_file(csv_path),
        },
        "settings": SYNTHETIC_SETTINGS if synthetic else None,
        "blocks": all_results,
    }
    if output_json:
        with open(output_json, "w", encoding="utf-8") as handle:
            json.dump(output, handle, indent=2, allow_nan=False)
            handle.write("\n")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv")
    parser.add_argument("-o", "--output")
    parser.add_argument("--print", action="store_true")
    parser.add_argument("--synthetic", action="store_true", help="software check with illustrative settings")
    args = parser.parse_args()
    try:
        result = process_file(args.input_csv, args.output, synthetic=args.synthetic)
        if args.print or not args.output:
            print(json.dumps(result, indent=2, allow_nan=False))
    except (OSError, ValueError, OverflowError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
    print(result["status"] + (": " + result["first_failed_predicate"] if result["overall_fail"] else ""),
          file=sys.stderr)
    raise SystemExit(1 if result["overall_fail"] else 0)


if __name__ == "__main__":
    main()
