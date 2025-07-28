import importlib.util
import os
from itertools import product
from math import atan2, cos, radians, sin, sqrt

import pandas as pd

# File paths
DEMAND_ZIPS_PATH = 'data/processed/ca_zip_demand_list_final.csv'
PROVIDERS_PATH = 'data/processed/ca_cardiology_providers.csv'
COORDS_PATH = 'src/data/travel_matrix/zip_coordinates_db.py'
OUTPUT_PATH = 'data/processed/travel_matrix_full.csv'

# Haversine formula (with road fudge factor)
def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8  # miles
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c * 1.15  # 1.15 fudge for road network

def main():
    print('Loading data...')
    demand_zips = pd.read_csv(DEMAND_ZIPS_PATH, dtype=str)['zip_code'].tolist()
    providers = pd.read_csv(PROVIDERS_PATH, dtype={'ZIP': str})
    provider_zips = providers['ZIP'].unique()
    print(f'Demand ZIPs: {len(demand_zips)} | Provider ZIPs: {len(provider_zips)}')

    # Load coordinate DB
    spec = importlib.util.spec_from_file_location('zip_coordinates_db', COORDS_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f'Could not load spec for {COORDS_PATH}')
    zip_coords_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(zip_coords_mod)
    ZipCoordinatesDB = zip_coords_mod.ZipCoordinatesDB
    zip_db = ZipCoordinatesDB()

    pairs = list(product(demand_zips, provider_zips))
    print(f'Total demand-provider pairs: {len(pairs)}')

    batch_size = 100000
    out = []
    for i, (dz, pz) in enumerate(pairs):
        d = zip_db.get_coordinates(dz)
        p = zip_db.get_coordinates(pz)
        if d and p:
            dist = haversine(d[0], d[1], p[0], p[1])
            out.append({'zip_code': dz, 'provider_zip': pz, 'drive_minutes': dist})
        if (i+1) % batch_size == 0 or (i+1) == len(pairs):
            print(f'{i+1} pairs processed...')
            df = pd.DataFrame(out)
            if os.path.exists(OUTPUT_PATH) and i+1 != batch_size:
                df.to_csv(OUTPUT_PATH, mode='a', header=False, index=False)
            else:
                df.to_csv(OUTPUT_PATH, index=False)
            out = []
    print(f'Done. Saved to {OUTPUT_PATH}')

if __name__ == '__main__':
    main() 