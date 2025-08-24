# decode_vt_tiles.py
import os, json, glob
import mapbox_vector_tile
import mercantile
from shapely.geometry import shape, mapping, Point, LineString, Polygon

CAP_DIR = "captures"
OUT = "extracted_places.jsonl"

def tile_coords_to_lonlat(x_tile, y_tile, z_tile, x, y, extent=4096):
    # Convert tile-local coordinates (x,y) in [0, extent) to lon/lat
    # mercantile.bounds returns west,south,east,north
    bounds = mercantile.bounds(x_tile, y_tile, z_tile)
    west, south, east, north = bounds.west, bounds.south, bounds.east, bounds.north
    lon = west + (x / extent) * (east - west)
    # tile y origin is top; mercantile north is top
    lat = north - (y / extent) * (north - south)
    return lon, lat

def try_decode_pbf_file(pbf_path):
    data = open(pbf_path, "rb").read()
    try:
        decoded = mapbox_vector_tile.decode(data)
    except Exception as e:
        print("decode error for", pbf_path, e)
        return []

    # Attempt to obtain tile z/x/y from meta file or filename
    meta_path = pbf_path + ".meta.txt"
    z = x = y = None
    if os.path.exists(meta_path):
        txt = open(meta_path, "r", encoding="utf8").read()
        # naive search for 'x=' or 'zoom=' or queries
        import re
        m = re.search(r"[?&]x=(\d+)", txt)
        if m:
            x = int(m.group(1))
        m = re.search(r"[?&]y=(\d+)", txt)
        if m:
            y = int(m.group(1))
        m = re.search(r"[?&]zoom=(\d+)|[?&]z=(\d+)", txt)
        if m:
            # group may be None; pick first non-None
            z = int(m.group(1) or m.group(2))
    # If we couldn't find z/x/y, the conversion will be approximate.
    # Some Google tiles encode tile coords in the "pb" param. If missing,
    # we won't convert correctly — see next steps.
    places = []
    for layer_name, layer in decoded.items():
        features = layer.get("features", [])
        for feat in features:
            props = feat.get("properties", {})
            geom = feat.get("geometry")
            # geometry may be GeoJSON-like already
            if geom is None and "geometry" in feat:
                geom = feat["geometry"]
            # common key names for POIs
            name = props.get("name") or props.get("title") or props.get("label") or props.get("caption")
            # heuristics: POIs often have 'point' geometry
            if geom and name:
                # If the feature geometry gives coordinates in tile local coords,
                # mapbox_vector_tile returns coordinates in absolute pixel-like coords scaled to extent (default 4096)
                # We will attempt to convert the first point we find.
                coords = None
                # geometry may be dict type GeoJSON
                if isinstance(geom, dict) and geom.get("type") == "Point":
                    coords = geom.get("coordinates")
                elif isinstance(geom, list):
                    # list of rings/points
                    # flatten to find a point
                    def find_point(g):
                        if isinstance(g, (list,tuple)) and len(g)>0 and isinstance(g[0], (int,float)):
                            return g
                        if isinstance(g, list):
                            for item in g:
                                r = find_point(item)
                                if r:
                                    return r
                        return None
                    coords = find_point(geom)
                if coords:
                    # coords typically [x, y], but we need tile z/x/y and extent
                    # mapbox-vector-tile returns coords in the tile coordinate space (extent)
                    extent = layer.get("extent", 4096) or 4096
                    # If we couldn't find tile z/x/y, skip conversion
                    if z is None or x is None or y is None:
                        lonlat = None
                    else:
                        lonlat = tile_coords_to_lonlat(x, y, z, coords[0], coords[1], extent=extent)
                    places.append({
                        "source_file": pbf_path,
                        "layer": layer_name,
                        "name": name,
                        "properties": props,
                        "coords_tile": coords,
                        "lonlat": lonlat
                    })
    return places

def main():
    pbf_files = glob.glob(os.path.join(CAP_DIR, "*.pbf"))
    all_places = []
    for p in pbf_files:
        print("Decoding", p)
        places = try_decode_pbf_file(p)
        print("Found", len(places), "places in", p)
        all_places.extend(places)
    # write output
    with open(OUT, "w", encoding="utf8") as f:
        for p in all_places:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print("Wrote", OUT, "with", len(all_places), "items")

if __name__ == "__main__":
    main()
