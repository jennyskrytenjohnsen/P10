import vitaldb
import requests
import pandas as pd
import matplotlib.pyplot as plt
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
special_variables = ["Orchestra/NEPI_VOL"]  # Example; you can add more special variables

# Initialize a list to store saved track details
saved_tracks = []

def collect_track_last_value():
    # Load the tracklist data
    track_list_url = "https://api.vitaldb.net/trks"
    df_tracklist = pd.read_csv(track_list_url)

    # Iterate through each row in the tracklist
    for index, row in df_tracklist.iterrows():
        if row['tname'] in special_variables: 
            trackidentifier = row["tid"]
            trackdata_url = f"https://api.vitaldb.net/{trackidentifier}"
            
            # Handle API error
            try:
                response = requests.get(trackdata_url, timeout=10)
                response.raise_for_status()
            except requests.exceptions.Timeout:
                print(f"Timeout error: Cannot get {row['tname']} ({trackdata_url})")
                continue  # Skip to next track

            try:
                # Convert API response into a pandas DataFrame
                trackdata = pd.read_csv(io.StringIO(response.text))
                if trackdata.empty:
                    continue
            except:
                continue  # Skip if there is an issue reading the track data

            # Get the last recorded value from the 'Orchestra/NEPI_VOL' column
            last_value = trackdata["Orchestra/NEPI_VOL"].iloc[-1]

            # Print the caseid and the last value of the track
            print(f"Case ID: {row['caseid']}, Last Value: {last_value}")

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

