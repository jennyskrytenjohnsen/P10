import pandas as pd
import requests
import io
import numpy as np
import os
import multiprocessing

# Track identifier for heart rate
DiaBP_track = {'Solar8000/ART_DBP'} 
 
# Load track list
track_list_url = "https://api.vitaldb.net/trks"
df_tracklist = pd.read_csv(track_list_url)

# Load clinical data
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Load the CSV file containing signal percentage information
data_signal = pd.read_csv("Preprocessing/MissingValues/saved_tracks_numerical_MC_total_15min.csv")

# Filter for only Solar8000/ART_DBP track data
data_signal = data_signal[data_signal["tname"] == "Solar8000/ART_DBP"]

def worker(subset):
    process_name = multiprocessing.current_process().name
    subset = subset.reset_index(drop=True)
    print("Processing subset of size:", len(subset))
    results = []

    for index, row in subset.iterrows():
        if row['tname'] in DiaBP_track:
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

                    if 'Solar8000/ART_DBP' in trackdata_filtered.columns and not trackdata_filtered.empty:
                        # Apply moving median filter
                        trackdata_filtered['Filtered'] = trackdata_filtered['Solar8000/ART_DBP'].rolling(window=5, center=True).median()
                        trackdata_filtered = trackdata_filtered.dropna(subset=['Filtered'])

                        signal_info = data_signal[data_signal['caseid'] == caseid]

                        avg_all = "NaN"
                        avg_15min = "NaN"
                        avg_15minMV = "NaN"
                        perc_below_40 = "NaN"
                        perc_above_100 = "NaN"

                        if not signal_info.empty:
                            if signal_info.iloc[0]['precentage_of_signal_is_there_total'] > 75:
                                avg_all = trackdata_filtered['Filtered'].mean()
                                total_points = len(trackdata_filtered)
                                perc_below_40 = (trackdata_filtered['Filtered'] < 40).sum() / total_points * 100
                                perc_above_100 = (trackdata_filtered['Filtered'] > 100).sum() / total_points * 100

                            max_time = trackdata_filtered['Time'].max()
                            start_15min = max_time - 15 * 60
                            data_last_15 = trackdata_filtered[trackdata_filtered['Time'] >= start_15min]

                            if not data_last_15.empty:
                                avg_15minMV = data_last_15['Filtered'].mean()
                                # Check if we have >75% signal in the 15min window
                                if signal_info.iloc[0]['precentage_of_signal_is_there_15min'] > 75:
                                    avg_15min = avg_15minMV

                        results.append({
                            'caseid': caseid,
                            'DiaBP_total': avg_all,
                            'DiaBP_w15min': avg_15min,
                            'DiaBP_w15minMV': avg_15minMV,
                            'DiaBP_n40': perc_below_40,
                            'DiaBP_n100': perc_above_100
                        })
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
    output_path = os.path.join(output_dir, "Data_DiaBP.csv")
    df_results = pd.DataFrame(result)
    df_results.to_csv(output_path, index=False)

    print(f'Data saved to {output_path}')
