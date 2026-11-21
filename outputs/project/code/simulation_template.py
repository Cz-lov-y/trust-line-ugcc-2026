"""Unexecuted simulation interface. Supply an evidence-supported sampler and scorer later."""
import random
from copy import deepcopy
from validate_data import EXPECTED_IDS

def assert_fixed_corridors(rows):
    ids = [str(r["corridor_id"]) for r in rows]
    if len(rows) != 24 or len(set(ids)) != 24 or set(ids) != EXPECTED_IDS:
        raise ValueError("Every draw must preserve the same 24 unique corridor IDs.")

def simulate(rows, draws, seed, sample_indicator_values, score_all_corridors):
    """Callbacks must implement documented assumptions; no default distributions are supplied.

    sample_indicator_values receives a deep copy and seeded RNG. It may change only
    indicator_* values. score_all_corridors returns an ID-to-score mapping for all 24.
    This template does not implement bootstrap resampling of corridor rows.
    """
    assert_fixed_corridors(rows)
    if draws < 1: raise ValueError("draws must be positive")
    rng = random.Random(seed)
    original = {str(r["corridor_id"]): r for r in rows}
    results = []
    for draw in range(draws):
        sampled = sample_indicator_values(deepcopy(rows), rng)
        assert_fixed_corridors(sampled)
        for r in sampled:
            base = original[str(r["corridor_id"])]
            if set(r) != set(base): raise ValueError("Sampler changed the schema")
            if any(r[k] != base[k] for k in base if not k.startswith("indicator_")):
                raise ValueError("Sampler changed corridor metadata")
        scores = score_all_corridors(sampled)
        if {str(k) for k in scores} != EXPECTED_IDS or len(scores) != 24:
            raise ValueError("Scoring must retain all 24 corridors")
        results.append({"draw_id": draw + 1, "scores": scores})
    return results

if __name__ == "__main__":
    print("Template only. No simulation executed. Define supported inputs, sampler, scorer, and scenario assumptions before use.")
