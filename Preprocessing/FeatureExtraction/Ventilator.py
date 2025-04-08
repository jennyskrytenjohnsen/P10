import pandas as pd
import requests
import io
import os

# Track identifiers for ventilation parameters
ventilator_tracks = {
    'Solar8000/VENT_COMPL', 'Solar8000/VENT_INSP_TM', 'Solar8000/VENT_MAWP',
    'Solar8000/VENT_MEAS_PEEP', 'Solar8000/VENT_MV', 'Solar8000/VENT_PIP',
    'Solar8000/VENT_PPLAT', 'Solar8000/VENT_RR', 'Solar8000/VENT_SET_FIO2',
    'Solar8000/VENT_SET_PCP', 'Solar8000/VENT_SET_TV', 'Solar8000/VENT_TV',
    'Primus/VENT_LEAK'
}

# Load track list
df_tracklist = pd.read_csv("https://api.vitaldb.net/trks")

# Load clinical data
df_clinical = pd.read_csv("https://api.vitaldb.net/cases")

# Prepare a list to store results
results = []

# Iterate over each case
for i, caseid in enumerate(df_clinical['caseid'].unique(), 1):
    print(f"Processing caseid: {caseid} ({i}/{len(df_clinical)})")

    # Filter tracks for the current case
    case_tracks = df_tracklist[df_tracklist['caseid'] == caseid]
    track_ids = case_tracks[case_tracks['tname'].isin(ventilator_tracks)]

    data_vent = 0  # Default to 0

    for _, track in track_ids.iterrows():
        trackid, tname = track['tid'], track['tname']

        # Extract numerical track data from API
        trackdata_url = f"https://api.vitaldb.net/{trackid}"
        response = requests.get(trackdata_url)

        if response.status_code == 200:
            trackdata = pd.read_csv(io.StringIO(response.text))

            if tname in trackdata.columns and (trackdata[tname] != 0).any():
                print(f"  Found non-zero values in {tname} for caseid {caseid}")
                data_vent = 1
                break

    results.append({
        'caseid': caseid,
        'data_vent': data_vent
    })

    print(f"  Finished caseid {caseid}, data_vent = {data_vent}")

    if i % 50 == 0:
        print(f"--- Processed {i} cases so far ---")

# Save to CSV
output_dir = "Preprocessing/Data"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "Data_ventilator.csv")
df_results = pd.DataFrame(results)
df_results.to_csv(output_path, index=False)

print(f"\nAll done! Data saved to {output_path}")
