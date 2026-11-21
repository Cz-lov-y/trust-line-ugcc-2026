# Repository setup and snapshot scope

Snapshot date: 21 November 2026. Repository: Cz-lov-y/trust-line-ugcc-2026.

## Included

The canonical project data, schemas, authoritative admission/dictionary JSON, generated workbooks, source reports, source-score archive, validation/review outputs, Sheppard West GIS pilot, complete assistant handoff, original delivery ZIP, earlier standalone inventory exports, first-party workspace helper scripts and acquisition/inspection intermediates are included. The three originally named competition PDFs are in reference/competition.

The missing working-copy handoff was recovered verbatim from the existing delivery ZIP into the upload snapshot. The original working data and admission records were not altered. The repository preserves the original workspace layout; treat outputs/project as the canonical project, not the earlier exports or historical work helpers.

UPLOAD_MANIFEST_v0.1.csv lists every uploaded payload file except itself, with byte length, SHA-256 and Git blob SHA-1. It describes this snapshot. The older handoff inventory describes its earlier local snapshot, including some paths excluded from Git.

## Excluded software and duplicates

- QGIS MSI (580468736 bytes), extracted application CAB, and the separately downloaded QuickOSM ZIP.
- Reconstructed QGIS runtime under work/tools/QGIS, the external pip target work/gis_pydeps, mutable QGIS profiles/plugin vendor files and Python bytecode caches.
- The stale extracted duplicate outputs/TRUST_Line_project_v0.1/project.

The canonical project and original delivery ZIP remain complete as project artifacts. No missing data were imputed, no criterion was admitted and no model was run for this upload.

## QGIS and Python

The original machine ran QGIS 3.44.15-Solothurn from a local extraction after a normal MSI installation failed. That runtime is not included in Git. Install QGIS from https://qgis.org/ and QuickOSM from the official QGIS plugin repository: https://plugins.qgis.org/plugins/QuickOSM/ . The original signed installer was https://download.qgis.org/downloads/QGIS-OSGeo4W-3.44.15-2.msi .

Open outputs/project/outputs/sheppard_west_pilot/corridor_01_pilot.qgz in QGIS. Its GeoJSON layers use relative paths. It does not require QuickOSM to display the already acquired City geometry.

Validation uses standard-library Python. The non-QGIS pilot builder needs outputs/project/code/requirements_gis.txt and matplotlib. Use a dedicated environment; PyQGIS needs QGIS's own environment and should not be mixed with arbitrary external NumPy/GDAL/Qt binaries. Workbook regeneration uses the Codex artifact-tool runtime and requires a current ARTIFACT_NODE_MODULES path.

The outer Open_Sheppard_West_QGIS.cmd is a historical local convenience launcher. It expects the excluded runtime/profile beside the original workspace and will not work on a fresh clone without installation/configuration. Absolute C:/Users/... and Windows short paths inside historical logs/handoff/setup files describe the original machine; adapt them to the clone rather than assuming that software or directory exists.

## Data interpretation

City road geometry was acquired on 21 November 2026. It is not a historical 2024 proposed alignment. The pilot's 500 m continuous corridor buffer differs from station-buffer unions and walking-network catchments. The Priority Populations Index remains uncomputed; exact tract data/methodology, census population support and a consistent geographic method are still needed.

The repository currently has public visibility as configured by its owner. Its initial commit is preserved; this snapshot is added as a subsequent commit. No open-source licence is assigned to third-party source reports or competition materials by this upload; their existing notices remain with the originals.
