import pandas as pd
import requests
import io
import numpy as np
import os
import multiprocessing

HR_track = {'Solar8000/HR'}

track_list_url = "https://api.vitaldb.net/trks"
df_tracklist = pd.read_csv(track_list_url)

clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

data_signal = pd.read_csv("Preprocessing/MissingValues/saved_tracks_numerical_MC_total_15min.csv")
data_signal = data_signal[data_signal["tname"] == "Solar8000/HR"]

def worker(subset):
    results_local = []

    for index, row in subset.iterrows():
        if row['tname'] in HR_track:
            trackid = row['tid']
            caseid = row['caseid']
            print(f'Processing CaseID: {caseid}, TrackName: {row["tname"]}')

            trackdata_url = f"https://api.vitaldb.net/{trackid}"
            response = requests.get(trackdata_url)

            if response.status_code == 200:
                trackdata = pd.read_csv(io.StringIO(response.text))
                case_info = df_clinical[df_clinical['caseid'] == caseid]
                signal_info = data_signal[data_signal['caseid'] == caseid]

                if not case_info.empty:
                    opstart = case_info.iloc[0]['opstart']
                    opend = case_info.iloc[0]['opend']

                    trackdata_filtered = trackdata[(trackdata['Time'] >= opstart) & (trackdata['Time'] <= opend)]

                    if not np.issubdtype(trackdata_filtered['Time'].dtype, np.number):
                        trackdata_filtered['Time'] = pd.to_numeric(trackdata_filtered['Time'], errors='coerce')

                    # Median filtering
                    trackdata_filtered['HR_filtered'] = trackdata_filtered['Solar8000/HR'].rolling(
                        window=9, center=True, min_periods=1).median()

                    total_seconds = len(trackdata_filtered)
                    seconds_below_30 = (trackdata_filtered['HR_filtered'] < 30).sum()
                    seconds_below_60 = (trackdata_filtered['HR_filtered'] < 60).sum()
                    seconds_above_100 = (trackdata_filtered['HR_filtered'] > 100).sum()

                    if total_seconds > 0:
                        percent_below_30 = (seconds_below_30 / total_seconds) * 100
                        percent_below_60 = (seconds_below_60 / total_seconds) * 100
                        percent_above_100 = (seconds_above_100 / total_seconds) * 100
                        mean_full = trackdata_filtered['HR_filtered'].mean()
                    else:
                        percent_below_30 = percent_below_60 = percent_above_100 = "No Data"
                        mean_full = "No Data"

                    start_15min = max(opstart, opend - 900)
                    last_15min_data = trackdata_filtered[
                        (trackdata_filtered['Time'] >= start_15min) &
                        (trackdata_filtered['Time'] <= opend)
                    ].copy()

                    HR_w15min = HR_w15minMV = "No Data"

                    if not last_15min_data.empty:
                        last_15min_data['HR_filtered'] = last_15min_data['HR_filtered'].rolling(
                            window=9, center=True, min_periods=1).median()

                        # Calculate mean regardless of completeness
                        HR_w15minMV = last_15min_data['HR_filtered'].mean()

                        # Determine how much data is missing
                        duration = opend - start_15min
                        expected_points = int(duration)  # assuming 1 Hz frequency
                        actual_points = len(last_15min_data)
                        percent_present = (actual_points / expected_points) * 100 if expected_points > 0 else 0

                        if percent_present >= 75:
                            HR_w15min = HR_w15minMV

                    results_local.append({
                        'caseid': caseid,
                        'HR_n30': percent_below_30,
                        'HR_n60': percent_below_60,
                        'HR_n100': percent_above_100,
                        'HR_total': mean_full,
                        'HR_w15min': HR_w15min,
                        'HR_w15minMV': HR_w15minMV
                    })

                    print(f'→ CaseID {caseid}: HR<30: {percent_below_30:.2f}%, HR<60: {percent_below_60:.2f}%, HR>100: {percent_above_100:.2f}%')
                    print(f'→ AvgHR (full): {mean_full}, AvgHR (last 15 min): {HR_w15min}, MV version: {HR_w15minMV}')
                else:
                    print(f'Skipping CaseID {caseid} due to missing case info.')
            else:
                print(f'Failed to retrieve data for CaseID {caseid}')

    return results_local


def parallel_for_loop(df, num_workers=None):
    if num_workers is None:
        num_workers = multiprocessing.cpu_count()

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input data must be a DataFrame.")

    chunks = np.array_split(df, num_workers)

    with multiprocessing.Pool(processes=num_workers) as pool:
        results_nested = pool.map(worker, chunks)

    return [item for sublist in results_nested for item in sublist]


if __name__ == "__main__":
    all_results = parallel_for_loop(df_tracklist)

    output_dir = "Preprocessing/Data/NewData"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "Data_HR.csv")

    df_results = pd.DataFrame(all_results)
    df_results.to_csv(output_path, index=False)

    print(f'Data saved to {output_path}')
