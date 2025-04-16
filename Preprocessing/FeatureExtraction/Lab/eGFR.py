import pandas as pd
import os

# Load data
clinical_data_url = "https://api.vitaldb.net/cases"
lab_data_url = "https://api.vitaldb.net/labs"

df_clinical = pd.read_csv(clinical_data_url)
df_lab = pd.read_csv(lab_data_url)

# Filter lab data for GFR
df_gfr = df_lab[df_lab["name"] == "gfr"]

# Store results
final_data = []

# Loop through patient cases
for _, row in df_clinical.iterrows():
    caseid = row['caseid']
    opstart = row['opstart']
    opend = row['opend']

    df_case_gfr = df_gfr[df_gfr['caseid'] == caseid]

    # --- Preop GFR: closest before opstart ---
    df_pre = df_case_gfr[df_case_gfr['dt'] < opstart]
    if not df_pre.empty:
        df_pre = df_pre.copy()
        df_pre['time_diff'] = (df_pre['dt'] - opstart).abs()
        pregfr = df_pre.loc[df_pre['time_diff'].idxmin(), 'result']
    else:
        pregfr = None

    # --- Periop GFR: closest during surgery to opend ---
    df_peri = df_case_gfr[(df_case_gfr['dt'] >= opstart) & (df_case_gfr['dt'] <= opend)]
    if not df_peri.empty:
        df_peri = df_peri.copy()
        df_peri['time_diff'] = (df_peri['dt'] - opend).abs()
        perigfr = df_peri.loc[df_peri['time_diff'].idxmin(), 'result']
    else:
        perigfr = None

    final_data.append({'caseid': caseid, 'pregfr': pregfr, 'perigfr': perigfr})

# Convert to DataFrame
df_final = pd.DataFrame(final_data)

# Save to CSV
save_path = os.path.join('Preprocessing', 'Data', 'Data_gfr.csv')
os.makedirs(os.path.dirname(save_path), exist_ok=True)
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_gfr.csv' with pregfr and perigfr saved successfully at {save_path}.")
