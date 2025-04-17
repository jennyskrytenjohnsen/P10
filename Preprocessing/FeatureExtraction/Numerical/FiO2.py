import pandas as pd
import requests
import io
import numpy as np
import os
import multiprocessing
from scipy.signal import medfilt

# Track identifier for FiO2
target_track = 'Primus/FIO2'

# Load track list
track_list_url = "https://api.vitaldb.net/trks"
df_tracklist = pd.read_csv(track_list_url)

# Load clinical data
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Load signal percentage info
data_signal = pd.read_csv("Preprocessing/MissingValues/saved_tracks_numerical_MC_total_15min.csv")
data_signal = data_signal[data_signal["tname"] == target_track]

# Prepare list to store results
def worker(subset):
    subset = subset.reset_index(drop=True)
    local_results = []

    for index, row in subset.iterrows():
        if row['tname'] == target_track:
            trackid = row['tid']
            caseid = row['caseid']
            print(f'Processing CaseID: {caseid}')

            # Get signal percentage for this caseid
            signal_info = data_signal[data_signal['caseid'] == caseid]
            if signal_info.empty:
                print(f'Skipping CaseID {caseid}: no signal info')
                continue

            signal_total = signal_info.iloc[0]['precentage_of_signal_is_there_total']
            signal_15min = signal_info.iloc[0]['precentage_of_signal_is_there_15min']

            # Download track data
            trackdata_url = f"https://api.vitaldb.net/{trackid}"
            response = requests.get(trackdata_url)

            if response.status_code == 200:
                trackdata = pd.read_csv(io.StringIO(response.text))

                if target_track not in trackdata.columns or trackdata.empty:
                    print(f'Missing or empty FiO2 data for CaseID {caseid}')
                    continue

                # Apply median filter (kernel size must be odd and >1)
                try:
                    trackdata[target_track] = medfilt(trackdata[target_track], kernel_size=5)
                except Exception as e:
                    print(f"Median filtering failed for CaseID {caseid}: {e}")
                    continue

                # Get surgery end time
                case_info = df_clinical[df_clinical['caseid'] == caseid]
                if not case_info.empty:
                    opend = case_info.iloc[0]['opend']

                    # Average over entire operation
                    if signal_total > 75:
                        mean_FiO2_total = trackdata[target_track].mean()
                    else:
                        mean_FiO2_total = np.nan

                    # Average over last 15 minutes
                    last_15_min = (trackdata['Time'] >= opend - 900) & (trackdata['Time'] <= opend)
                    trackdata_last = trackdata[last_15_min]

                    if signal_15min > 75 and not trackdata_last.empty:
                        mean_FiO2_15min = trackdata_last[target_track].mean()
                    else:
                        mean_FiO2_15min = np.nan
                    
                    # Ensure FiO2_w15minMV is always recorded
                    if not trackdata_last.empty:
                        FiO2_w15minMV = trackdata_last[target_track].tolist()
                    else:
                        FiO2_w15minMV = np.nan

                    print(f'CaseID {caseid} - Mean FiO2 Total: {mean_FiO2_total}, Last 15min: {mean_FiO2_15min}')
                    local_results.append({
                        'caseid': caseid,
                        'FiO2_total': mean_FiO2_total, 
                        'FiO2_15min': mean_FiO2_15min, 
                        'FiO2_w15minMV': FiO2_w15minMV
                    })
                else:
                    print(f'No clinical info for CaseID {caseid}')
            else:
                print(f'Failed to retrieve data for CaseID {caseid}')

    return local_results

def parallel_for_loop(df, num_workers=None):
    if num_workers is None:
        num_workers = multiprocessing.cpu_count()

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input data must be a DataFrame.")

    chunks = np.array_split(df, num_workers)
    with multiprocessing.Pool(processes=num_workers) as pool:
        results = pool.map(worker, chunks)

    return [item for sublist in results for item in sublist]

if __name__ == "__main__":
    result = parallel_for_loop(df_tracklist)

    output_dir = "Preprocessing/Data/NewData"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "Data_FiO2.csv")
    df_results = pd.DataFrame(result)
    df_results.to_csv(output_path, index=False)

    print(f'Results saved to {output_path}')
