import pandas as pd
import requests
import io
import numpy as np
import os
import multiprocessing

# Track identifier for SpO2
target_track = 'Solar8000/PLETH_SPO2'

# Load track list
track_list_url = "https://api.vitaldb.net/trks"
df_tracklist = pd.read_csv(track_list_url)

# Load clinical data
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Load signal percentage info
data_signal = pd.read_csv("Preprocessing/MissingValues/saved_tracks_numerical_MC_total_15min.csv")
data_signal = data_signal[data_signal["tname"] == target_track]

# Prepare multiprocessing-safe result container
def worker(subset):
    subset = subset.reset_index(drop=True)
    local_results = []

    for index, row in subset.iterrows():
        if row['tname'] != target_track:
            continue

        trackid = row['tid']
        caseid = row['caseid']
        print(f'Processing CaseID: {caseid}')

        # Get signal percentage info
        signal_info = data_signal[data_signal['caseid'] == caseid]
        if signal_info.empty:
            print(f'Skipping CaseID {caseid} due to missing signal info')
            continue

        perc_total = signal_info.iloc[0]['precentage_of_signal_is_there_total']
        perc_15min = signal_info.iloc[0]['precentage_of_signal_is_there_15min']

        # Download track data
        trackdata_url = f"https://api.vitaldb.net/{trackid}"
        response = requests.get(trackdata_url)
        if response.status_code != 200:
            print(f'Failed to retrieve data for CaseID {caseid}')
            continue

        trackdata = pd.read_csv(io.StringIO(response.text))
        if target_track not in trackdata.columns:
            print(f'Missing target column for CaseID {caseid}')
            continue

        # Apply moving median filter (window size = 5)
        trackdata[target_track] = trackdata[target_track].rolling(window=5, center=True, min_periods=1).median()

        # Get surgery end time
        case_info = df_clinical[df_clinical['caseid'] == caseid]
        if case_info.empty:
            print(f'No clinical info for CaseID {caseid}')
            continue

        opend = case_info.iloc[0]['opend']

        # Filter for last 15 minutes
        last_15_min_mask = (trackdata['Time'] >= opend - 900) & (trackdata['Time'] <= opend)
        trackdata_last = trackdata[last_15_min_mask]

        # Filter for full operation duration
        full_op_mask = (trackdata['Time'] <= opend)
        trackdata_full = trackdata[full_op_mask]

        # Initialize result record
        result = {
            'caseid': caseid,
            'SpO2_total': np.nan,
            'SpO2_w15min': np.nan,
            'SpO2_n90': np.nan
        }

        # Compute average over entire operation
        if perc_total > 75 and not trackdata_full.empty:
            result['SpO2_total'] = trackdata_full[target_track].mean()
            below_90 = trackdata_full[target_track] < 90
            result['SpO2_n90'] = below_90.sum() / len(trackdata_full) * 100

        # Compute average over last 15 minutes
        if perc_15min > 75 and not trackdata_last.empty:
            result['SpO2_w15min'] = trackdata_last[target_track].mean()

        print(f'Finished CaseID {caseid}')
        local_results.append(result)

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
    output_path = os.path.join(output_dir, "Data_SpO2.csv")
    df_results = pd.DataFrame(result)
    df_results.to_csv(output_path, index=False)

    print(f'Results saved to {output_path}')
