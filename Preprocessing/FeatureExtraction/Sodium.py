import pandas as pd
import os

# Load clinical dataset from the VitalDB API
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Load lab data from the VitalDB API
lab_data_url = "https://api.vitaldb.net/labs"
df_lab = pd.read_csv(lab_data_url)

# Filter lab data for sodium (name == 'na')
df_na = df_lab[df_lab["name"] == "na"]

# Prepare list to collect final rows
final_data = []

for index, row in df_clinical.iterrows():
    caseid = row['caseid']
    opstart = row['opstart']
    
    df_case_na = df_na[(df_na['caseid'] == caseid) & (df_na['dt'] < opstart)]
    
    if not df_case_na.empty:
        closest_row = df_case_na.loc[df_case_na['dt'].idxmax()]
        preop_na = closest_row['result']
    else:
        preop_na = None
    
    final_data.append({'caseid': caseid, 'preop_na': preop_na})

df_final = pd.DataFrame(final_data)
save_path = os.path.join('Preprocessing', 'Data', 'Data_preopSodium.csv')
os.makedirs(os.path.dirname(save_path), exist_ok=True)
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_sodium.csv' has been saved successfully at {save_path}.")
