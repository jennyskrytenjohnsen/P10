import pandas as pd
import os

# Load clinical and lab data
clinical_data_url = "https://api.vitaldb.net/cases"
lab_data_url = "https://api.vitaldb.net/labs"

df_clinical = pd.read_csv(clinical_data_url)
df_lab = pd.read_csv(lab_data_url)

# Filter lab data for potassium
df_k = df_lab[df_lab["name"] == "k"]

# Store results
final_data = []

# Loop through cases
for _, row in df_clinical.iterrows():
    caseid = row['caseid']
    opstart = row['opstart']
    opend = row['opend']
    
    df_case_k = df_k[df_k['caseid'] == caseid]

    # --- Preop potassium: closest before opstart ---
    df_pre = df_case_k[df_case_k['dt'] < opstart]
    if not df_pre.empty:
        df_pre = df_pre.copy()
        df_pre['time_diff'] = (df_pre['dt'] - opstart).abs()
        prek = df_pre.loc[df_pre['time_diff'].idxmin(), 'result']
    else:
        prek = None

    # --- Periop potassium: closest during surgery to opend ---
    df_peri = df_case_k[(df_case_k['dt'] >= opstart) & (df_case_k['dt'] <= opend)]
    if not df_peri.empty:
        df_peri = df_peri.copy()
        df_peri['time_diff'] = (df_peri['dt'] - opend).abs()
        perik = df_peri.loc[df_peri['time_diff'].idxmin(), 'result']
    else:
        perik = None

    final_data.append({'caseid': caseid, 'prek': prek, 'perik': perik})

# Create final DataFrame
df_final = pd.DataFrame(final_data)

# Save to file
save_path = os.path.join('Preprocessing', 'Data', 'Data_k.csv')
os.makedirs(os.path.dirname(save_path), exist_ok=True)
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_k.csv' with prek and perik saved successfully at {save_path}.")
