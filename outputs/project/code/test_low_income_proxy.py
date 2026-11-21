"""Regression checks for the equity pivot, suppression and truthful readiness."""
import contextlib
import csv
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from calculate_low_income_proxy import ROOT, INDICATOR, calculate, read_csv, weighted_share
from validate_data import validate


class LowIncomeProxyTests(unittest.TestCase):
    def test_ratio_uses_allocated_counts_not_average_of_rates(self):
        result = weighted_share([{"area_fraction": 0.5, "population": 100, "low_income": 10},
                                 {"area_fraction": 1.0, "population": 900, "low_income": 450}])
        self.assertAlmostEqual(result["share"], 455 / 950)
        self.assertNotAlmostEqual(result["share"], 0.3)

    def test_suppression_blocks_complete_ratio_and_preserves_known_contribution(self):
        result = weighted_share([{"area_fraction": 1, "population": 100, "low_income": 20},
                                 {"area_fraction": 0.5, "population": 200, "low_income": None}])
        self.assertIsNone(result["share"])
        self.assertIsNone(result["low_income_estimate"])
        self.assertEqual(result["known_low_income_contribution"], 20)
        self.assertEqual(result["suppression_only_share_lower"], 0.1)
        self.assertEqual(result["suppression_only_share_upper"], 0.6)

    def test_zero_missing_and_negative_counts_are_distinct(self):
        self.assertEqual(weighted_share([{"area_fraction": 1, "population": 100, "low_income": 0}])["share"], 0)
        self.assertIsNone(weighted_share([{"area_fraction": 1, "population": 0, "low_income": 0}])["share"])
        self.assertIsNone(weighted_share([{"area_fraction": 1, "population": None, "low_income": 0}])["share"])
        with self.assertRaises(ValueError):
            weighted_share([{"area_fraction": 1, "population": 100, "low_income": -1}])
        with self.assertRaises(ValueError):
            weighted_share([{"area_fraction": 1, "population": 100, "low_income": 101}])

    def test_archived_ct_pilot_and_da_missingness(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            with contextlib.redirect_stdout(io.StringIO()):
                result = calculate(ROOT, folder, folder / "model_inputs.csv")
            self.assertAlmostEqual(result["results"]["CT"]["share"], 0.15911921596379328, places=8)
            self.assertAlmostEqual(result["results"]["CT"]["lim_applicable_population_share"], 0.16001234799459568, places=8)
            self.assertEqual(result["results"]["CT"]["geography_count"], 14)
            self.assertEqual(result["results"]["DA"]["missing_low_income_ids"], ["35202414"])
            self.assertIsNone(result["results"]["DA"]["share"])
            rows = read_csv(folder / "model_inputs.csv")
            self.assertEqual([r["corridor_id"] for r in rows], [str(i) for i in range(1, 25)])
            self.assertTrue(all(r[INDICATOR] == "" and r["estimation_status"] == "pending_collection" for r in rows[1:]))
            self.assertEqual(result["model_facing_coverage_count"], 1)
            self.assertFalse(result["model_ready"])
            self.assertFalse(result["ranking_run"])
            scenarios = [r for r in read_csv(folder / "population_stress_scenarios.csv") if r["corridor_id"] == "1"]
            by_name = {r["scenario_id"]: r for r in scenarios}
            self.assertEqual(float(by_name["midpoint_population"]["population_denominator"]), 32679.5)
            self.assertFalse(result["midpoint_is_area_weighted"])
            self.assertGreater(float(by_name["low_bound"][INDICATOR]), float(by_name["high_bound"][INDICATOR]))

    def test_active_selection_is_six_with_ppi_withdrawn(self):
        selection = json.loads((ROOT / "data/model_input_selection_v0.1.json").read_text())
        self.assertEqual(len(selection["selected_indicator_ids"]), 6)
        self.assertIn(INDICATOR, selection["selected_indicator_ids"])
        self.assertNotIn("priority_populations_index", selection["selected_indicator_ids"])
        report = validate(ROOT)
        self.assertTrue(report["valid_structure"])
        self.assertFalse(report["model_ready"])

    def copy_validation_inputs(self, folder):
        target = Path(folder)
        shutil.copytree(ROOT / "data", target / "data")
        (target / "evidence").mkdir()
        shutil.copyfile(ROOT / "evidence/city_2024_published_scores_NOT_RAW_v0.1.csv",
                        target / "evidence/city_2024_published_scores_NOT_RAW_v0.1.csv")
        return target

    def test_claiming_admission_and_coverage_does_not_manufacture_readiness(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = self.copy_validation_inputs(temporary)
            file = target / "data/workbook_records_v0.1.json"
            records = json.loads(file.read_text())
            selected = json.loads((target / "data/model_input_selection_v0.1.json").read_text())["selected_indicator_ids"]
            for row in records["indicator_admission"]:
                if row["indicator_id"] in selected:
                    row.update(admission_status="admitted", coverage_count=24, missing_corridor_ids="",
                               temporal_comparability="confirmed", spatial_comparability="confirmed", baseline_comparability="confirmed")
            file.write_text(json.dumps(records))
            report = validate(target)
            self.assertFalse(report["model_ready"])
            self.assertTrue(any("geographic review" in issue for issue in report["readiness_issues"]))
            self.assertTrue(any("source" in error.lower() or "no such file" in error.lower() for error in report["errors"]))

    def test_fraction_cannot_disagree_with_its_numerator_and_denominator(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = self.copy_validation_inputs(temporary)
            admissions = json.loads((target / "data/workbook_records_v0.1.json").read_text())["indicator_admission"]
            relative = next(row["input_file"] for row in admissions if row["indicator_id"] == INDICATOR)
            file = target / relative
            rows = read_csv(file)
            rows[0][INDICATOR] = "0.9"
            with file.open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            report = validate(target)
            self.assertFalse(report["valid_structure"])
            self.assertTrue(any("invalid area-weighted share contract" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
