import pandas as pd
import os

# Load clinical and lab data
clinical_data_url = "https://api.vitaldb.net/cases"
lab_data_url = "https://api.vitaldb.net/labs"

df_clinical = pd.read_csv(clinical_data_url)
df_lab = pd.read_csv(lab_data_url)

# Filter lab data for creatinine
df_cr = df_lab[df_lab["name"] == "cr"]

# List to store results
final_data = []

# Loop through cases
for _, row in df_clinical.iterrows():
    caseid = row['caseid']
    opstart = row['opstart']
    opend = row['opend']

    df_case_cr = df_cr[df_cr['caseid'] == caseid]

    # --- Preop creatinine: closest before opstart ---
    df_pre = df_case_cr[df_case_cr['dt'] < opstart]
    if not df_pre.empty:
        df_pre = df_pre.copy()
        df_pre['time_diff'] = (df_pre['dt'] - opstart).abs()
        precr = df_pre.loc[df_pre['time_diff'].idxmin(), 'result']
    else:
        precr = None

    # --- Periop creatinine: closest during surgery to opend ---
    df_peri = df_case_cr[(df_case_cr['dt'] >= opstart) & (df_case_cr['dt'] <= opend)]
    if not df_peri.empty:
        df_peri = df_peri.copy()
        df_peri['time_diff'] = (df_peri['dt'] - opend).abs()
        pericr = df_peri.loc[df_peri['time_diff'].idxmin(), 'result']
    else:
        pericr = None

    final_data.append({'caseid': caseid, 'precr': precr, 'pericr': pericr})

# Convert to DataFrame
df_final = pd.DataFrame(final_data)

# Save to CSV
save_path = os.path.join('Preprocessing', 'Data', 'Data_cr.csv')
os.makedirs(os.path.dirname(save_path), exist_ok=True)
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_cr.csv' with precr and pericr from lab has been saved successfully at {save_path}.")