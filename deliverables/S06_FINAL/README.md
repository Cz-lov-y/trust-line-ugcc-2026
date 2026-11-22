# S06 TRUST-Line — final assembled version

Recommendation: **corridor 23, Finch East (Yonge–Victoria Park), BRT**, with feasible future LRT options studied rather than promised. Team: Zhuo Chen; Yue Tang; Yuen Song (Rain); Zihan Cao (Dalton).

## Use these files

- `S06_TRUST_LINE_FINAL.pptx`: integrated eleven-slide whole-case presentation. Both models, EDA, sensitivity, single-technology recommendation, AI disclosure and references are present. Last slide: **Final Recommendation: BRT**.
- `S06_ABSTRACT.pdf`: 167-word English body, two references, full team identification; no figures/tables/equations. Plain English and Chinese short versions are provided.
- `REHEARSAL_10MIN.md`, `REHEARSAL_SPLITS.csv`, `REHEARSAL_TIMER.html`: one whole-case pacing plan, including Task 1, disclosure and references. Actual speaking/transition times are not invented; practice aloud and record them. Notes and timer are private, not judge-facing props.
- `REFERENCES.md`, `STATUS.json`, `MANIFEST.json`: citations, factual readiness/limitations and file checksums.

## Decisions and limits

The primary formula and equal weights are unchanged. BRT wins the equal/capital-efficiency cases; LRT wins the declared service-benefit case. No universal-robustness claim is made. Eight conditional corridors retain prerequisite/bundle assessment instead of fabricated common-base ranks. Census allocation, City missing-value scenarios, partial principle coverage, cost price/scope and assumed demand/time are disclosed.

The cost point is hypothetical, the milestone programme is assumed 6–9 years with zero extra buffer in its upper case, and future LRT conversion has not been costed or certified. There is no guaranteed opening, verified fiscal surplus or seamless-conversion claim.

AI policy basis: the team/user explicitly confirmed on 2026-11-22 that AI is unrestricted under the applicable rules and instructed final assembly. Actual AI assistance remains fully disclosed. This confirmation is not represented as an independently obtained organizer letter. Earlier v0.5 cautionary files are historical snapshots, superseded on that policy premise and on team identity. No outside message or competition submission has been sent.

The ten-minute whole-case version is intentionally conservative because the supplied guideline contains both general ten-minute wording and Statistical Science fifteen-minute wording. No fifteen-minute permission is assumed.

## Supporting archive: numerical replay

The sibling `S06_TRUST_LINE_FINAL.zip` contains these deliverables plus structured data, computational source, delivered outputs and provenance/documentation. After extraction from the archive's root:

```sh
python -m pip install numpy
python outputs/project/code/replay_final_models_v1_0.py
```

The offline entry point recomputes all 144 contextual Part 1 scores, main-tier rank support and Part 2 scores/weight support, comparing with the delivered results. It uses delivered Census overlay estimates; it does not rebuild GIS overlays. Large geographic archives and public source PDFs are referenced through their original URLs/checksums rather than duplicated in this compact model package. The complete repository preserves raw acquisitions and historical validators: https://github.com/Cz-lov-y/trust-line-ugcc-2026

Full historical tests and source-byte audits should be run from the complete repository with its GIS and presentation requirements, rather than the compact archive. Do not confuse numerical replay with engineering certification or completed human rehearsal.
