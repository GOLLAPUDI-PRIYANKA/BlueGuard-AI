import pandas as pd


def clean_ais_data(ais_data):
    """
    Clean and normalize AIS data.

    Operations:
    1. Remove duplicate records
    2. Convert timestamps to UTC
    3. Remove invalid coordinates
    4. Sort records by vessel and timestamp
    """

    ais_data = ais_data.copy()

    # 1. Remove duplicate AIS records
    ais_data = ais_data.drop_duplicates()

    # 2. Normalize timestamps to UTC
    ais_data["timestamp"] = pd.to_datetime(
        ais_data["timestamp"],
        utc=True
    )

    # 3. Remove invalid latitude and longitude
    ais_data = ais_data[
        (ais_data["latitude"].between(-90, 90)) &
        (ais_data["longitude"].between(-180, 180))
    ]

    # 4. Sort by vessel and timestamp
    ais_data = ais_data.sort_values(
        by=["mmsi", "timestamp"]
    ).reset_index(drop=True)

    print("AIS data cleaned successfully.")
    print(f"Records after cleaning: {len(ais_data)}")

    return ais_data


if __name__ == "__main__":
    file_path = "ais-services/data/ais_sample.csv"

    ais_data = pd.read_csv(file_path)

    cleaned_data = clean_ais_data(ais_data)

    print("\nCleaned AIS data:")
    print(cleaned_data)
