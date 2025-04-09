import pandas as pd
import os

# Load clinical dataset
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Load lab data
lab_data_url = "https://api.vitaldb.net/labs"
df_lab = pd.read_csv(lab_data_url)

# Filter lab data for ionized calcium (ica)
df_ica = df_lab[df_lab["name"] == "ica"]

# Prepare list to collect results
final_data = []

# Loop through each patient/case
for index, row in df_clinical.iterrows():
    caseid = row['caseid']
    opstart_time = row['opstart']
    opend_time = row['opend']
    
    df_case_ica = df_ica[df_ica['caseid'] == caseid]

    # --- Preoperative ionized calcium ---
    df_pre = df_case_ica[df_case_ica['dt'] < opstart_time]
    if not df_pre.empty:
        preica = df_pre.loc[df_pre['dt'].idxmax(), 'result']
    else:
        preica = None

    # --- Perioperative ionized calcium (closest to opend) ---
    df_peri = df_case_ica[(df_case_ica['dt'] >= opstart_time) & (df_case_ica['dt'] <= opend_time)]
    if not df_peri.empty:
        df_peri = df_peri.copy()
        df_peri['time_diff'] = (df_peri['dt'] - opend_time).abs()
        perica = df_peri.loc[df_peri['time_diff'].idxmin(), 'result']
    else:
        perica = None

    final_data.append({'caseid': caseid, 'preica': preica, 'perica': perica})

# Create DataFrame
df_final = pd.DataFrame(final_data)

# Save to CSV
save_path = os.path.join('Preprocessing', 'Data', 'Data_ica.csv')
os.makedirs(os.path.dirname(save_path), exist_ok=True)
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_ica.csv' with preica and perica has been saved successfully at {save_path}.")
