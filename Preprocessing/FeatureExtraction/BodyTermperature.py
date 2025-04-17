import pandas as pd
import requests
import io
import numpy as np
import os
import matplotlib.pyplot as plt

# Track identifier for heart rate
body_temperature = {'Solar8000/BT'}

# Load track list
track_list_url = "https://api.vitaldb.net/trks"
df_tracklist = pd.read_csv(track_list_url)

# Load clinical data
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)


# Prepare a list to store results
results = []

# Iterate over each row in the DataFrame
for index, row in df_tracklist.iterrows():
    if row['tname'] in body_temperature:  # Check if track name is in our target list
        hypothermia=0
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
                trackdata_filtered.loc[trackdata_filtered['Solar8000/BT'] < 34, 'Solar8000/BT'] = np.nan

                #length_trackdatafiltered = len(trackdata_filtered)
                median_filtered = trackdata_filtered.rolling(window=3, center=True).median()

                #plt.plot(median_filtered, marker='o', linestyle='-')
                
                #plt.ylim(20,40)
                #plt.show()
                
                if 'Solar8000/BT' in median_filtered.columns and not median_filtered.empty:
                    #median_filtered_track=median_filtered[:,1]
                    mean_BT = median_filtered['Solar8000/BT'].mean()
                    print('mean_BT', mean_BT)

                    for value in median_filtered['Solar8000/BT']:
                        if value < 36:
                            hypothermia  = hypothermia+1
                    precentage_hypothermia = (hypothermia/len(trackdata_filtered))*100
                    print("precentage_hypothermia", precentage_hypothermia)    
                    
                    average_first_15_min = median_filtered['Solar8000/BT'][:900].mean()
                    average_last_15_min = median_filtered['Solar8000/BT'][-900:].mean()
                    difference_BT = average_first_15_min-average_last_15_min
                    print("difference_BT", difference_BT)

                    results.append([mean_BT,precentage_hypothermia, difference_BT])

                else:
                    mean_val = "No Data"
            else:
                mean_val = "No Data"                

# Create DataFrame and save to CSV
output_dir = "Preprocessing/Data"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "Data_BT.csv")
df_results = pd.DataFrame(results)
df_results.to_csv(output_path, index=False)

print(f'Data saved to {output_path}')
