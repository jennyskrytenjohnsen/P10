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
                
                # Define time ranges
                first_15_min = (trackdata['Time'] >= opstart) & (trackdata['Time'] <= opstart + 900)
                last_15_min = (trackdata['Time'] >= opend - 900) & (trackdata['Time'] <= opend)
                
                # Filter data to only include the first and last 15 minutes
                trackdata_first = trackdata[first_15_min]
                trackdata_last = trackdata[last_15_min]
                
                # Calculate means
                if 'Primus/PEEP_MBAR' in trackdata.columns:
                    mean_first = trackdata_first['Primus/PEEP_MBAR'].mean() if not trackdata_first.empty else np.nan
                    mean_last = trackdata_last['Primus/PEEP_MBAR'].mean() if not trackdata_last.empty else np.nan
                else:
                    mean_first, mean_last = np.nan, np.nan
                
                # Compute the difference
                peep_difference = mean_last - mean_first if not np.isnan(mean_first) and not np.isnan(mean_last) else np.nan
            else:
                peep_difference = np.nan
            
            # Check if the signal percentage for the caseid is more than 75
            signal_info = data_signal[data_signal['caseid'] == caseid]
            if not signal_info.empty and signal_info.iloc[0]['precentage_of_signal_is_there'] > 75:
                print(f'PEEP Difference for CaseID {caseid}: {peep_difference}')
                results.append({'caseid': caseid, 'PEEP_Diff': peep_difference})
            else:
                print(f'Skipping CaseID {caseid} due to signal percentage <= 75')
        else:
            print(f'Failed to retrieve data for CaseID {caseid}')

# Create DataFrame and save to CSV
output_dir = "Preprocessing/Data"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "Data_avgPEEPdiff.csv")
df_results = pd.DataFrame(results)
df_results.to_csv(output_path, index=False)

print(f'Data saved to {output_path}')
