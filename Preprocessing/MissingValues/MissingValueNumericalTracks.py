import vitaldb
import pandas as pd
import requests
import json
import io
import time  # Importer time-modulet
import numpy as np

# track identifier (den konkrete patients konktere måling)
track_list_url = "https://api.vitaldb.net/trks"
df_tracklist = pd.read_csv(track_list_url) #Skriv tracklist_url inne i parantesen

special_variables = {'Solar8000/PLETH_HR'}

save_numerical_tracks = []

def count_missing_vaules_in_numeric_tracks():
    for index, row in df_tracklist.iterrows():
        if row['tname'] in special_variables:
            trackid= row['tid']
            caseid = row['caseid']
            print('Caseid', caseid, 'TrackName:', row['tname'])
            trackdata_url = f"https://api.vitaldb.net/{trackid}"

            response = requests.get(trackdata_url)
            trackdata = pd.read_csv(io.StringIO(response.text))
        
            time_before_start = trackdata.iloc[0,0]

            min_gap = trackdata.iloc[:20]['Time'].diff().min()
            min_gap = round(min_gap, 0)
            print('Min Gap:', min_gap)

            sampled_times = trackdata['Time'].diff()

            total_length_of_singal = len(trackdata['Time'])

            res = sum(x > min_gap for x in sampled_times[1:])
            print(res)

            if res > 0.2*total_length_of_singal:
                print('No, this signal has length', total_length_of_singal, 'and there are missing', res, 'values')
            
            else:
                print('Yes, this signal has length', total_length_of_singal, 'and are missing', res, 'values')
                save_numerical_tracks.append([row['caseid'], row['tname'], row['tid'], res, total_length_of_singal, min_gap])

    # Konverter listen til en DataFrame og lagre som CSV
    if save_numerical_tracks:
        df_saved_tracks = pd.DataFrame(save_numerical_tracks, columns=["caseid", "tname", "tid", "res","total_length_of_singal", "min_gap"])
        df_saved_tracks.to_csv("saved_tracks_numerical.csv", index=False)
        print("CSV file 'saved_tracks.csv' has been saved.")
    else:
        print("No tracks met the criteria for saving.")

    
count_missing_vaules_in_numeric_tracks()
