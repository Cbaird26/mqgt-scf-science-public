#!/usr/bin/env python3
"""Scientific consistency, fail-closed, and CLI regressions for Gate 1."""

import copy
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import emp01_analyzer as analyzer
import falsifiable_predictions as predictor

ROOT = Path(__file__).resolve().parent
FIXTURE = ROOT / "fixtures" / "emp01_gate1_synthetic.csv"


class Gate1Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "input.csv"
        with FIXTURE.open(newline="") as handle:
            reader = csv.DictReader(handle)
            self.fields = reader.fieldnames
            self.rows = list(reader)

    def write(self, rows=None):
        with self.path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=self.fields)
            writer.writeheader()
            writer.writerows(self.rows if rows is None else rows)
        return self.path

    def analyze(self, rows=None, synthetic=True):
        return analyzer.process_file(self.write(rows), synthetic=synthetic)

    def assert_suppressed(self, result):
        self.assertTrue(result["overall_fail"])
        self.assertEqual(result["eta_estimates_eV_inverse"], [])
        for block in result["blocks"]:
            self.assertIsNone(block["eta_estimate_eV_inverse"])

    def test_physical_attenuation_and_exact_eta_both_baselines(self):
        result = self.analyze()
        self.assertEqual(result["status"], "PASS_SYNTHETIC")
        for index, delta in enumerate((0.1, -0.1)):
            block = result["blocks"][index]
            self.assertAlmostEqual(block["alpha_N0_on"], -0.05, places=14)
            self.assertAlmostEqual(block["N0_null_residual"], 0, places=14)
            self.assertAlmostEqual(block["N1_null_residual"], 0, places=14)
            self.assertAlmostEqual(block["eta_estimate_eV_inverse"], 0.5, places=12)
            self.assertAlmostEqual(block["alpha_N2_on"], 0.05 * math.expm1(0.5*delta), places=14)
            self.assertAlmostEqual(block["alpha_N3_on"], 1/600, places=14)
        # N1 declared off-reference depth is A, separate from its independent null.
        self.assertAlmostEqual(result["blocks"][1]["alpha_N1"], 0.05, places=14)

    def test_prediction_table_matches_absolute_visibility_oracle(self):
        for delta in (-0.1, 0, 0.1):
            a0 = 0.05
            off = 0.99
            # Independent construction: absolute depths of the four settings.
            depths = (0, a0, a0*math.exp(0.5*delta), a0*310/300)
            on = off*math.exp(-a0)
            expected = predictor.protocol_predictions(1000, 1e-4, 0.5, delta, 1000*310/300)
            for index, depth in enumerate(depths):
                v = off*math.exp(-depth)
                on_key = "N0_alpha_on_offset" if index == 0 else f"N{index}_alpha_on"
                self.assertAlmostEqual(expected[on_key], -math.log(v/on), places=14)
                self.assertAlmostEqual(expected[f"N{index}_alpha_off"], -math.log(v/off), places=14)

    def test_tiny_gate_signal_is_not_rounded_to_zero(self):
        # Linear limit at x=7e-18; ordinary exp(x)-1 loses this signal.
        value = predictor.alpha_on(1000, 1e-4, 1e-7, 7e-11)
        self.assertTrue(math.isclose(value, 3.5e-19, rel_tol=1e-14))
        self.assertEqual(predictor.gate_lambda(0, 0.5), 1)
        self.assertEqual(predictor.alpha_on(1000, 1e-4, 0, 0.5), 0)

    def test_production_is_blocked_even_with_complete_synthetic_fixture(self):
        result = self.analyze(synthetic=False)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["first_failed_predicate"], "preregistration_incomplete")
        self.assert_suppressed(result)

    def test_later_failure_suppresses_earlier_estimates(self):
        self.rows[6]["phase_scanned"] = "0"
        result = self.analyze()
        self.assertFalse(result["blocks"][0]["fail"])
        self.assert_suppressed(result)

    def test_predicates_with_controlled_mutations(self):
        cases = [
            (0, "data_kind", "", "synthetic_data_declaration_required"),
            (2, "phase_scanned", "0", "phase_not_scanned"),
            (0, "coupler", "1", "N0_coupler_invalid"),
            (1, "coupler", "0", "N1_coupler_invalid"),
            (2, "coupler", "0", "N2_coupler_invalid"),
            (3, "coupler", "0", "N3_coupler_invalid"),
            (2, "E_unit", "J", "unsupported_E_units"),
            (2, "e_meter_ok", "", "missing_E_metrology"),
            (0, "e_meter_id", "", "missing_E_metrology"),
            (2, "e_from_visibility", "", "E_independence_unconfirmed"),
            (2, "e_from_visibility", "true", "E_independence_unconfirmed"),
            (2, "T", "0.0002", "flight_time_settings_mismatch"),
            (2, "T_bath", "301", "reference_bath_settings_mismatch"),
            (1, "E_L", "0.4", "N1_is_not_common_mode"),
            (3, "E_L", "0.4", "N3_is_not_common_mode"),
            (2, "E_L", "0.2", "N2_has_no_differential_E"),
            (3, "T_bath", "300", "N3_bath_unchanged"),
            (1, "reference_on_id", "", "N1_independent_reference_required"),
            (1, "reference_on_id", "synthetic:b0:N1", "N1_independent_reference_required"),
            (1, "reference_v_on_err", "", "N1_reference_value_or_error_missing"),
            (0, "reference_v_off", "", "N0_reference_value_or_error_missing"),
            (1, "references_frozen", "", "reference_freeze_unconfirmed"),
            (1, "V_hat", "0.94", "N1_null_band_exceeded"),
            (0, "V_hat", "0.97", "N0_null_band_exceeded"),
            (1, "reference_v_on_err", "0.01", "N1_null_band_exceeded"),
            (2, "V_hat_err", "0.01", "budget_violated"),
            (2, "N_tot", "10", "budget_violated"),
            (3, "V_hat", "0.95", "N3_bath_band_exceeded"),
            (2, "V_hat", "1.01", "exponential_gate_domain_invalid"),
        ]
        original = copy.deepcopy(self.rows)
        for index, key, value, predicate in cases:
            with self.subTest(key=key, value=value, predicate=predicate):
                self.rows = copy.deepcopy(original)
                self.rows[index][key] = value
                result = self.analyze()
                self.assertEqual(result["first_failed_predicate"], predicate)
                self.assert_suppressed(result)

    def test_n0_positive_offset_regression(self):
        # The earlier patch used this reversed attenuation and incorrectly passed.
        wrong_v0 = 0.95*math.exp(-0.05)
        self.rows[0]["V_hat"] = str(wrong_v0)
        self.rows[0]["reference_v_off"] = str(wrong_v0)
        result = self.analyze()
        self.assertEqual(result["first_failed_predicate"], "N0_offset_band_exceeded")
        self.assert_suppressed(result)

    def test_zero_readings_are_not_missing_metrology(self):
        for row in self.rows:
            if row["row_id"] in ("N0", "N1", "N3"):
                row["E_L"] = row["E_R"] = "0"
        self.assertFalse(self.analyze()["overall_fail"])

    def test_zero_eta_is_retained(self):
        self.rows[2]["V_hat"] = self.rows[1]["V_hat"]
        result = self.analyze()
        self.assertFalse(result["overall_fail"])
        self.assertEqual(result["eta_estimates_eV_inverse"][0], 0)

    def test_nonfinite_invalid_and_incomplete_inputs(self):
        original = copy.deepcopy(self.rows)
        for field, value in (("V_hat", "nan"), ("T", "inf"), ("V_hat", "0"),
                             ("V_hat_err", "-1"), ("N_tot", "0"), ("T_bath", "-1")):
            with self.subTest(field=field, value=value):
                self.rows = copy.deepcopy(original)
                self.rows[0][field] = value
                with self.assertRaises(ValueError):
                    self.analyze()
        for rows in ([], original[:3], original[:3] + [original[0]]):
            with self.subTest(rows=len(rows)), self.assertRaises(ValueError):
                self.analyze(rows)

    def test_duplicate_ids_missing_block_and_shuffle(self):
        self.rows[0]["measurement_id"] = self.rows[1]["measurement_id"]
        with self.assertRaises(ValueError):
            self.analyze()
        self.setUp_rows_from_fixture()
        self.rows[0]["block"] = ""
        with self.assertRaises(ValueError):
            self.analyze()
        self.setUp_rows_from_fixture()
        self.rows.reverse()
        self.assertFalse(self.analyze()["overall_fail"])

    def setUp_rows_from_fixture(self):
        with FIXTURE.open(newline="") as handle:
            self.rows = list(csv.DictReader(handle))

    def test_partial_and_duplicate_header_csv_rejected(self):
        for content in ("row_id,row_id\nN0,N1\n",
                        ",".join(self.fields) + "\nN0,0\n",
                        ",".join(self.fields) + "\n" + ",".join(["N0"]*(len(self.fields)+1)) + "\n"):
            with self.subTest(content=content[:20]):
                self.path.write_text(content)
                with self.assertRaises(ValueError):
                    analyzer.process_file(self.path)

    def test_output_does_not_overwrite_input(self):
        path = self.write()
        before = path.read_bytes()
        with self.assertRaises(ValueError):
            analyzer.process_file(path, path, synthetic=True)
        self.assertEqual(before, path.read_bytes())

    def test_hashes_identify_actual_files(self):
        result = self.analyze()
        digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(result["provenance"]["source_note_sha256"],
                         digest(ROOT / "Reservoir_Protocol_Note_2026-09-11_CORRECTED.pdf"))
        self.assertEqual(result["provenance"]["source_protocol_sha256"], digest(ROOT/"emp01_protocol.md"))
        self.assertEqual(result["provenance"]["input_sha256"], digest(self.path))

    def test_cli_exit_codes_labels_and_failure_output(self):
        path = self.write()
        cmd = [sys.executable, "-B", str(ROOT/"emp01_analyzer.py"), str(path)]
        for extra, expected_rc, expected_status in (
            ([], 1, "BLOCKED"), (["--synthetic"], 0, "PASS_SYNTHETIC")
        ):
            proc = subprocess.run(cmd+extra, capture_output=True, text=True)
            self.assertEqual(proc.returncode, expected_rc, proc.stderr)
            self.assertEqual(json.loads(proc.stdout)["status"], expected_status)
        self.rows[6]["phase_scanned"] = "0"
        self.write()
        proc = subprocess.run(cmd+["--synthetic"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1)
        self.assert_suppressed(json.loads(proc.stdout))
        self.path.write_text("invalid\n")
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("ERROR:", proc.stderr)


if __name__ == "__main__":
    unittest.main()
