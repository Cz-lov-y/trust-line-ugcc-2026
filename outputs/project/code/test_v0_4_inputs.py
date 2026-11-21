"""Checks for source-preserving imputation and honest batch geometry coverage."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from analyze_city_missingness import ROOT, FIELDS, analyze, read_csv
from batch_corridor_equity import calculate
from build_corridor_road_proxies import path_between
from validate_data import validate, validate_city_scenario


class VersionFourInputTests(unittest.TestCase):
    def test_missingness_and_scenarios_preserve_observed_source_cells(self):
        original_path = ROOT / "data/city_standardized_scores_v0.1.csv"
        before = original_path.read_bytes()
        original = {r["corridor_id"]: r for r in read_csv(original_path)}
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            with contextlib.redirect_stdout(io.StringIO()):
                result = analyze(ROOT, folder / "out", folder / "data")
            self.assertEqual(result["missing_values"], 22)
            self.assertEqual(result["missing_corridor_ids"], ["3", "4", "5", "6", "8", "10", "13"])
            self.assertEqual(result["row_missing_count_distribution"], {0: 17, 2: 3, 4: 4})
            derived = read_csv(folder / "data/city_analysis_inputs_v0.4.csv")
            self.assertEqual(len(derived), 24)
            substitutions = 0
            for row in derived:
                for field in FIELDS:
                    source = original[row["corridor_id"]][field]
                    self.assertNotEqual(row[field], "")
                    if source != "":
                        self.assertEqual(row[field], source)
                        self.assertEqual(row[field + "_value_status"], "source_observed")
                    else:
                        substitutions += 1
                        self.assertEqual(row[field + "_value_status"], "imputed_conservative_min")
            self.assertEqual(substitutions, 22)
            self.assertNotEqual(result["top3_or_tied_top3_by_policy"]["imputed_conservative_min"], result["top3_or_tied_top3_by_policy"]["imputed_observed_mean"])
            self.assertFalse(result["observed_minimum_is_theoretical_lower_bound"])
        self.assertEqual(original_path.read_bytes(), before)

    def test_correct_note_cannot_hide_an_incorrect_imputation(self):
        rows = {r["corridor_id"]: r for r in read_csv(ROOT / "data/city_analysis_inputs_v0.4.csv")}
        rows["3"]["current_speed"] = "100"
        rows["3"]["notes"] = "imputed_conservative_min"
        errors = validate_city_scenario(ROOT, "current_speed", "current_speed", rows)
        self.assertTrue(any("scenario value does not match" in error for error in errors))

    def test_imputed_value_cannot_be_disguised_as_an_observation(self):
        rows = {r["corridor_id"]: r for r in read_csv(ROOT / "data/city_analysis_inputs_v0.4.csv")}
        rows["3"]["current_speed_value_status"] = "source_observed"
        errors = validate_city_scenario(ROOT, "current_speed", "current_speed", rows)
        self.assertTrue(any("provenance flag mismatch" in error for error in errors))

    def test_disconnected_named_roads_are_not_bridged(self):
        with self.assertRaises(ValueError):
            path_between({1: [(2, 1, None, None)], 2: [], 3: []}, 1, 3)

    def test_batch_retains_all_corridors_and_preserves_census_suppression(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            with contextlib.redirect_stdout(io.StringIO()):
                result = calculate(ROOT, folder, folder / "model.csv")
            rows = {r["corridor_id"]: r for r in read_csv(folder / "model.csv")}
            self.assertEqual(set(rows), {str(i) for i in range(1, 25)})
            self.assertEqual(result["coverage_count"], 15)
            self.assertEqual(result["pending_equity_corridor_ids"], [3, 4, 5, 6, 8, 9, 10, 19, 21])
            self.assertEqual(rows["3"]["low_income_population_share_500m"], "")
            self.assertEqual(rows["21"]["low_income_population_share_500m"], "")
            self.assertEqual(result["per_corridor"][3]["missing_source_CTUIDs"], ["5350205.00"])
            self.assertEqual(result["per_corridor"][21]["missing_source_CTUIDs"], ["5350006.00"])
            previous = json.loads((ROOT / "outputs/low_income_pilot_v0.3/proxy_summary.json").read_text())
            self.assertAlmostEqual(result["per_corridor"][1]["share"], previous["results"]["CT"]["share"], places=10)
            self.assertTrue(result["all_geographic_reviews_pending"])

    def test_readiness_does_not_depend_on_a_missing_notes_bypass(self):
        report = validate(ROOT)
        self.assertTrue(report["valid_structure"])
        self.assertFalse(report["model_ready"])
        self.assertTrue(any("9 selected input values are missing" in issue for issue in report["readiness_issues"]))


if __name__ == "__main__":
    unittest.main()
