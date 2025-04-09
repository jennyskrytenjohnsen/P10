import pandas as pd
import requests
import io
import numpy as np
import os

# Track identifier for heart rate
PEEP_track = {'Primus/PEEP_MBAR'}

# Load track list
track_list_url = "https://api.vitaldb.net/trks"
df_tracklist = pd.read_csv(track_list_url)

# Load clinical data
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Load the CSV file containing signal percentage information
data_signal = pd.read_csv("Preprocessing/MissingValues/saved_tracks_numerical_MC_below100trialtest2.csv")

# Filter for only Primus/PEEP_MBAR track data
data_signal = data_signal[data_signal["tname"] == "Primus/PEEP_MBAR"]

# Prepare a list to store results
results = []

# Iterate over each row in the DataFrame
for index, row in df_tracklist.iterrows():
    if row['tname'] in PEEP_track:  # Check if track name is in our target list
        trackid = row['tid']  # Track ID
        caseid = row['caseid']  # Case ID
        print(f'Processing CaseID: {caseid}, TrackName: {row["tname"]}')
        
        # Extract numerical track data from API
        trackdata_url = f"https://api.vitaldb.net/{trackid}"
        response = requests.get(trackdata_url)
        
        if response.status_code == 200:
            trackdata = pd.read_csv(io.StringIO(response.text))
            
            # Get opstart and opend times for the case
            case_info = df_clinical[df_clinical['caseid'] == caseid]
            if not case_info.empty:
                opstart = case_info.iloc[0]['opstart']
                opend = case_info.iloc[0]['opend']
                
                # Filter data to only include values between opstart and opend
                trackdata_filtered = trackdata[(trackdata['Time'] >= opstart) & (trackdata['Time'] <= opend)]
                
                if 'Primus/PEEP_MBAR' in trackdata_filtered.columns and not trackdata_filtered.empty:
                    mean_val = trackdata_filtered['Primus/PEEP_MBAR'].mean()
                else:
                    mean_val = "No Data"
            else:
                mean_val = "No Data"
            
            # Check if the signal percentage for the caseid is more than 75
            signal_info = data_signal[data_signal['caseid'] == caseid]
            if not signal_info.empty and signal_info.iloc[0]['precentage_of_signal_is_there'] > 75:
                print(f'Average PEEP for CaseID {caseid}: {mean_val}')
                results.append({'caseid': caseid, 'AvgPEEP': mean_val})
            else:
                print(f'Skipping CaseID {caseid} due to signal percentage <= 75')
        else:
            print(f'Failed to retrieve data for CaseID {caseid}')

# Create DataFrame and save to CSV
output_dir = "Preprocessing/Data"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "Data_AvgPEEP.csv")
df_results = pd.DataFrame(results)
df_results.to_csv(output_path, index=False)

print(f'Data saved to {output_path}')
