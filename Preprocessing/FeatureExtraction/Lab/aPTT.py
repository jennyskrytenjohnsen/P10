import pandas as pd
import os

# Load clinical and lab data
clinical_data_url = "https://api.vitaldb.net/cases"
lab_data_url = "https://api.vitaldb.net/labs"

df_clinical = pd.read_csv(clinical_data_url)
df_lab = pd.read_csv(lab_data_url)

# Filter lab data for aPTT
df_aptt = df_lab[df_lab["name"] == "aptt"]

# Store final rows
final_data = []

# Loop through cases
for _, row in df_clinical.iterrows():
    caseid = row['caseid']
    preaptt = row.get('preop_aptt')  # from clinical dataset
    opstart = row['opstart']
    opend = row['opend']

    # Filter lab data for current case during surgery
    df_case_aptt = df_aptt[
        (df_aptt['caseid'] == caseid) &
        (df_aptt['dt'] >= opstart) &
        (df_aptt['dt'] <= opend)
    ]

    # --- Perioperative aPTT: closest to opend ---
    if not df_case_aptt.empty:
        df_case_aptt = df_case_aptt.copy()
        df_case_aptt['time_diff'] = (df_case_aptt['dt'] - opend).abs()
        periaptt = df_case_aptt.loc[df_case_aptt['time_diff'].idxmin(), 'result']
    else:
        periaptt = None

    final_data.append({
        'caseid': caseid,
        'preaptt': preaptt,
        'periaptt': periaptt
    })

# Convert to DataFrame
df_final = pd.DataFrame(final_data)

# Save to file
save_path = os.path.join('Preprocessing', 'Data', 'Data_aptt.csv')
os.makedirs(os.path.dirname(save_path), exist_ok=True)
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_aptt.csv' with preaptt (clinical) and periaptt (lab) has been saved at {save_path}.")