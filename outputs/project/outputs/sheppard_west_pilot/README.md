# Corridor 01: Sheppard Avenue West geometry pilot

This pilot tests the geometry workflow before processing the remaining 23 corridors. It does not calculate population coverage, the Priority Populations Index, corridor rankings, or model results.

## Result

- Corridor: Sheppard West Station area to Sheppard-Yonge Station area.
- Source: City of Toronto Centreline, retrieved 21 November 2026, https://gis.toronto.ca/arcgis/rest/services/cot_geospatial/FeatureServer/2 . This is current geometry, not a frozen 2024 dataset.
- Method: shortest connected path restricted to named Sheppard Ave W road segments, between City network nodes 13450458 (Allen Road junction) and 13448689 (Yonge Street junction).
- Joined segments: 33. The archive preserves all source segment IDs and attributes.
- Measured road length: 4.407067 km. Report assumed length: 4.404 km. Difference: 3.067 m. Length agreement is a useful check, not proof of transit alignment accuracy.
- Buffer: 500 m perpendicular distance on each side, with round end caps, calculated in EPSG:2952 (metres). Area: 5.192196 km2. No clipping to municipal boundaries or land polygons.
- GeoJSON delivery CRS: EPSG:4326, longitude/latitude. Reproject to EPSG:2952 before measuring or buffering.

## Files

- corridor_01_boundary_pilot.png / .svg: static map, usable without web access.
- corridor_01_interactive_map.html: interactive map; Leaflet dependencies and OSM background tiles require web access. OSM supplies background tiles only, not the pilot centreline.
- corridor_01_pilot.qgz: styled QGIS project with three relative-path GeoJSON layers. Opening in the running QGIS application was verified.
- corridor_01_centerline.geojson: joined road centreline proxy.
- corridor_01_buffer_500m.geojson: analytical proximity polygon.
- corridor_01_endpoints.geojson: two road-junction endpoint proxies.
- source_centerline_segments.geojson: original 33 source road features.
- pilot_summary.json / qgis_setup_status.json: measurements, assumptions and setup verification.

## QGIS and QuickOSM setup

Official QGIS 3.44.15 installer signature was valid (Open Source Geospatial Foundation). Windows Installer refused the normal MSI installation (exit 1601 / access error 0x80070005). The signed MSI was extracted into a local standalone runtime under the workspace work/tools/QGIS directory; it is not registered as a normal Windows installation.

QuickOSM 2.6.0 files are installed in the separate workspace profile work/qgis_profiles/profiles/default/python/plugins/QuickOSM. A PyQGIS check loaded its Processing provider and enumerated 12 algorithms. A new QGIS session displayed its toolbar and OSM copyright prompt, confirming GUI initialization. The default-profile GUI plugin manager became unresponsive, and acknowledging the new-session copyright prompt also timed out. No GUI query completed. The prepared profile can be launched with the local launcher in the top-level delivery folder.

Overpass API requests returned HTTP 406. No OSM road geometry was downloaded. TTC GTFS shapes were not extracted. The official City road network provides a traceable alternative; bus shapes may contain terminal loops and need separate route/direction/segment review.

The runtime and installer are kept outside the project archive because of their size. The QGZ and GeoJSON files can also be opened in an independently installed QGIS.

## Rebuild and checks

From the project directory, install code/requirements_gis.txt and run:

    python code/build_sheppard_pilot.py

Archived inputs are in evidence/gis. Rebuilding uses these archived files. The script asserts that the road is simple, the buffer is valid, successive segments join within 1 m, and merged length agrees with graph path length within 0.1 m. The static map was visually inspected and the three-layer QGIS project was opened successfully.

## Workload interpretation and remaining decisions

The pilot demonstrates that a simple corridor can be assembled from existing road geometry without tracing every vertex by hand. Software installation and source discovery were one-time overhead; this run does not establish a reliable minutes-per-corridor estimate. Reusing the pipeline will still require endpoint, branch and segment review for every corridor, especially corridors with curves, branches or off-road alignments.

Before final indicator calculations, confirm station-related endpoints and choose one consistent catchment definition across all 24 corridors. This road buffer is not an approved future subway alignment, construction footprint, station walkshed, or walking-network catchment. It includes areas between stations even where boarding is impossible. Population-weighted equity aggregation also needs census geometry, a population allocation method and verified index definitions. No equity input has been filled from this pilot.
