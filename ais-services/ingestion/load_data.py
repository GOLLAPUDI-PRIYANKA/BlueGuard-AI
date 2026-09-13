import pandas as pd


def load_ais_data(file_path):
    """
    Load AIS data from a CSV file.

    Expected AIS fields:
    mmsi, imo_number, latitude, longitude,
    timestamp, speed, course, vessel_type
    """

    ais_data = pd.read_csv(file_path)

    print("AIS data loaded successfully.")
    print(f"Total AIS records: {len(ais_data)}")

    print("\nColumns:")
    print(list(ais_data.columns))

    print("\nFirst 5 records:")
    print(ais_data.head())

    return ais_data


if __name__ == "__main__":
    file_path = "ais-services/data/ais_sample.csv"

    ais_data = load_ais_data(file_path)
