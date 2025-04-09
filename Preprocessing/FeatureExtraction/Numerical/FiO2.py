import pandas as pd
import requests
import io
import numpy as np
import os

# Track identifier for FiO2
target_track = 'Primus/FIO2'

# Load track list
track_list_url = "https://api.vitaldb.net/trks"
df_tracklist = pd.read_csv(track_list_url)

# Load clinical data
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Load signal percentage info
data_signal = pd.read_csv("Preprocessing/MissingValues/saved_tracks_numerical_MC_below100trialtest2.csv")
data_signal = data_signal[data_signal["tname"] == target_track]

# Prepare list to store results
results = []

# Iterate over track list
for index, row in df_tracklist.iterrows():
    if row['tname'] == target_track:
        trackid = row['tid']
        caseid = row['caseid']
        print(f'Processing CaseID: {caseid}')

        # Get signal percentage for this caseid
        signal_info = data_signal[data_signal['caseid'] == caseid]
        if signal_info.empty or signal_info.iloc[0]['precentage_of_signal_is_there'] <= 75:
            print(f'Skipping CaseID {caseid} due to signal percentage <= 75')
            continue

        # Download track data
        trackdata_url = f"https://api.vitaldb.net/{trackid}"
        response = requests.get(trackdata_url)

        if response.status_code == 200:
            trackdata = pd.read_csv(io.StringIO(response.text))

            # Get surgery end time
            case_info = df_clinical[df_clinical['caseid'] == caseid]
            if not case_info.empty:
                opend = case_info.iloc[0]['opend']

                # Filter for last 15 minutes
                last_15_min = (trackdata['Time'] >= opend - 900) & (trackdata['Time'] <= opend)
                trackdata_last = trackdata[last_15_min]

                # Calculate mean FiO2
                if target_track in trackdata.columns and not trackdata_last.empty:
                    mean_FiO2 = trackdata_last[target_track].mean()
                else:
                    mean_FiO2 = np.nan

                print(f'Average FiO2 for CaseID {caseid}: {mean_FiO2}')
                results.append({'caseid': caseid, 'data_FiO2': mean_FiO2})
            else:
                print(f'No clinical info for CaseID {caseid}')
        else:
            print(f'Failed to retrieve data for CaseID {caseid}')

# Save results
output_dir = "Preprocessing/Data"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "Data_FiO2.csv")
df_results = pd.DataFrame(results)
df_results.to_csv(output_path, index=False)

print(f'Results saved to {output_path}')
