import pandas as pd
import os

# Load clinical and lab data
clinical_data_url = "https://api.vitaldb.net/cases"
lab_data_url = "https://api.vitaldb.net/labs"

df_clinical = pd.read_csv(clinical_data_url)
df_lab = pd.read_csv(lab_data_url)

# Filter lab data for pt%
df_pt = df_lab[df_lab["name"] == "pt%"]

# Prepare result list
final_data = []

# Loop through clinical cases
for _, row in df_clinical.iterrows():
    caseid = row['caseid']
    prept = row.get('preop_pt')  # From clinical dataset
    opstart = row['opstart']
    opend = row['opend']

    # Filter lab pt% values for the current case during surgery
    df_case_pt = df_pt[
        (df_pt['caseid'] == caseid) &
        (df_pt['dt'] >= opstart) &
        (df_pt['dt'] <= opend)
    ]

    # --- Perioperative PT%: closest to opend ---
    if not df_case_pt.empty:
        df_case_pt = df_case_pt.copy()
        df_case_pt['time_diff'] = (df_case_pt['dt'] - opend).abs()
        peript = df_case_pt.loc[df_case_pt['time_diff'].idxmin(), 'result']
    else:
        peript = None

    final_data.append({
        'caseid': caseid,
        'prept': prept,
        'peript': peript
    })

# Convert to DataFrame
df_final = pd.DataFrame(final_data)

# Save to CSV
save_path = os.path.join('Preprocessing', 'Data', 'Data_pt.csv')
os.makedirs(os.path.dirname(save_path), exist_ok=True)
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_pt.csv' with prept and peript has been saved successfully at {save_path}.")
