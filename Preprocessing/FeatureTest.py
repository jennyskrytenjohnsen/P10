import vitaldb  
import requests
import pandas as pd
import io

# Load clinical dataset from the VitalDB API
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Extract 'intraop_eph' column and count missing values
missing_eph = df_clinical["intraop_eph"].isna().sum()
print(f"Missing values in 'intraop_eph': {missing_eph}")

# Extract 'intraop_phe' column and count missing values
missing_phe = df_clinical["intraop_phe"].isna().sum()
print(f"Missing values in 'intraop_phe': {missing_phe}")

# Load tracklist data from the VitalDB API
track_list_url = "https://api.vitaldb.net/trks"
df_tracklist = pd.read_csv(track_list_url)

# List of special variables you're interested in (update as necessary)
special_variables = [
    "Orchestra/NEPI_VOL",
    "Orchestra/EPI_VOL",
    "Orchestra/PHEN_VOL",
    "Orchestra/VASO_VOL",
    "Orchestra/DOPA_VOL",
    "Orchestra/DOBU_VOL",
    "Orchestra/MRN_VOL"
]

# Initialize a list to store the results for each caseid
results = []

def collect_track_last_value():
    # Iterate over each caseid in the clinical dataset
    for index, row in df_clinical.iterrows():
        caseid = row["caseid"]

        # Initialize the values for the current caseid
        value_vaso = 0  # Default to 0 for value_vaso
        value_eph = 0  # Default to 0 for value_eph
        value_phe = 0  # Default to 0 for value_phe

        # Get the value of intraop_eph from the clinical dataset
        intraop_eph = row["intraop_eph"]
        if pd.notna(intraop_eph) and intraop_eph != 0:
            value_eph = 1

        # Get the value of intraop_phe from the clinical dataset
        intraop_phe = row["intraop_phe"]
        if pd.notna(intraop_phe) and intraop_phe != 0:
            value_phe = 1

        # Iterate over the special variables and check if any have non-zero values for the current caseid
        for var in special_variables:
            track_row = df_tracklist[df_tracklist['tname'] == var]
            if not track_row.empty:
                trackidentifier = track_row.iloc[0]["tid"]
                trackdata_url = f"https://api.vitaldb.net/{trackidentifier}"

                # Handle API error
                try:
                    response = requests.get(trackdata_url, timeout=10)
                    response.raise_for_status()
                except requests.exceptions.Timeout:
                    print(f"Timeout error: Cannot get {var} ({trackdata_url})")
                    continue  # Skip to next track

                try:
                    # Convert API response into a pandas DataFrame
                    trackdata = pd.read_csv(io.StringIO(response.text))
                    if trackdata.empty:
                        continue
                except:
                    continue  # Skip if there is an issue reading the track data

                # Get the last value of the track data
                last_value = trackdata[var].iloc[-1] if var in trackdata.columns else 0

                # Set value_vaso to 1 if the last value is non-zero
                if last_value != 0:
                    value_vaso = 1
                    break  # Once we find a non-zero value, we don't need to check further

        # Append the results for the current caseid
        results.append({
            "caseid": caseid,
            "value_eph": value_eph,
            "value_phe": value_phe,
            "value_vaso": value_vaso
        })

    # Save the results to a CSV file in the 'Data' folder
    output_file = "C:/Users/mariah/Documents/GitHub/P10/Preprocessing/Data/Data_vasoactivedrugs.csv"
    df_results = pd.DataFrame(results)
    df_results.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")

# Run the function
collect_track_last_value()
