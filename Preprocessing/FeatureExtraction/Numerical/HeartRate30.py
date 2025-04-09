import pandas as pd
import requests
import io
import numpy as np
import os

# Track identifier for heart rate
HR_track = {'Solar8000/HR'}

# Load track list
track_list_url = "https://api.vitaldb.net/trks"
df_tracklist = pd.read_csv(track_list_url)

# Load clinical data
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Load the CSV file containing signal percentage information
data_signal = pd.read_csv("Preprocessing/MissingValues/saved_tracks_numerical_MC_below100trialtest2.csv")

# Filter for only Solar8000/HR track data
data_signal = data_signal[data_signal["tname"] == "Solar8000/HR"]

# Prepare a list to store results
results = []

# Iterate over each row in the DataFrame
for index, row in df_tracklist.iterrows():
    if row['tname'] in HR_track:
        trackid = row['tid']
        caseid = row['caseid']
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
                
                # Filter data between opstart and opend
                trackdata_filtered = trackdata[(trackdata['Time'] >= opstart) & (trackdata['Time'] <= opend)]
                
                if 'Solar8000/HR' in trackdata_filtered.columns and not trackdata_filtered.empty:
                    total_seconds = len(trackdata_filtered)
                    
                    # Count seconds where HR is below certain thresholds
                    seconds_below_30 = (trackdata_filtered['Solar8000/HR'] < 30).sum()
                    seconds_below_60 = (trackdata_filtered['Solar8000/HR'] < 60).sum()
                    seconds_above_100 = (trackdata_filtered['Solar8000/HR'] > 100).sum()
                    
                    # Calculate percentage for each category
                    if total_seconds > 0:
                        percent_below_30 = (seconds_below_30 / total_seconds) * 100
                        percent_below_60 = (seconds_below_60 / total_seconds) * 100
                        percent_above_100 = (seconds_above_100 / total_seconds) * 100
                    else:
                        percent_below_30 = percent_below_60 = percent_above_100 = "No Data"
                else:
                    percent_below_30 = percent_below_60 = percent_above_100 = "No Data"
            else:
                percent_below_30 = percent_below_60 = percent_above_100 = "No Data"
            
            # Check signal quality
            signal_info = data_signal[data_signal['caseid'] == caseid]
            if not signal_info.empty and signal_info.iloc[0]['precentage_of_signal_is_there'] > 75:
                print(f'HR <30 % for CaseID {caseid}: {percent_below_30}')
                print(f'HR <60 % for CaseID {caseid}: {percent_below_60}')
                print(f'HR >100 % for CaseID {caseid}: {percent_above_100}')
                
                # Append results to list
                results.append({
                    'caseid': caseid,
                    'HR_below_30_percent': percent_below_30,
                    'HR_below_60_percent': percent_below_60,
                    'HR_above_100_percent': percent_above_100
                })
            else:
                print(f'Skipping CaseID {caseid} due to signal percentage <= 75')
        else:
            print(f'Failed to retrieve data for CaseID {caseid}')

# Save results to CSV
output_dir = "Preprocessing/FeatureExtraction"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "Data_HRcount.csv")
df_results = pd.DataFrame(results)
df_results.to_csv(output_path, index=False)

print(f'Data saved to {output_path}')
