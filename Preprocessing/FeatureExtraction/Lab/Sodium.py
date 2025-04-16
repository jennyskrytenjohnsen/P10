import pandas as pd
import os

# Load data
clinical_data_url = "https://api.vitaldb.net/cases"
lab_data_url = "https://api.vitaldb.net/labs"

df_clinical = pd.read_csv(clinical_data_url)
df_lab = pd.read_csv(lab_data_url)

# Filter lab data for sodium
df_na = df_lab[df_lab["name"] == "na"]

# Store results
final_data = []

for _, row in df_clinical.iterrows():
    caseid = row['caseid']
    opstart = row['opstart']
    opend = row['opend']
    
    df_case_na = df_na[df_na['caseid'] == caseid]

    # --- Preoperative sodium ---
    df_pre = df_case_na[df_case_na['dt'] < opstart]
    if not df_pre.empty:
        df_pre = df_pre.copy()
        df_pre['time_diff'] = (df_pre['dt'] - opstart).abs()
        prena = df_pre.loc[df_pre['time_diff'].idxmin(), 'result']
    else:
        prena = None

    # --- Perioperative sodium ---
    df_peri = df_case_na[(df_case_na['dt'] >= opstart) & (df_case_na['dt'] <= opend)]
    if not df_peri.empty:
        df_peri = df_peri.copy()
        df_peri['time_diff'] = (df_peri['dt'] - opend).abs()
        perina = df_peri.loc[df_peri['time_diff'].idxmin(), 'result']
    else:
        perina = None

    final_data.append({'caseid': caseid, 'prena': prena, 'perina': perina})

# Convert and save
df_final = pd.DataFrame(final_data)
save_path = os.path.join('Preprocessing', 'Data', 'Data_na.csv')
os.makedirs(os.path.dirname(save_path), exist_ok=True)
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_na.csv' with prena and perina saved successfully at {save_path}.")
