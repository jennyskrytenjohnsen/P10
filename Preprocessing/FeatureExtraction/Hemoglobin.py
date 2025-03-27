import pandas as pd
import os

# Load clinical dataset from the VitalDB API
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Extract preop_hb (prehb) from the clinical dataset
df_clinical['prehb'] = df_clinical['preop_hb']

# Load lab data from the VitalDB API
lab_data_url = "https://api.vitaldb.net/labs"
df_lab = pd.read_csv(lab_data_url)

# Filter lab data for rows where name is 'hb' (hemoglobin)
df_hb = df_lab[df_lab["name"] == "hb"]

# Convert the `dt` and `opend` columns to datetime format
df_hb['dt'] = pd.to_datetime(df_hb['dt'])
df_clinical['opend'] = pd.to_datetime(df_clinical['opend'])

# Initialize an empty list to store the final rows
final_data = []

# Loop through each row in the clinical dataset to extract the relevant info
for index, row in df_clinical.iterrows():
    caseid = row['caseid']
    prehb = row['prehb']
    opend_time = row['opend']
    
    # Filter the lab data for the current caseid and check if the time is earlier than opend
    df_case_hb = df_hb[(df_hb['caseid'] == caseid) & (df_hb['dt'] < opend_time)]
    
    # Extract perihb values (hemoglobin values before surgery)
    for _, lab_row in df_case_hb.iterrows():
        perihb = lab_row['result']
        # Append the row with caseid, prehb, and perihb to the final_data list
        final_data.append({'caseid': caseid, 'prehb': prehb, 'perihb': perihb})

# Convert the final list into a DataFrame
df_final = pd.DataFrame(final_data)

# Define the file path to save the CSV file in the 'Preprocessing\Data' directory
save_path = os.path.join('Preprocessing', 'Data', 'Data_hb.csv')

# Ensure the directory exists
os.makedirs(os.path.dirname(save_path), exist_ok=True)

# Save the DataFrame to the specified path
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_hb.csv' has been saved successfully at {save_path}.")
