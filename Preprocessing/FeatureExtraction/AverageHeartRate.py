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

# Prepare a list to store results
results = []

# Iterate over each row in the DataFrame
for index, row in df_tracklist.iterrows():
    if row['tname'] in HR_track:  # Check if track name is in our target list
        trackid = row['tid']  # Track ID
        caseid = row['caseid']  # Case ID
        print(f'Processing CaseID: {caseid}, TrackName: {row["tname"]}')
        
        # Extract numerical track data from API
        trackdata_url = f"https://api.vitaldb.net/{trackid}"
        response = requests.get(trackdata_url)
        
        if response.status_code == 200:
            trackdata = pd.read_csv(io.StringIO(response.text))
            if 'Solar8000/HR' in trackdata.columns:
                mean_val = trackdata['Solar8000/HR'].mean()
                print(f'Average HR for CaseID {caseid}: {mean_val}')
                results.append({'caseid': caseid, 'AvgHR': mean_val})
            else:
                print(f'Column "Solar8000/HR" not found in CaseID {caseid}')
        else:
            print(f'Failed to retrieve data for CaseID {caseid}')

# Create DataFrame and save to CSV
output_dir = "Preprocessing/FeatureExtraction"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "Data_AvgHR.csv")
df_results = pd.DataFrame(results)
df_results.to_csv(output_path, index=False)

print(f'Data saved to {output_path}')
