import pandas as pd
import requests
import io
import numpy as np
import os
import multiprocessing

# Track identifier for heart rate
SysBP_track = {'Solar8000/ART_SBP'} 

# Load track list
track_list_url = "https://api.vitaldb.net/trks"
df_tracklist = pd.read_csv(track_list_url)

# Load clinical data
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Load the CSV file containing signal percentage information
data_signal = pd.read_csv("Preprocessing/MissingValues/saved_tracks_numerical_MC_total_15min.csv")

# Filter for only Solar8000/ART_SBP track data
data_signal = data_signal[data_signal["tname"] == "Solar8000/ART_SBP"]

def worker(subset):
    process_name = multiprocessing.current_process().name
    subset = subset.reset_index(drop=True)
    print("Processing subset of size:", len(subset))
    results = []

    for index, row in subset.iterrows():
        if row['tname'] in SysBP_track:
            trackid = row['tid']
            caseid = row['caseid']
            print(f'Processing CaseID: {caseid}, TrackName: {row["tname"]}')
            
            # Extract numerical track data
            trackdata_url = f"https://api.vitaldb.net/{trackid}"
            response = requests.get(trackdata_url)

            if response.status_code == 200:
                trackdata = pd.read_csv(io.StringIO(response.text))
                case_info = df_clinical[df_clinical['caseid'] == caseid]

                if not case_info.empty:
                    opstart = case_info.iloc[0]['opstart']
                    opend = case_info.iloc[0]['opend']

                    trackdata_filtered = trackdata[(trackdata['Time'] >= opstart) & (trackdata['Time'] <= opend)]

                    if 'Solar8000/ART_SBP' in trackdata_filtered.columns and not trackdata_filtered.empty:
                        # Apply moving median filter with window of 5 samples
                        trackdata_filtered['Filtered'] = trackdata_filtered['Solar8000/ART_SBP'].rolling(window=5, center=True).median()
                        trackdata_filtered = trackdata_filtered.dropna(subset=['Filtered'])  # Drop rows where rolling window gives NaN

                        # Signal info
                        signal_info = data_signal[data_signal['caseid'] == caseid]

                        avg_all = "NaN"
                        avg_15min = "NaN"
                        perc_below_80 = "NaN"
                        perc_above_180 = "NaN"
                        avg_15min_mv = "NaN"  # New column to capture the average with missing values allowed

                        if not signal_info.empty:
                            if signal_info.iloc[0]['precentage_of_signal_is_there_total'] > 75:
                                avg_all = trackdata_filtered['Filtered'].mean()

                                # Percentage below 80 and above 180
                                total_points = len(trackdata_filtered)
                                perc_below_80 = (trackdata_filtered['Filtered'] < 80).sum() / total_points * 100
                                perc_above_180 = (trackdata_filtered['Filtered'] > 180).sum() / total_points * 100

                            # Calculate the 15 minute average, handling missing values
                            if signal_info.iloc[0]['precentage_of_signal_is_there_15min'] > 75:
                                max_time = trackdata_filtered['Time'].max()
                                start_15min = max_time - 15 * 60
                                data_last_15 = trackdata_filtered[trackdata_filtered['Time'] >= start_15min]

                                # If there is any data in the last 15 minutes, calculate average
                                if not data_last_15.empty:
                                    avg_15min = data_last_15['Filtered'].mean()
                                    avg_15min_mv = data_last_15['Filtered'].mean()  # Allowing missing values in this column as well
                                else:
                                    avg_15min = "NaN"
                                    avg_15min_mv = "NaN"

                            results.append({
                                'caseid': caseid,
                                'SysBP_total': avg_all,
                                'SysBP_w15min': avg_15min,
                                'SysBP_n80': perc_below_80,
                                'SysBP_n180': perc_above_180,
                                'SysBP_w15minMV': avg_15min_mv  # Save the value with missing data allowed
                            })
                        else:
                            print(f'No signal info for CaseID {caseid}')
                    else:
                        print(f'Missing data for CaseID {caseid}')
                else:
                    print(f'Missing case info for CaseID {caseid}')
            else:
                print(f'Failed to retrieve data for CaseID {caseid}')

    return results

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
    output_path = os.path.join(output_dir, "Data_SysBP.csv")
    df_results = pd.DataFrame(result)
    df_results.to_csv(output_path, index=False)

    print(f'Data saved to {output_path}')
