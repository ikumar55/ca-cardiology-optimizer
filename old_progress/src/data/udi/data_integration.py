import pandas as pd
import pyarrow.parquet as pq

# File paths
PROVIDER_PATH = "data/processed/ca_providers_filtered.csv"
TRAVEL_MATRIX_PATH = "data/processed/travel_matrix.parquet"
DEMAND_PATH = "data/processed/zip_demand.csv"


def main():
    print("Loading provider data...")
    providers = pd.read_csv(PROVIDER_PATH)
    print(f"Providers: {providers.shape}")
    print(providers.head())
    print("\n---\n")

    print("Loading travel matrix...")
    travel_matrix = pd.read_parquet(TRAVEL_MATRIX_PATH)
    print(f"Travel matrix: {travel_matrix.shape}")
    print(travel_matrix.head())
    print("\n---\n")

    print("Loading demand data...")
    demand = pd.read_csv(DEMAND_PATH)
    print(f"Demand: {demand.shape}")
    print(demand.head())
    print("\n---\n")

    # Calculate minimum travel time to any provider for each ZIP
    print("Calculating minimum travel time to any provider for each ZIP...")
    min_travel = travel_matrix.groupby("zip_code")["drive_minutes"].min().reset_index()
    min_travel = min_travel.rename(columns={"drive_minutes": "min_travel_minutes"})
    print(min_travel.head())
    print("\n---\n")

    # Ensure zip_code is string in both DataFrames
    min_travel["zip_code"] = min_travel["zip_code"].astype(str)
    demand["zip_code"] = demand["zip_code"].astype(str)

    # Flag ZIPs where min travel time > 6 minutes (UDI = 1) - Updated threshold for California data
    min_travel["UDI_flag"] = (min_travel["min_travel_minutes"] > 6).astype(int)

    # Merge with demand data for context
    udi_df = pd.merge(min_travel, demand, on="zip_code", how="left")
    print("UDI DataFrame sample:")
    print(udi_df.head())
    print("\n---\n")

    # Summary statistics
    num_udi = udi_df["UDI_flag"].sum()
    pct_udi = 100 * num_udi / len(udi_df)
    print(f"Number of ZIPs with UDI=1 (>30 min): {num_udi} / {len(udi_df)} ({pct_udi:.1f}%)")
    print("Min travel time stats:")
    print(udi_df["min_travel_minutes"].describe())

if __name__ == "__main__":
    main() 