"""Prepare a reviewable GitHub snapshot without editing the original project data."""
from pathlib import Path
import csv,hashlib,json,shutil,zipfile,re

ROOT=Path(__file__).resolve().parent.parent
STAGE=ROOT/'work/github_upload'
STAGE.mkdir(parents=True,exist_ok=True)
COPIED=[]

def copy(src,dest):
    target=STAGE/dest
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,target)
    COPIED.append(dest)

for src in sorted((ROOT/'outputs/project').rglob('*')):
    if src.is_file() and '__pycache__' not in src.parts:
        copy(src,src.relative_to(ROOT).as_posix())

# The delivered ZIP contains the complete handoff even though the working copy is absent.
handoff=STAGE/'outputs/project/HANDOFF_v0.1.md'
if not handoff.exists():
    with zipfile.ZipFile(ROOT/'outputs/TRUST_Line_project_v0.1.zip') as z:
        handoff.write_bytes(z.read('project/HANDOFF_v0.1.md'))
    COPIED.append('outputs/project/HANDOFF_v0.1.md')

# Preserve earlier exports and the complete delivery archive, without the stale extracted duplicate.
for src in sorted((ROOT/'outputs').iterdir()):
    if src.is_file():copy(src,src.relative_to(ROOT).as_posix())

# Keep first-party acquisition/build history, but not third-party installers or runtime trees.
excluded={'QGIS-OSGeo4W-3.44.15-2.msi','qgis_application.cab','QuickOSM-2.6.0.zip'}
for src in sorted((ROOT/'work').iterdir()):
    if src.is_file() and src.name not in excluded and not src.name.startswith('github_upload_'):
        copy(src,src.relative_to(ROOT).as_posix())

case_dir=Path(r'C:\Users\pipis\OneDrive\桌面\ugcc')
for name in ['STAT Case UGCC 2026.pdf','UGCC 2026 Guideline Package-1-18.pdf','UGCC 2026 Guideline Package-20-21.pdf']:
    src=case_dir/name
    if src.exists():copy(src,'reference/competition/'+name)

readme='''# TRUST-Line - UGCC 2026

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
'''
(STAGE/'README.md').write_text(readme,encoding='utf-8')
(STAGE/'.gitignore').write_text('''# Python and editor caches
__pycache__/
*.py[cod]
.venv/
venv/
.DS_Store
Thumbs.db

# Reinstall software from official sources; do not version runtime/vendor trees.
work/tools/
work/gis_pydeps/
work/qgis_profiles/
work/qgis_cab/
work/qgis_admin/
work/github_upload/
work/github_upload_*
*.msi
*.cab

# Local credentials and transient environment files
.env
.env.*
''',encoding='utf-8')
(STAGE/'REPOSITORY_SETUP.md').write_text('''# Repository setup and snapshot scope

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
''',encoding='utf-8')

# Git does not preserve empty directories, so keep the requested slides directory visible.
slides=STAGE/'outputs/project/slides'
slides.mkdir(parents=True,exist_ok=True)
(slides/'.gitkeep').write_text('',encoding='utf-8')

manifest=[]
for f in sorted(STAGE.rglob('*')):
    if not f.is_file() or f.name=='UPLOAD_MANIFEST_v0.1.csv':continue
    data=f.read_bytes()
    if len(data)>=100*1024*1024:raise ValueError('Oversized Git payload: '+str(f))
    manifest.append(dict(path=f.relative_to(STAGE).as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),git_blob_sha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()))
with (STAGE/'UPLOAD_MANIFEST_v0.1.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['path','bytes','sha256','git_blob_sha']);w.writeheader();w.writerows(manifest)
f=STAGE/'UPLOAD_MANIFEST_v0.1.csv';data=f.read_bytes()
manifest.append(dict(path=f.relative_to(STAGE).as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),git_blob_sha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()))
(ROOT/'work/github_upload_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'stage':str(STAGE),'files':len(manifest),'total_mb':round(sum(x['bytes'] for x in manifest)/1e6,2),'largest':sorted(manifest,key=lambda x:-x['bytes'])[:5],'handoff_recovered':handoff.exists(),'original_project_modified':False},indent=2))
