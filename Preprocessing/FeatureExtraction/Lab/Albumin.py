import pandas as pd
import os

# Load data
clinical_data_url = "https://api.vitaldb.net/cases"
lab_data_url = "https://api.vitaldb.net/labs"

df_clinical = pd.read_csv(clinical_data_url)
df_lab = pd.read_csv(lab_data_url)

# Filter lab data for albumin
df_alb = df_lab[df_lab["name"] == "alb"]

# List to collect results
final_data = []

# Loop through each case
for _, row in df_clinical.iterrows():
    caseid = row['caseid']
    opstart = row['opstart']
    opend = row['opend']

    df_case_alb = df_alb[df_alb['caseid'] == caseid]

    # --- Preop albumin: closest before opstart ---
    df_pre = df_case_alb[df_case_alb['dt'] < opstart]
    if not df_pre.empty:
        df_pre = df_pre.copy()
        df_pre['time_diff'] = (df_pre['dt'] - opstart).abs()
        prealb = df_pre.loc[df_pre['time_diff'].idxmin(), 'result']
    else:
        prealb = None

    # --- Periop albumin: closest during op to opend ---
    df_peri = df_case_alb[(df_case_alb['dt'] >= opstart) & (df_case_alb['dt'] <= opend)]
    if not df_peri.empty:
        df_peri = df_peri.copy()
        df_peri['time_diff'] = (df_peri['dt'] - opend).abs()
        perialb = df_peri.loc[df_peri['time_diff'].idxmin(), 'result']
    else:
        perialb = None

    final_data.append({'caseid': caseid, 'prealb': prealb, 'perialb': perialb})

# Convert to DataFrame and save
df_final = pd.DataFrame(final_data)
save_path = os.path.join('Preprocessing', 'Data', 'Data_alb.csv')
os.makedirs(os.path.dirname(save_path), exist_ok=True)
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_alb.csv' with prealb and perialb (from lab) saved successfully at {save_path}.")