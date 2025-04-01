import pandas as pd
import os

# Load clinical dataset from the VitalDB API
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Load lab data from the VitalDB API
lab_data_url = "https://api.vitaldb.net/labs"
df_lab = pd.read_csv(lab_data_url)

# Filter lab data for rows where name is 'cr' (creatinine)
df_cr = df_lab[df_lab["name"] == "cr"]

# Prepare list to collect final rows
final_data = []

# Loop through each row in the clinical dataset
for index, row in df_clinical.iterrows():
    caseid = row['caseid']
    opstart_time = row['opstart']  # opstart in seconds
    opend_time = row['opend']      # opend in seconds
    
    # Filter creatinine values during surgery
    df_case_cr = df_cr[(df_cr['caseid'] == caseid) & (df_cr['dt'] >= opstart_time) & (df_cr['dt'] <= opend_time)]
    
    # Get value closest to opend
    if not df_case_cr.empty:
        df_case_cr['time_diff'] = (df_case_cr['dt'] - opend_time).abs()
        closest_cr_row = df_case_cr.loc[df_case_cr['time_diff'].idxmin()]
        pericr = closest_cr_row['result']
    else:
        pericr = None
    
    # Append to final results
    final_data.append({'caseid': caseid, 'pericr': pericr})

# Convert to DataFrame
df_final = pd.DataFrame(final_data)

# Define save path
save_path = os.path.join('Preprocessing', 'Data', 'Data_creatinine.csv')
os.makedirs(os.path.dirname(save_path), exist_ok=True)

# Save to CSV
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_creatinine.csv' has been saved successfully at {save_path}.")
