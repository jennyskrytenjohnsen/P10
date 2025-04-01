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

# Loop through each row in the clinical dataset
for index, row in df_clinical.iterrows():
    caseid = row['caseid']
    opstart_time = row['opstart']
    opend_time = row['opend']
    
    # Filter potassium values during surgery
    df_case_k = df_k[(df_k['caseid'] == caseid) & (df_k['dt'] >= opstart_time) & (df_k['dt'] <= opend_time)]
    
    if not df_case_k.empty:
        df_case_k['time_diff'] = (df_case_k['dt'] - opend_time).abs()
        closest_k_row = df_case_k.loc[df_case_k['time_diff'].idxmin()]
        perik = closest_k_row['result']
    else:
        perik = None

    # Append result
    final_data.append({'caseid': caseid, 'perik': perik})

# Convert to DataFrame
df_final = pd.DataFrame(final_data)

# Define save path
save_path = os.path.join('Preprocessing', 'Data', 'Data_potassium.csv')
os.makedirs(os.path.dirname(save_path), exist_ok=True)
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_potassium.csv' has been saved successfully at {save_path}.")
