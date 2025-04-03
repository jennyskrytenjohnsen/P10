import pandas as pd
import os

# Load clinical dataset
clinical_data_url = "https://api.vitaldb.net/cases"
lab_data_url = "https://api.vitaldb.net/labs"
df_clinical = pd.read_csv(clinical_data_url)
df_lab = pd.read_csv(lab_data_url)

# Filter lab data for GFR
df_gfr = df_lab[df_lab["name"] == "gfr"]

# Prepare list for results
final_data = []

# Loop through cases to get preoperative GFR
for index, row in df_clinical.iterrows():
    caseid = row['caseid']
    opstart = row['opstart']

    df_case_gfr = df_gfr[(df_gfr['caseid'] == caseid) & (df_gfr['dt'] < opstart)]

    if not df_case_gfr.empty:
        latest_row = df_case_gfr.loc[df_case_gfr['dt'].idxmax()]
        preop_gfr = latest_row['result']
    else:
        preop_gfr = None

    final_data.append({'caseid': caseid, 'preop_gfr': preop_gfr})

# Convert to DataFrame and save
df_final = pd.DataFrame(final_data)
save_path = os.path.join('Preprocessing', 'Data', 'Data_preopEgfr.csv')
os.makedirs(os.path.dirname(save_path), exist_ok=True)
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_preopEgfr.csv' has been saved successfully at {save_path}.")
