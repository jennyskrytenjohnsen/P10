import pandas as pd
import matplotlib.pyplot as plt
import requests
import io
import numpy as np

df = pd.read_csv('C:/Users/johns/Documents/10semester/Kode/VitalDB_Tracks.csv')


mean_signal = []
std_signal = []
empty_signal = []
number_of_signals = []


special_variable = {'Solar8000/PLETH_HR'}

for index, row in df.iterrows():
    if row['tname'] in special_variable:
        trackidentifier = row["tid"]
        trackdata_url = f"https://api.vitaldb.net/{trackidentifier}"
            
        try: 
            response = requests.get(trackdata_url, timeout = 10)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            print(f"Timeout-error: Can not get {row['tname']} ({trackdata_url})")
            continue # Go to next signal

        try:
        # Konverter API-respons til en pandas DataFrame
            trackdata = pd.read_csv(io.StringIO(response.text)) 
        except Exception as e: 
            continue
        
        if trackdata.empty:
            empty_signal =+ 1
            continue
        else:
            number_of_signals =+1

        placeholder_mean = np.mean(trackdata, axis=0)
        mean_signal = placeholder_mean
        print(mean_signal)
        placeholder_std = np.std(trackdata, axis=0)
        std_signal = std_signal
        print(std_signal)
    
plt.plot(number_of_signals,mean_signal)
plt.plot(number_of_signals,std_signal)

plt.show()
    
    
