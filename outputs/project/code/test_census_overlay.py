"""Population-accounting regression checks: run using the isolated GIS environment."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest

from shapely.geometry import box, Polygon

from audit_census_overlay import audit, classify_block, population_bounds, read_csv, ROOT


class PopulationAccountingTests(unittest.TestCase):
    def test_partial_area_never_implies_population_fraction(self):
        status, fraction, _, _ = classify_block(box(0, 0, 10, 10), box(0, 0, 5, 10))
        self.assertEqual(status, "partially_inside")
        self.assertEqual(fraction, 0.5)
        self.assertEqual(population_bounds(status, 100), (0, 100))

    def test_fully_contained_block_has_equal_bounds(self):
        status, _, _, _ = classify_block(box(0, 0, 10, 10), box(-1, -1, 11, 11))
        self.assertEqual(population_bounds(status, 100), (100, 100))

    def test_boundary_touch_does_not_count_population(self):
        status, fraction, _, _ = classify_block(box(0, 0, 10, 10), box(10, 0, 20, 10))
        self.assertEqual((status, fraction), ("outside", 0.0))
        self.assertEqual(population_bounds(status, 100), (0, 0))

    def test_missing_population_is_not_zero(self):
        self.assertEqual(population_bounds("partially_inside", None), (None, None))
        self.assertEqual(population_bounds("fully_inside", None), (None, None))
        self.assertEqual(population_bounds("partially_inside", 0), (0, 0))

    def test_negative_population_and_invalid_geometry_fail(self):
        with self.assertRaises(ValueError):
            population_bounds("fully_inside", -1)
        with self.assertRaises(ValueError):
            classify_block(Polygon([(0, 0), (10, 10), (0, 10), (10, 0)]), box(0, 0, 10, 10))

    def test_archived_data_reconcile_and_keep_all_alternatives(self):
        with tempfile.TemporaryDirectory() as directory:
            with contextlib.redirect_stdout(io.StringIO()):
                result = audit(ROOT, directory, repair_invalid=True)
            rows = read_csv(Path(directory) / "corridor_ppi_audit_v0.2.csv")
            self.assertEqual([r["corridor_id"] for r in rows], [str(i) for i in range(1, 25)])
            self.assertTrue(all(r["priority_populations_index"] == "" for r in rows))
            self.assertTrue(all(r["ppi_denominator"] == "" for r in rows))
            blocks = read_csv(Path(directory) / "pilot_db_intersections.csv")
            self.assertTrue(all(r["estimated_covered_population"] == "" for r in blocks))
            self.assertEqual(result["missing_population_db_ids"], [])
            self.assertAlmostEqual(result["buffer_area_without_db_polygon_m2"], 0, places=3)
            self.assertFalse(result["model_ready"])
            # Independent census-count reconciliation, not an area-weighted estimate.
            total_inside = sum(int(r["source_population_2021"]) for r in blocks if r["geometry_status"] == "fully_inside")
            total_intersecting = sum(int(r["source_population_2021"]) for r in blocks)
            self.assertEqual(result["population_lower_bound"], total_inside)
            self.assertEqual(result["population_upper_bound"], total_intersecting)


if __name__ == "__main__":
    unittest.main()
