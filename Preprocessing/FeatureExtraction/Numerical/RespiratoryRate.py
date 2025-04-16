import pandas as pd
import requests
import io
import numpy as np
import os
import multiprocessing

# Track identifier for respiratory rate
RR_track = {'Solar8000/RR_CO2'}

def apply_median_filter(series, window=5):
    return series.rolling(window=window, center=True, min_periods=1).median()

def worker(subset, df_clinical, data_signal, results):
    subset = subset.reset_index(drop=True)
    local_results = []

    for index, row in subset.iterrows():
        if row['tname'] in RR_track:
            trackid = row['tid']
            caseid = row['caseid']
            print(f'Processing CaseID: {caseid}, TrackName: {row["tname"]}')

            # Extract numerical track data from API
            trackdata_url = f"https://api.vitaldb.net/{trackid}"
            response = requests.get(trackdata_url)

            if response.status_code == 200:
                trackdata = pd.read_csv(io.StringIO(response.text))

                # Get clinical case info
                case_info = df_clinical[df_clinical['caseid'] == caseid]
                signal_info = data_signal[data_signal['caseid'] == caseid]

                if not case_info.empty and not signal_info.empty:
                    opstart = case_info.iloc[0]['opstart']
                    opend = case_info.iloc[0]['opend']
                    rr_col = 'Solar8000/RR_CO2'

                    if rr_col in trackdata.columns:
                        # Apply median filter
                        trackdata[rr_col] = apply_median_filter(trackdata[rr_col])

                        # Filter for the operation time
                        mask_operation = (trackdata['Time'] >= opstart) & (trackdata['Time'] <= opend)
                        track_op = trackdata[mask_operation]

                        # Filter for the last 15 min
                        mask_15min = (trackdata['Time'] >= opend - 900) & (trackdata['Time'] <= opend)
                        track_15min = trackdata[mask_15min]

                        rr_values_op = track_op[rr_col]
                        rr_values_15min = track_15min[rr_col]

                        result_entry = {'caseid': caseid}

                        # Average during entire operation
                        if signal_info.iloc[0]['precentage_of_signal_is_there_total'] > 75:
                            result_entry['RR_total'] = rr_values_op.mean()
                            result_entry['RR_n12'] = (rr_values_op < 12).sum() / len(rr_values_op) * 100
                            result_entry['RR_n20'] = (rr_values_op > 20).sum() / len(rr_values_op) * 100
                        else:
                            result_entry['RR_total'] = np.nan
                            result_entry['RR_n12'] = np.nan
                            result_entry['RR_n20'] = np.nan

                        # Average during last 15 min
                        if signal_info.iloc[0]['precentage_of_signal_is_there_15min'] > 75:
                            result_entry['RR_w15min'] = rr_values_15min.mean()
                        else:
                            result_entry['RR_w15min'] = np.nan

                        local_results.append(result_entry)
                    else:
                        print(f"RR column missing for CaseID {caseid}")
                else:
                    print(f"Missing clinical or signal data for CaseID {caseid}")
            else:
                print(f"Failed to retrieve data for CaseID {caseid}")
    
    results.extend(local_results)

def parallel_for_loop(df, df_clinical, data_signal, num_workers=None):
    if num_workers is None:
        num_workers = multiprocessing.cpu_count()

    manager = multiprocessing.Manager()
    results = manager.list()

    chunks = np.array_split(df, num_workers)
    processes = []
    for chunk in chunks:
        p = multiprocessing.Process(target=worker, args=(chunk, df_clinical, data_signal, results))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    return list(results)

if __name__ == "__main__":
    # Load data inside the main block to avoid multiprocessing issues
    track_list_url = "https://api.vitaldb.net/trks"
    df_tracklist = pd.read_csv(track_list_url)

    clinical_data_url = "https://api.vitaldb.net/cases"
    df_clinical = pd.read_csv(clinical_data_url)

    data_signal = pd.read_csv("Preprocessing/MissingValues/saved_tracks_numerical_MC_total_15min.csv")

    result = parallel_for_loop(df_tracklist, df_clinical, data_signal)

    output_dir = "Preprocessing/Data/NewData"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "Data_RR.csv")
    df_results = pd.DataFrame(result)
    df_results.to_csv(output_path, index=False)

    print(f'Results saved to {output_path}')
