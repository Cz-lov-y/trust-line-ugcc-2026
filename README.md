# TRUST-Line - UGCC 2026

Evidence, data preparation, reproducible code, geometry pilot and assistant handoff for the UTSRI x NRCI 2026 UGCC statistics case, "Drawing Toronto's Line of Best Fit".

## Start here

- [Complete assistant handoff](outputs/project/HANDOFF_v0.1.md)
- [Current project strategy and reproduction instructions](outputs/project/README.md)
- [Input coverage](outputs/project/data/model_input_coverage_v0.1.csv)
- [Validation status](outputs/project/outputs/validation_v0.1.json)
- [Sheppard West geometry pilot](outputs/project/outputs/sheppard_west_pilot/README.md)
- [Repository setup and upload scope](REPOSITORY_SETUP.md)

## Current status

All 24 alternatives are retained. Part 1 excludes construction costs and cost-normalized measures. Source missingness is preserved without imputation. No ranking, optimization or simulation has been run.

The five selected non-cost City score columns contain 98 published values and 22 missing values. The supplemental Priority Populations Index has not been computed for any corridor. Structural validation passes, but **model_ready remains false**.

Corridor 01, Sheppard Ave West, has an official City road-centreline proxy of **4.407 km** and a trial **500 m** buffer of **5.192 km2**. This is a geometry test, not the chosen winning corridor or an approved future transit alignment.

![Sheppard West boundary pilot](outputs/project/outputs/sheppard_west_pilot/corridor_01_boundary_pilot.png)

## Repository layout

```text
outputs/project/       Canonical project snapshot: data, code, evidence, maps and handoff
outputs/*.zip          Complete original delivery archive
outputs/               Earlier inventory exports and local convenience launcher
reference/competition/ Original user-supplied case and guideline PDFs
work/                  Historical acquisition, preparation and audit helpers/intermediates
```

The workspace layout is retained so source-relative paths remain understandable. The older extracted duplicate `outputs/TRUST_Line_project_v0.1/project` and software runtime trees are not copied into Git. Do not execute historical `work` generators without reading them; some overwrite newer data and documentation.

## Validate

From the canonical project directory:

```powershell
cd outputs/project
python -B code/validate_data.py --output outputs/validation_v0.1.json
```

Read the JSON: a zero process exit does not mean the inputs are ready for modelling. See the handoff for exact dependencies and next steps for tract-level PPI acquisition and population-weighted corridor aggregation.
