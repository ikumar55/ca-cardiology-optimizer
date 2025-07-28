import importlib.util
import os

import folium
import pandas as pd

# File paths
TRAVEL_MATRIX_PATH = "data/processed/travel_matrix.parquet"
DEMAND_PATH = "data/processed/zip_demand.csv"
ZIP_COORDS_PATH = "src/data/travel_matrix/zip_coordinates_db.py"
OUTPUT_MAP = "udi_map.html"

def main():
    # Load travel matrix and demand data
    travel_matrix = pd.read_parquet(TRAVEL_MATRIX_PATH)
    demand = pd.read_csv(DEMAND_PATH)
    demand["zip_code"] = demand["zip_code"].astype(str)
    # Calculate min travel time and UDI flag
    min_travel = travel_matrix.groupby("zip_code")["drive_minutes"].min().reset_index()
    min_travel = min_travel.rename(columns={"drive_minutes": "min_travel_minutes"})
    min_travel["zip_code"] = min_travel["zip_code"].astype(str)
    min_travel["UDI_flag"] = (min_travel["min_travel_minutes"] > 6).astype(int)
    udi_df = pd.merge(min_travel, demand, on="zip_code", how="left")

    # Dynamically import ZipCoordinatesDB
    spec = importlib.util.spec_from_file_location("zip_coordinates_db", ZIP_COORDS_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for {ZIP_COORDS_PATH}")
    zip_coords_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(zip_coords_mod)
    ZipCoordinatesDB = zip_coords_mod.ZipCoordinatesDB
    zip_db = ZipCoordinatesDB()

    # Get coordinates for all ZIPs in udi_df
    zip_list = udi_df["zip_code"].unique().tolist()
    zip_to_latlon = zip_db.batch_get_coordinates(zip_list)
    coords_df = pd.DataFrame([
        {"zip_code": z, "lat": lat, "lon": lon} for z, (lat, lon) in zip_to_latlon.items()
    ])
    # Merge coordinates
    udi_map_df = pd.merge(udi_df, coords_df, on="zip_code", how="left")
    # Create Folium map centered on California
    m = folium.Map(location=[36.7783, -119.4179], zoom_start=6, tiles="cartodbpositron")
    for _, row in udi_map_df.iterrows():
        if pd.isna(row["lat"]) or pd.isna(row["lon"]):
            continue
        color = "red" if row["UDI_flag"] == 1 else "blue"
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=6 if row["UDI_flag"] == 1 else 4,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=(
                f"ZIP: {row['zip_code']}<br>"
                f"Min Travel: {row['min_travel_minutes']:.1f} min<br>"
                f"UDI: {row['UDI_flag']}"
            ),
            tooltip=(
                f"ZIP: {row['zip_code']} | Min: {row['min_travel_minutes']:.1f} min | UDI: {row['UDI_flag']}"
            ),
        ).add_to(m)
    m.save(OUTPUT_MAP)
    print(f"UDI map saved to {OUTPUT_MAP}")

def visualize_statewide_udi_access():
    import importlib.util

    import folium
    import pandas as pd
    access = pd.read_csv('data/processed/ca_zip_access_metrics.csv', dtype={'zip_code': str})
    spec = importlib.util.spec_from_file_location('zip_coordinates_db', 'src/data/travel_matrix/zip_coordinates_db.py')
    if spec is None or spec.loader is None:
        raise ImportError("Could not load spec for src/data/travel_matrix/zip_coordinates_db.py")
    zip_coords_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(zip_coords_mod)
    ZipCoordinatesDB = zip_coords_mod.ZipCoordinatesDB
    zip_db = ZipCoordinatesDB()
    coords = access['zip_code'].map(lambda z: zip_db.get_coordinates(z))
    access['lat'] = coords.map(lambda x: x[0] if x else None)
    access['lon'] = coords.map(lambda x: x[1] if x else None)
    m = folium.Map(location=[36.7783, -119.4179], zoom_start=6, tiles='cartodbpositron')
    for _, row in access.iterrows():
        color = 'red' if row['UDI_flag'] == 1 else 'blue'
        if pd.notna(row['lat']) and pd.notna(row['lon']):
            popup = (
                f"ZIP: {row['zip_code']}<br>"
                f"Min: {row['min_travel_minutes']:.1f} min<br>"
                f"Median: {row['median_travel_minutes']:.1f} min<br>"
                f"Mean: {row['mean_travel_minutes']:.1f} min<br>"
                f"Providers ≤30min: {row['providers_within_30min']}<br>"
                f"UDI: {row['UDI_flag']}"
            )
            tooltip = f"ZIP: {row['zip_code']} | Min: {row['min_travel_minutes']:.1f} min | UDI: {row['UDI_flag']}"
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=6 if row['UDI_flag'] == 1 else 4,
                color=color,
                fill=True,
                fill_opacity=0.7,
                popup=popup,
                tooltip=tooltip
            ).add_to(m)
    m.save('statewide_udi_access_map.html')
    print('Map saved as statewide_udi_access_map.html')

def visualize_statewide_udi_access_full():
    import importlib.util

    import folium
    import pandas as pd
    access = pd.read_csv('data/processed/ca_zip_access_metrics_full.csv', dtype={'zip_code': str})
    spec = importlib.util.spec_from_file_location('zip_coordinates_db', 'src/data/travel_matrix/zip_coordinates_db.py')
    if spec is None or spec.loader is None:
        raise ImportError("Could not load spec for src/data/travel_matrix/zip_coordinates_db.py")
    zip_coords_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(zip_coords_mod)
    ZipCoordinatesDB = zip_coords_mod.ZipCoordinatesDB
    zip_db = ZipCoordinatesDB()
    coords = access['zip_code'].map(lambda z: zip_db.get_coordinates(z))
    access['lat'] = coords.map(lambda x: x[0] if x else None)
    access['lon'] = coords.map(lambda x: x[1] if x else None)

    # Log missing ZIPs
    missing = access[access['lat'].isna() | access['lon'].isna()]
    if not missing.empty:
        print(f"WARNING: {len(missing)} ZIPs missing coordinates out of {len(access)} total.")
        print("Missing ZIPs:", missing['zip_code'].tolist())
    else:
        print("All ZIPs have coordinates.")

    m = folium.Map(location=[36.7783, -119.4179], zoom_start=6, tiles='cartodbpositron')
    for _, row in access.iterrows():
        color = 'red' if row['UDI_flag'] == 1 else 'blue'
        if pd.notna(row['lat']) and pd.notna(row['lon']):
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=6 if row['UDI_flag'] == 1 else 4,
                color=color,
                fill=True,
                fill_opacity=0.7,
                popup=(
                    f"ZIP: {row['zip_code']}<br>"
                    f"Min: {row['min_travel_minutes']:.1f} min<br>"
                    f"Median: {row['median_travel_minutes']:.1f} min<br>"
                    f"Providers ≤30min: {row['providers_within_30min']}"
                ),
                tooltip=(
                    f"ZIP: {row['zip_code']} | Min: {row['min_travel_minutes']:.1f} min"
                )
            ).add_to(m)
    m.save('statewide_udi_access_map_full.html')
    print('Saved map to statewide_udi_access_map_full.html')

def diagnostic_plot_all_demand_zips():
    import importlib.util
    import os

    import folium
    import pandas as pd
    zip_db_path = os.path.join(os.path.dirname(__file__), '../travel_matrix/zip_coordinates_db.py')
    spec = importlib.util.spec_from_file_location('zip_coordinates_db', zip_db_path)
    zip_coords_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(zip_coords_mod)
    ZipCoordinatesDB = zip_coords_mod.ZipCoordinatesDB
    zips = pd.read_csv('data/processed/ca_zip_demand_list_final.csv', dtype=str)['zip_code'].str.zfill(5)
    zip_db = ZipCoordinatesDB()
    coords = zips.map(lambda z: zip_db.get_coordinates(z))
    m = folium.Map(location=[36.7783, -119.4179], zoom_start=6, tiles='cartodbpositron')
    count = 0
    for zip_code, coord in zip(zips, coords):
        if coord is not None:
            folium.CircleMarker(location=coord, radius=3, color='green', fill=True, fill_opacity=0.6, popup=zip_code).add_to(m)
            count += 1
    m.save('diagnostic_all_demand_zips_map.html')
    print(f'Plotted {count} ZIPs out of {len(zips)} (should be statewide)')

if __name__ == "__main__":
    main()
    visualize_statewide_udi_access()
    diagnostic_plot_all_demand_zips() 