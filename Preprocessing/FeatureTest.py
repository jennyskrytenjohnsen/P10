import vitaldb  
import requests
import pandas as pd
import io

# Load clinical dataset from the VitalDB API
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Extract 'intraop_eph' and 'intraop_phe' columns and count missing values
missing_eph = df_clinical["intraop_eph"].isna().sum()
missing_phe = df_clinical["intraop_phe"].isna().sum()
print(f"Missing values in 'intraop_eph': {missing_eph}")
print(f"Missing values in 'intraop_phe': {missing_phe}")

# Load tracklist data from the VitalDB API
track_list_url = "https://api.vitaldb.net/trks"
df_tracklist = pd.read_csv(track_list_url)

# List of special variables you're interested in (update as necessary)
special_variables = ["Orchestra/NEPI_VOL"]  # Example; you can add more special variables

# Initialize a list to store the results for each caseid
results = []

def collect_track_last_value():
    # Load the tracklist data
    track_list_url = "https://api.vitaldb.net/trks"
    df_tracklist = pd.read_csv(track_list_url)

    # Iterate through each row in the clinical data to ensure all caseids are included
    for index, row in df_clinical.iterrows():
        caseid = row["caseid"]

        # Initialize value_vaso to 0 (default)
        value_vaso = 0

        # Check if 'Orchestra/NEPI_VOL' data is available for this caseid
        track_found = df_tracklist[df_tracklist['caseid'] == caseid]
        
        if not track_found.empty:
            for _, track_row in track_found.iterrows():
                if track_row['tname'] in special_variables:
                    trackidentifier = track_row["tid"]
                    trackdata_url = f"https://api.vitaldb.net/{trackidentifier}"

                    try:
                        response = requests.get(trackdata_url, timeout=10)
                        response.raise_for_status()
                    except requests.exceptions.Timeout:
                        print(f"Timeout error: Cannot get {track_row['tname']} ({trackdata_url})")
                        continue  # Skip to next track

                    try:
                        # Convert API response into a pandas DataFrame
                        trackdata = pd.read_csv(io.StringIO(response.text))
                        if trackdata.empty:
                            continue
                    except:
                        continue  # Skip if there is an issue reading the track data

                    # Check if the 'Orchestra/NEPI_VOL' column exists and has values
                    if "Orchestra/NEPI_VOL" in trackdata.columns and not trackdata["Orchestra/NEPI_VOL"].isna().all():
                        # Get the last recorded value from the 'Orchestra/NEPI_VOL' column
                        last_value_vaso = trackdata["Orchestra/NEPI_VOL"].iloc[-1]
                        # Determine the value to store (1 if not 0, 0 if 0)
                        value_vaso = 1 if last_value_vaso != 0 else 0
                    else:
                        value_vaso = 0  # No data for 'Orchestra/NEPI_VOL'
        
        # Get the value of intraop_eph from the clinical dataset by matching the caseid
        intraop_eph = row.get("intraop_eph", pd.NA)

        # If intraop_eph is found, transform it; otherwise, set to 0
        value_eph = 1 if (intraop_eph != 0 and pd.notna(intraop_eph)) else 0

        # Get the value of intraop_phe from the clinical dataset by matching the caseid
        intraop_phe = row.get("intraop_phe", pd.NA)

        # If intraop_phe is found, transform it; otherwise, set to 0
        value_phe = 1 if (intraop_phe != 0 and pd.notna(intraop_phe)) else 0

        # Append the caseid, value_eph, value_phe, and value_vaso to the results list
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
