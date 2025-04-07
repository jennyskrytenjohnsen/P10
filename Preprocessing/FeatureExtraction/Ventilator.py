import pandas as pd
import requests
import io
import numpy as np
import os

# Track identifiers for heart rate and ventilation parameters
RR_track = {'Solar8000/RR_CO2'}
ventilator_tracks = {
    'Solar8000/VENT_COMPL', 'Solar8000/VENT_INSP_TM', 'Solar8000/VENT_MAWP',
    'Solar8000/VENT_MEAS_PEEP', 'Solar8000/VENT_MV', 'Solar8000/VENT_PIP',
    'Solar8000/VENT_PPLAT', 'Solar8000/VENT_RR', 'Solar8000/VENT_SET_FIO2',
    'Solar8000/VENT_SET_PCP', 'Solar8000/VENT_SET_TV', 'Solar8000/VENT_TV',
    'Primus/VENT_LEAK'
}

# Load track list
df_tracklist = pd.read_csv("https://api.vitaldb.net/trks")

# Load clinical data
df_clinical = pd.read_csv("https://api.vitaldb.net/cases")

# Load signal percentage data
data_signal = pd.read_csv("Preprocessing/MissingValues/saved_tracks_numerical_MC_below100trialtest2.csv")

# Prepare a list to store results
results = []

# Iterate over each case
for caseid in df_clinical['caseid'].unique():
    # Filter tracks for the current case
    case_tracks = df_tracklist[df_tracklist['caseid'] == caseid]
    
    # Find relevant track IDs
    track_ids = case_tracks[case_tracks['tname'].isin(RR_track | ventilator_tracks)]
    
    if track_ids.empty:
        continue
    
    mean_rr = np.nan
    ventilator_flag = 0  # Default to 0
    
    for _, track in track_ids.iterrows():
        trackid, tname = track['tid'], track['tname']
        
        # Extract numerical track data from API
        trackdata_url = f"https://api.vitaldb.net/{trackid}"
        response = requests.get(trackdata_url)
        
        if response.status_code == 200:
            trackdata = pd.read_csv(io.StringIO(response.text))
            
            if tname in RR_track and tname in trackdata.columns:
                mean_rr = trackdata[tname].mean() if not trackdata.empty else np.nan
                
            if tname in ventilator_tracks and tname in trackdata.columns:
                if (trackdata[tname] != 0).any():
                    ventilator_flag = 1  # Set to 1 if any value is nonzero
        
    # Check signal percentage
    signal_info = data_signal[data_signal['caseid'] == caseid]
    if not signal_info.empty and signal_info.iloc[0]['precentage_of_signal_is_there'] > 75:
        results.append({
            'caseid': caseid,
            'Avg_RR': mean_rr,
            'Ventilator_Flag': ventilator_flag
        })

# Create DataFrame and save to CSV
output_dir = "Preprocessing/Data"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "Data_ventilator.csv")
df_results = pd.DataFrame(results)
df_results.to_csv(output_path, index=False)

print(f'Data saved to {output_path}')
