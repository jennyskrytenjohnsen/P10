import pandas as pd
import requests
import io
import numpy as np
import os

# Track identifier for heart rate
RR_track = {'Solar8000/RR_CO2'}

# Load track list
track_list_url = "https://api.vitaldb.net/trks"
df_tracklist = pd.read_csv(track_list_url)

# Load clinical data
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Load the CSV file containing signal percentage information
data_signal = pd.read_csv("Preprocessing/MissingValues/saved_tracks_numerical_MC_below100trialtest2.csv")

# Prepare a list to store results
results = []

# Iterate over each row in the DataFrame
for index, row in df_tracklist.iterrows():
    if row['tname'] in RR_track:  # Check if track name is in our target list
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
                opend = case_info.iloc[0]['opend']
                
                # Define time range for 15 minutes before opend
                last_15_min = (trackdata['Time'] >= opend - 900) & (trackdata['Time'] <= opend)
                
                # Filter data for the last 15 minutes
                trackdata_last = trackdata[last_15_min]
                
                # Calculate mean RR
                if 'Solar8000/RR_CO2' in trackdata.columns:
                    mean_rr_last_15min = trackdata_last['Solar8000/RR_CO2'].mean() if not trackdata_last.empty else np.nan
                else:
                    mean_rr_last_15min = np.nan
            else:
                mean_rr_last_15min = np.nan
            
            # Check if the signal percentage for the caseid is more than 75
            signal_info = data_signal[data_signal['caseid'] == caseid]
            if not signal_info.empty and signal_info.iloc[0]['precentage_of_signal_is_there'] > 75:
                print(f'Average RR for last 15 min before opend for CaseID {caseid}: {mean_rr_last_15min}')
                results.append({'caseid': caseid, 'Avg_RR_Last_15min': mean_rr_last_15min})
            else:
                print(f'Skipping CaseID {caseid} due to signal percentage <= 75')
        else:
            print(f'Failed to retrieve data for CaseID {caseid}')

# Create DataFrame and save to CSV
output_dir = "Preprocessing/Data"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "Data_avgRR_last15min.csv")
df_results = pd.DataFrame(results)
df_results.to_csv(output_path, index=False)

print(f'Data saved to {output_path}')
