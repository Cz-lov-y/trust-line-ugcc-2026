"""Batch current-road proximity catchments; keep unresolved alignments blank."""
from pathlib import Path
import argparse
from collections import defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import heapq
import json
import math
import urllib.request

import shapely
from shapely.geometry import shape, LineString, Point, mapping
from shapely.ops import substring, unary_union
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
CITY_RESOURCE = "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/1d079757-377b-4564-82df-eb5638583bfb/resource/7bc94ccf-7bcf-4a7d-88b1-bdfc8ec5aaf1/download/centreline-version-2-4326.geojson"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def archive_subset(root, full_source):
    root = Path(root)
    folder = root / "evidence/corridor_batch_v0.4"
    folder.mkdir(parents=True, exist_ok=True)
    spec_path = root / "data/corridor_road_proxy_specs_v0.4.json"
    specs = json.loads(spec_path.read_text())
    names = {name for spec in specs["specifications"] for field in ["roads", "cross_a", "cross_b"] for name in spec.get(field, [])}
    raw = json.loads(Path(full_source).read_text())
    features = [f for f in raw["features"] if f["properties"]["LINEAR_NAME_FULL"] in names]
    target = folder / "named_road_source_features.geojson"
    target.write_text(json.dumps({"type": "FeatureCollection", "features": features}) + "\n")
    manifest = {"source_id": "CITY_CENTRELINE_CKAN_CURRENT", "url": CITY_RESOURCE,
                "retrieved_utc": datetime.fromtimestamp(Path(full_source).stat().st_mtime, timezone.utc).isoformat(),
                "full_download_size_bytes": Path(full_source).stat().st_size, "full_download_sha256": sha(full_source),
                "full_feature_count": len(raw["features"]), "selected_names": sorted(names),
                "selected_feature_count": len(features), "subset_file": str(target.relative_to(root)),
                "subset_sha256": sha(target), "selection": "Exact LINEAR_NAME_FULL membership; original selected feature geometry and properties retained",
                "arcgis_query_attempt": "City FeatureServer/2 ID query timed out after 25 seconds; official CKAN download succeeded."}
    (folder / "road_acquisition_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def path_between(graph, start, end):
    queue = [(0.0, start)]
    distance = {start: 0.0}
    previous = {}
    while queue:
        value, node = heapq.heappop(queue)
        if value != distance[node]:
            continue
        if node == end:
            break
        for following, length, feature, line in graph[node]:
            candidate = value + length
            if candidate < distance.get(following, math.inf):
                distance[following] = candidate
                previous[following] = node, feature, line
                heapq.heappush(queue, (candidate, following))
    if end not in distance:
        raise ValueError("Named-road segments do not provide a connected path; no gap bridge introduced")
    result = []
    node = end
    while node != start:
        before, feature, line = previous[node]
        result.append((before, node, feature, line))
        node = before
    return list(reversed(result)), distance[end]


def build(root=ROOT, output=None):
    root = Path(root)
    output = Path(output) if output else root / "outputs/corridor_batch_v0.4"
    output.mkdir(parents=True, exist_ok=True)
    spec_path = root / "data/corridor_road_proxy_specs_v0.4.json"
    specs = json.loads(spec_path.read_text())
    evidence = root / "evidence/corridor_batch_v0.4"
    acquisition = json.loads((evidence / "road_acquisition_manifest.json").read_text())
    source = root / acquisition["subset_file"]
    if sha(source) != acquisition["subset_sha256"]:
        raise ValueError("Road source subset checksum mismatch")
    features = json.loads(source.read_text())["features"]
    projected = Transformer.from_crs(4326, 2952, always_xy=True)
    geographic = Transformer.from_crs(2952, 4326, always_xy=True)
    by_name = defaultdict(list)
    nodes_by_name = defaultdict(set)
    node_coordinates = {}
    for feature in features:
        properties = feature["properties"]
        geometry = shape(feature["geometry"])
        if geometry.geom_type == "MultiLineString":
            geometry = shapely.line_merge(geometry)
        if geometry.geom_type != "LineString":
            continue
        line = shapely.transform(geometry, projected.transform, interleaved=False)
        a, b = properties["FROM_INTERSECTION_ID"], properties["TO_INTERSECTION_ID"]
        by_name[properties["LINEAR_NAME_FULL"]].append((a, b, feature, line))
        nodes_by_name[properties["LINEAR_NAME_FULL"]].update([a, b])
        node_coordinates.setdefault(a, tuple(line.coords[0]))
        node_coordinates.setdefault(b, tuple(line.coords[-1]))
    with (root / "data/corridor_master_v0.1.csv").open(encoding="utf-8-sig", newline="") as stream:
        master = {int(row["corridor_id"]): row for row in csv.DictReader(stream)}
    status_rows, lines, buffers, reviews = [], [], [], []
    for spec in specs["specifications"]:
        cid = spec["corridor_id"]
        metadata = master[cid]
        row = {"corridor_id": cid, "corridor_name": metadata["corridor_name"],
               "geometry_status": "pending_alignment", "measured_route_length_km": "",
               "source_construction_length_km": metadata["length_km"], "buffer_area_km2": "",
               "endpoint_method": "named_road_intersection_proxies", "geographic_review": "pending",
               "reason_or_limitations": spec.get("blocked_reason", spec.get("note", "Current road proxy; endpoint/station and alignment review pending."))}
        if spec.get("blocked_reason"):
            status_rows.append(row)
            continue
        try:
            if spec.get("reuse_archived_pilot"):
                pilot = root / "outputs/sheppard_west_pilot"
                line = shape(json.loads((pilot / "corridor_01_centerline.geojson").read_text())["features"][0]["geometry"])
                buffer = shape(json.loads((pilot / "corridor_01_buffer_500m.geojson").read_text())["features"][0]["geometry"])
                metric_line = shapely.transform(line, projected.transform, interleaved=False)
                metric_buffer = shapely.transform(buffer, projected.transform, interleaved=False)
                review = {"corridor_id": cid, "method": "Reuse exact v0.1 archived pilot", "segment_ids": json.loads((pilot / "pilot_summary.json").read_text())["segment_ids"]}
            else:
                graph = defaultdict(list)
                main_nodes = set()
                main_entries = []
                for name in spec["roads"]:
                    for a, b, feature, road in by_name[name]:
                        graph[a].append((b, road.length, feature, road))
                        graph[b].append((a, road.length, feature, road))
                        main_nodes.update([a, b])
                        main_entries.append((a, b, feature, road))
                if not main_nodes:
                    raise ValueError("No named corridor road features in source")
                endpoint_info = []
                for endpoint_index, cross in enumerate([spec["cross_a"], spec["cross_b"]]):
                    endpoint_roads = spec.get("endpoint_a_roads" if endpoint_index == 0 else "endpoint_b_roads", spec["roads"])
                    allowed_nodes = set().union(*(nodes_by_name[name] for name in endpoint_roads))
                    candidates = sorted(allowed_nodes & set().union(*(nodes_by_name[name] for name in cross)))
                    if not candidates:
                        if not spec.get("allow_geometric_crossing"):
                            raise ValueError("No shared intersection node with " + ";".join(cross))
                        crossings = unary_union([entry[3] for name in cross for entry in by_name[name]])
                        main_lines = unary_union([entry[3] for name in endpoint_roads for entry in by_name[name]])
                        intersections = main_lines.intersection(crossings)
                        points = [intersections] if intersections.geom_type == "Point" else [g for g in getattr(intersections, "geoms", []) if g.geom_type == "Point"]
                        if not points:
                            raise ValueError("No planar source-road crossing with " + ";".join(cross))
                        center = (sum(point.x for point in points) / len(points), sum(point.y for point in points) / len(points))
                        if max(math.dist((point.x, point.y), center) for point in points) > 250:
                            raise ValueError("Distant ambiguous planar source-road crossings")
                        point = min(points, key=lambda point: math.dist((point.x, point.y), center))
                        a, b, feature, road = min(main_entries, key=lambda entry: entry[3].distance(point))
                        if road.distance(point) > 0.1:
                            raise ValueError("Planar endpoint is not on a source corridor edge")
                        position = road.project(point)
                        chosen = -(cid * 10 + endpoint_index)
                        node_coordinates[chosen] = (point.x, point.y)
                        fid = feature["properties"]["CENTRELINE_ID"]
                        graph[a] = [edge for edge in graph[a] if not (edge[0] == b and edge[2]["properties"]["CENTRELINE_ID"] == fid)]
                        graph[b] = [edge for edge in graph[b] if not (edge[0] == a and edge[2]["properties"]["CENTRELINE_ID"] == fid)]
                        for before, after, piece in [(a, chosen, substring(road, 0, position)), (chosen, b, substring(road, position, road.length))]:
                            if piece.geom_type != "LineString" or piece.length <= 0:
                                raise ValueError("Planar split coincides with an existing endpoint; review its node identity")
                            graph[before].append((after, piece.length, feature, piece))
                            graph[after].append((before, piece.length, feature, piece))
                        endpoint_info.append({"cross_streets": cross, "chosen_node_id": chosen,
                                              "method": "planar_source_edge_split", "source_segment_id": fid,
                                              "source_edge_distance_m": position, "grade_connectivity_not_asserted": True})
                        continue
                    x = sum(node_coordinates[n][0] for n in candidates) / len(candidates)
                    y = sum(node_coordinates[n][1] for n in candidates) / len(candidates)
                    if max(math.dist(node_coordinates[n], (x, y)) for n in candidates) > 250:
                        raise ValueError("Ambiguous distant crossing nodes for " + ";".join(cross))
                    chosen = min(candidates, key=lambda n: (math.dist(node_coordinates[n], (x, y)), n))
                    endpoint_info.append({"cross_streets": cross, "candidate_node_ids": candidates, "chosen_node_id": chosen})
                path, distance = path_between(graph, endpoint_info[0]["chosen_node_id"], endpoint_info[1]["chosen_node_id"])
                coordinates = []
                maximum_join_gap = 0.0
                for a, b, feature, road in path:
                    points = list(road.coords)
                    if math.dist(points[-1], node_coordinates[a]) < math.dist(points[0], node_coordinates[a]):
                        points.reverse()
                    if coordinates:
                        gap = math.dist(coordinates[-1], points[0])
                        maximum_join_gap = max(maximum_join_gap, gap)
                        if gap > 1:
                            raise ValueError(f"Source path join gap exceeds 1 m: {gap}")
                    coordinates += points if not coordinates else points[1:]
                metric_line = LineString(coordinates)
                if not metric_line.is_simple or abs(metric_line.length - distance) > 0.1:
                    raise ValueError("Path geometry/graph length or simplicity check failed")
                metric_buffer = metric_line.buffer(specs["buffer_m"], quad_segs=48)
                line = shapely.transform(metric_line, geographic.transform, interleaved=False)
                buffer = shapely.transform(metric_buffer, geographic.transform, interleaved=False)
                review = {"corridor_id": cid, "roads": spec["roads"], "endpoints": endpoint_info,
                          "segment_ids": [f["properties"]["CENTRELINE_ID"] for _, _, f, _ in path],
                          "maximum_join_gap_m": maximum_join_gap}
            if not metric_buffer.is_valid:
                raise ValueError("Invalid corridor buffer")
            row.update(geometry_status="road_proxy_pending_review", measured_route_length_km=metric_line.length / 1000,
                       buffer_area_km2=metric_buffer.area / 1e6)
            review["construction_length_relative_difference"] = metric_line.length / (1000 * float(metadata["length_km"])) - 1
            review["length_comparison_is_alignment_proof"] = False
            lines.append({"type": "Feature", "geometry": mapping(line), "properties": row.copy()})
            buffers.append({"type": "Feature", "geometry": mapping(buffer), "properties": row.copy()})
            reviews.append(review)
        except ValueError as error:
            row["geometry_status"] = "pending_endpoint_or_topology"
            row["reason_or_limitations"] = str(error) + "; " + row["reason_or_limitations"]
        status_rows.append(row)
    if len(status_rows) != 24 or {r["corridor_id"] for r in status_rows} != set(range(1, 25)):
        raise ValueError("Geometry register must retain exactly all 24 corridors")
    for filename, collection in [("corridor_road_proxies.geojson", lines), ("corridor_buffers_500m.geojson", buffers)]:
        (output / filename).write_text(json.dumps({"type": "FeatureCollection", "features": collection}) + "\n")
    with (output / "geometry_status.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(status_rows[0])); writer.writeheader(); writer.writerows(status_rows)
    summary = {"available_corridor_ids": [r["corridor_id"] for r in status_rows if r["geometry_status"] == "road_proxy_pending_review"],
               "pending_corridor_ids": [r["corridor_id"] for r in status_rows if r["geometry_status"] != "road_proxy_pending_review"],
               "review_details": reviews, "source_sha256": sha(source), "specification_sha256": sha(spec_path),
               "buffer_m": 500, "measurement_crs": "EPSG:2952", "all_geographic_reviews_pending": True}
    (output / "geometry_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "review_details"}, indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=ROOT)
    parser.add_argument("--full-city-source", type=Path, help="Archive the named-road subset from an official whole-city GeoJSON download")
    args = parser.parse_args()
    if args.full_city_source:
        archive_subset(args.project, args.full_city_source)
    build(args.project)
