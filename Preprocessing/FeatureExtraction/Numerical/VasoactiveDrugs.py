## VASOACTIVE DRUGS

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
        value_ino = 0  # Default to 0 for value_ino

        # Get the value of intraop_eph from the clinical dataset
        intraop_eph = row["intraop_eph"]
        if pd.notna(intraop_eph) and intraop_eph != 0:
            value_eph = 1

        # Get the value of intraop_phe from the clinical dataset
        intraop_phe = row["intraop_phe"]
        if pd.notna(intraop_phe) and intraop_phe != 0:
            value_phe = 1

        # Variables to track if the last value is non-zero
        non_zero_count_ino = 0

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

                # For value_ino, track only NEPI_VOL, EPI_VOL, and DOPA_VOL
                if var in ["Orchestra/NEPI_VOL", "Orchestra/EPI_VOL", "Orchestra/DOPA_VOL"]:
                    if last_value != 0:
                        non_zero_count_ino += 1

        # Set value_ino to 1 if exactly one of the three variables had a non-zero value
        if non_zero_count_ino == 1:
            value_ino = 1

        # Append the results for the current caseid
        results.append({
            "caseid": caseid,
            "value_eph": value_eph,
            "value_phe": value_phe,
            "value_vaso": value_vaso,
            "value_ino": value_ino
        })

    # Save the results to a CSV file in the 'Data' folder /home/user/maria_ws/P10/Preprocessing/Data C:/Users/mariah/Documents/GitHub/P10/Preprocessing/Data
    output_file = "/home/user/maria_ws/P10/Preprocessing/Data/Data_vasoactivedrugs.csv"
    df_results = pd.DataFrame(results)
    df_results.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")

# Run the function
collect_track_last_value()

#### PLOTTE KODE ####

# import requests
# import pandas as pd
# import io
# import matplotlib.pyplot as plt

# # List of special variables you're interested in (update as necessary)
# special_variables = ["Orchestra/NEPI_VOL"]

# # Load the tracklist data
# track_list_url = "https://api.vitaldb.net/trks"
# df_tracklist = pd.read_csv(track_list_url)

# # Get the first caseid from the dataframe
# first_caseid = 17

# # Iterate through the tracklist to find the track for the first caseid
# for index, row in df_tracklist.iterrows():
#     if row['tname'] in special_variables and row["caseid"] == first_caseid:
#         trackidentifier = row["tid"]
#         trackdata_url = f"https://api.vitaldb.net/{trackidentifier}"
        
#         # Handle API error
#         try:
#             response = requests.get(trackdata_url, timeout=10)
#             response.raise_for_status()
#         except requests.exceptions.Timeout:
#             print(f"Timeout error: Cannot get {row['tname']} ({trackdata_url})")
#             continue  # Skip to next track

#         try:
#             # Convert API response into a pandas DataFrame
#             trackdata = pd.read_csv(io.StringIO(response.text))
#             if trackdata.empty:
#                 print(f"Track data for track {row['tname']} is empty.")
#                 continue
#         except Exception as e:
#             print(f"Error reading track data for track {row['tname']}: {e}")
#             continue  # Skip if there is an issue reading the track data

#         # Debugging: Check the first few rows of the data
#         print(f"First few rows of track data for caseid {first_caseid}:")
#         print(trackdata.head())

#         # Check if 'Time' and 'Orchestra/NEPI_VOL' columns exist
#         if 'Time' not in trackdata.columns or 'Orchestra/NEPI_VOL' not in trackdata.columns:
#             print(f"Columns 'Time' and/or 'Orchestra/NEPI_VOL' not found in track data.")
#             continue

#         # Extract 'Time' and 'Orchestra/NEPI_VOL' columns
#         time_data = trackdata["Time"]
#         track_values = trackdata["Orchestra/NEPI_VOL"]

#         # Check if the columns have valid data
#         if time_data.empty or track_values.empty:
#             print(f"Empty data for 'Time' or 'Orchestra/NEPI_VOL' in track data for caseid {first_caseid}.")
#             continue

#         # Plot the data
#         plt.figure(figsize=(10, 6))
#         plt.plot(time_data, track_values, label='Orchestra/NEPI_VOL', color='b')
#         plt.xlabel("Time")
#         plt.ylabel("Orchestra/NEPI_VOL Value")
#         plt.title(f"Track Values Over Time for Case ID: {first_caseid}")
#         plt.xticks(rotation=45)
#         plt.grid(True)
#         plt.legend()
#         plt.tight_layout()
#         plt.show()

#         break  # We only need the first caseid, so break the loop after plotting
