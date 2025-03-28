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

# Initialize an empty list to store the final rows
final_data = []

# Loop through each row in the clinical dataset to extract the relevant info
for index, row in df_clinical.iterrows():
    caseid = row['caseid']
    prehb = row['prehb']
    opstart_time = row['opstart']  # opstart is in seconds
    opend_time = row['opend']  # opend is in seconds
    
    # Filter the lab data for the current caseid and check if dt is between opstart and opend
    df_case_hb = df_hb[(df_hb['caseid'] == caseid) & (df_hb['dt'] >= opstart_time) & (df_hb['dt'] <= opend_time)]
    
    # If there are any matching lab data for this caseid, select the closest to opend
    if not df_case_hb.empty:
        df_case_hb['time_diff'] = (df_case_hb['dt'] - opend_time).abs()  # Calculate the time difference to opend
        closest_hb_row = df_case_hb.loc[df_case_hb['time_diff'].idxmin()]  # Get the row with the closest time
        perihb = closest_hb_row['result']
    else:
        perihb = None  # If no matching lab data, set perihb to None
    
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
