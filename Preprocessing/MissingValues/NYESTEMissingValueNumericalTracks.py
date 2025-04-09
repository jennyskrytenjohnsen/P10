import pandas as pd
import requests
import io
import numpy as np
import multiprocessing

# track identifier (den konkrete patients konktere måling)
track_list_url = "https://api.vitaldb.net/trks"
df_tracklist = pd.read_csv(track_list_url)


def worker(subset):
    process_name = multiprocessing.current_process().name
    subset = subset.reset_index(drop=True)
    index_len = len(subset)
    print("Processing subset of size:", index_len)
    save_numerical_tracks = []
    special_variables = {
    'Solar8000/PLETH_HR', 'Orchestra/NEPI_VOL', 'Orchestra/EPI_VOL', 'Orchestra/PHEN_VOL', 'Orchestra/VASO_VOL',
    'Orchestra/DOPA_VOL', 'Orchestra/DOBU_VOL', 'Orchestra/MRN_VOL', 'Solar8000/NIBP_SBP', 'Solar8000/NIBP_DBP', 
    'Solar8000/ART_MBP', 'Solar8000/NIBP_MBP', 'Solar8000/HR', 'CardioQ/HR', 'Vigilance/HR_AVG',
    'Vigileo/CO', 'EV1000/CO', 'Vigilance/CO', 'CardioQ/CO', 'Solar8000/PLETH_SPO2', 'Vigilance/SVO2',
    'Solar8000/FIO2', 'Primus/FIO2', 'Solar8000/RR', 'Primus/PEEP_MBAR', 'Solar8000/VENT_TV', 'Primus/TV',
    'Solar8000/VENT_MEAS_PEEP', 'Solar8000/VENT_PIP', 'Primus/PIP_MBAR',
    'Solar8000/ART_SBP', 'Solar8000/ART_DBP'}

    for index, row in subset.iterrows():
        if row['tname'] in special_variables:
            trackid = row['tid']
            caseid = row['caseid']
            print('Caseid', caseid, 'TrackName:', row['tname'])

            trackdata_url = f"https://api.vitaldb.net/{trackid}"
            response = requests.get(trackdata_url)
            trackdata = pd.read_csv(io.StringIO(response.text))

            if trackdata.empty or 'Time' not in trackdata.columns:
                print(f"Track {trackid} is empty or malformed.")
                continue

            # Find min_gap from first 20 samples
            min_gap = trackdata.iloc[:500]['Time'].diff().min()

            last_time = trackdata['Time'].iloc[-1]
            total_expected_samples = last_time / min_gap
            total_actual_samples = len(trackdata['Time'])
            total_missing = total_expected_samples - total_actual_samples
            percent_total = (total_actual_samples / total_expected_samples) * 100

            # --- 15-minute segment calculation ---
            fifteen_min_start = max(0, last_time - 900)
            track_15min = trackdata[trackdata['Time'] >= fifteen_min_start]

            if len(track_15min) > 1:
                time_range_15 = track_15min['Time'].iloc[-1] - track_15min['Time'].iloc[0]
                expected_15min_samples = time_range_15 / min_gap
                actual_15min_samples = len(track_15min['Time'])
                percent_15min = (actual_15min_samples / expected_15min_samples) * 100
            else:
                percent_15min = 0.0

            if total_expected_samples > 1.2 * total_actual_samples:
                print(f'No index: {index} of {index_len} — total %: {percent_total:.2f} — 15min %: {percent_15min:.2f}')
            else:
                print(f'Yes index: {index} of {index_len} — total %: {percent_total:.2f} — 15min %: {percent_15min:.2f}')
                save_numerical_tracks.append([
                    caseid, row['tname'], trackid,
                    total_expected_samples, total_actual_samples,
                    min_gap, total_missing,
                    percent_total, percent_15min
                ])

    return save_numerical_tracks

#####

def parallel_for_loop(df, num_workers=None):
    """Splits the for loop workload across multiple CPU cores."""
    if num_workers is None:
        num_workers = multiprocessing.cpu_count()  # Use all available cores

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input data must be a DataFrame.")

    chunks = np.array_split(df, num_workers)

    with multiprocessing.Pool(processes=num_workers) as pool:
        results = pool.map(worker, chunks)

    return [item for sublist in results for item in sublist]

if __name__ == "__main__":
    
    result = parallel_for_loop(df_tracklist)
    if result:
        df_saved_tracks = pd.DataFrame(result, columns=["caseid", "tname", "tid", "how_many_samples_should_there_be","total_samples_of_singal", "min_gap", "samples_missing", "precentage_of_signal_is_there_total", "precentage_of_signal_is_there_15min"])
        df_saved_tracks.to_csv("saved_tracks_numerical_MC_total_15min.csv", index=False)
        print("CSV file has been saved.")
    else:
        print("No tracks met the criteria for saving.:()")
    print(result)