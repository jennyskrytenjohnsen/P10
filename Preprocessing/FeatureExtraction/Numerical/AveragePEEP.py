import pandas as pd
import requests
import io
import numpy as np
import os
import multiprocessing

# Track identifier for PEEP
PEEP_track = {'Primus/PEEP_MBAR'}

# Load track list
track_list_url = "https://api.vitaldb.net/trks"
df_tracklist = pd.read_csv(track_list_url)

# Load clinical data
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Load the CSV file containing signal percentage information
data_signal = pd.read_csv("Preprocessing/MissingValues/saved_tracks_numerical_MC_total_15min.csv")

# Filter for only Primus/PEEP_MBAR track data
data_signal = data_signal[data_signal["tname"] == "Primus/PEEP_MBAR"]

# Prepare a list to store results
# manager = multiprocessing.Manager()
# results = manager.list()
results = []

def worker(subset):
    local_results = []
    subset = subset.reset_index(drop=True)
    for index, row in subset.iterrows():
        if row['tname'] in PEEP_track:
            trackid = row['tid']
            caseid = row['caseid']
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

                    if 'Primus/PEEP_MBAR' in trackdata_filtered.columns and not trackdata_filtered.empty:
                        # Apply median filter with window size 5 (can adjust as needed)
                        trackdata_filtered['PEEP_filtered'] = trackdata_filtered['Primus/PEEP_MBAR'].rolling(window=5, center=True, min_periods=1).median()

                        # Get signal quality info
                        signal_info = data_signal[data_signal['caseid'] == caseid]
                        avg_total = avg_15min = None

                        if not signal_info.empty:
                            pct_total = signal_info.iloc[0]['precentage_of_signal_is_there_total']
                            pct_15min = signal_info.iloc[0]['precentage_of_signal_is_there_15min']

                            if pct_total > 75:
                                avg_total = trackdata_filtered['PEEP_filtered'].mean()

                            # # Last 15 minutes of the operation
                            # opend_time = trackdata_filtered['Time'].max()
                            # last_15min_start = opend_time - 15 * 60 * 1000  # Assuming time in milliseconds
                            # last_15min_data = trackdata_filtered[trackdata_filtered['Time'] >= last_15min_start].copy()

                            # if pct_15min > 75 and not last_15min_data.empty:
                            #     avg_15min = last_15min_data['PEEP_filtered'].mean()

                            # local_results.append({
                            #     'caseid': caseid,
                            #     'PEEP_total': avg_total,
                            #     'PEEP_w15min': avg_15min
                            # })

                            # Last 15 minutes of the operation
                            opend_time = trackdata_filtered['Time'].max()
                            last_15min_start = opend_time - 15 * 60 * 1000  # Assuming time in milliseconds
                            last_15min_data = trackdata_filtered[trackdata_filtered['Time'] >= last_15min_start].copy()

                            avg_15min = None
                            avg_15min_mv = None

                            if not last_15min_data.empty:
                                avg_15min_mv = last_15min_data['PEEP_filtered'].mean()  # Always save this if any data is present

                                if pct_15min > 75:
                                    avg_15min = avg_15min_mv  # Only save in PEEP_w15min if quality is sufficient

                            local_results.append({
                                'caseid': caseid,
                                'PEEP_total': avg_total,
                                'PEEP_w15min': avg_15min,
                                'PEEP_w15minMV': avg_15min_mv
                            })

                        else:
                            print(f"No signal quality data for CaseID {caseid}")
                    else:
                        print(f"No Primus/PEEP_MBAR data for CaseID {caseid}")
                else:
                    print(f"Missing case info for CaseID {caseid}")
            else:
                print(f'Failed to retrieve data for CaseID {caseid}')
    # results.extend(local_results)
    return local_results


def parallel_for_loop(df, num_workers=None):
    if num_workers is None:
        num_workers = multiprocessing.cpu_count()

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input data must be a DataFrame.")

    chunks = np.array_split(df, num_workers)
    processes = []

    # for chunk in chunks:
    #     p = multiprocessing.Process(target=worker, args=(chunk,))
    #     processes.append(p)
    #     p.start()

    # for p in processes:
    #     p.join()
    
    with multiprocessing.Pool(processes=num_workers) as pool:
        results_nested = pool.map(worker, chunks)

    return [item for sublist in results_nested for item in sublist]

    # return list(results)


if __name__ == "__main__":
    result = parallel_for_loop(df_tracklist)

    output_dir = "Preprocessing/Data/NewData"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "Data_PEEP.csv")
    df_results = pd.DataFrame(result)
    df_results.to_csv(output_path, index=False)

    print(f'Data saved to {output_path}')
