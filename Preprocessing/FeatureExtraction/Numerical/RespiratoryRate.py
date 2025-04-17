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

def process_row(row, df_clinical, data_signal):
    if row['tname'] not in RR_track:
        return None

    trackid = row['tid']
    caseid = row['caseid']
    print(f'Processing CaseID: {caseid}, TrackName: {row["tname"]}')

    try:
        response = requests.get(f"https://api.vitaldb.net/{trackid}")
        if response.status_code != 200:
            print(f"Failed to retrieve data for CaseID {caseid}")
            return None
        trackdata = pd.read_csv(io.StringIO(response.text))
    except Exception as e:
        print(f"Exception retrieving track data for CaseID {caseid}: {e}")
        return None

    case_info = df_clinical[df_clinical['caseid'] == caseid]
    signal_info = data_signal[data_signal['caseid'] == caseid]

    if case_info.empty or signal_info.empty:
        print(f"Missing clinical or signal data for CaseID {caseid}")
        return None

    opstart = case_info.iloc[0]['opstart']
    opend = case_info.iloc[0]['opend']
    rr_col = 'Solar8000/RR_CO2'

    if rr_col not in trackdata.columns:
        print(f"RR column missing for CaseID {caseid}")
        return None

    trackdata[rr_col] = apply_median_filter(trackdata[rr_col])

    # Operation and last 15 minutes
    mask_op = (trackdata['Time'] >= opstart) & (trackdata['Time'] <= opend)
    track_op = trackdata[mask_op]

    mask_15min = (trackdata['Time'] >= opend - 900) & (trackdata['Time'] <= opend)
    track_15min = trackdata[mask_15min]

    rr_op = track_op[rr_col]
    rr_15min = track_15min[rr_col]
    rr_15min_clean = rr_15min.dropna()

    result_entry = {'caseid': caseid}

    # Entire operation averages
    if signal_info.iloc[0]['precentage_of_signal_is_there_total'] > 75:
        result_entry['RR_total'] = rr_op.mean()
        result_entry['RR_n12'] = (rr_op < 12).sum() / len(rr_op) * 100
        result_entry['RR_n20'] = (rr_op > 20).sum() / len(rr_op) * 100
    else:
        result_entry['RR_total'] = np.nan
        result_entry['RR_n12'] = np.nan
        result_entry['RR_n20'] = np.nan

    # Last 15 min averages
    if len(rr_15min) > 0:
        missing_pct = 100 * (len(rr_15min) - len(rr_15min_clean)) / len(rr_15min)
        result_entry['RR_w15minMV'] = rr_15min.mean()

        if missing_pct <= 25:
            result_entry['RR_w15min'] = rr_15min_clean.mean()
        else:
            result_entry['RR_w15min'] = np.nan
    else:
        result_entry['RR_w15minMV'] = np.nan
        result_entry['RR_w15min'] = np.nan

    return result_entry

if __name__ == "__main__":
    # Load data
    track_list_url = "https://api.vitaldb.net/trks"
    df_tracklist = pd.read_csv(track_list_url)

    clinical_data_url = "https://api.vitaldb.net/cases"
    df_clinical = pd.read_csv(clinical_data_url)

    data_signal = pd.read_csv("Preprocessing/MissingValues/saved_tracks_numerical_MC_total_15min.csv")

    # Convert rows to dictionaries so they are serializable
    tracklist_dicts = df_tracklist.to_dict(orient="records")

    # Use Pool for multiprocessing
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        args = [(row, df_clinical, data_signal) for row in tracklist_dicts]
        result = pool.starmap(process_row, args)

    # Filter out None entries
    result = [r for r in result if r is not None]

    # Save to CSV
    output_dir = "Preprocessing/Data/NewData"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "Data_RR.csv")

    df_results = pd.DataFrame(result)
    df_results.to_csv(output_path, index=False)

    print(f'Results saved to {output_path}')
