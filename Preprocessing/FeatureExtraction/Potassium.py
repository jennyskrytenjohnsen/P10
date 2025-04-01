import pandas as pd
import os

# Load clinical dataset from the VitalDB API
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Load lab data from the VitalDB API
lab_data_url = "https://api.vitaldb.net/labs"
df_lab = pd.read_csv(lab_data_url)

# Filter lab data for potassium (name == 'k')
df_k = df_lab[df_lab["name"] == "k"]

# Prepare list to collect final rows
final_data = []

for index, row in df_clinical.iterrows():
    caseid = row['caseid']
    opstart = row['opstart']
    
    df_case_k = df_k[(df_k['caseid'] == caseid) & (df_k['dt'] < opstart)]
    
    if not df_case_k.empty:
        closest_row = df_case_k.loc[df_case_k['dt'].idxmax()]
        preop_k = closest_row['result']
    else:
        preop_k = None
    
    final_data.append({'caseid': caseid, 'preop_k': preop_k})

df_final = pd.DataFrame(final_data)
save_path = os.path.join('Preprocessing', 'Data', 'Data_preopPotassium.csv')
os.makedirs(os.path.dirname(save_path), exist_ok=True)
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_potassium.csv' has been saved successfully at {save_path}.")
