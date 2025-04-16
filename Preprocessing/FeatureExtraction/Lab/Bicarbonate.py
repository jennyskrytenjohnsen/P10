import pandas as pd
import os

# Load clinical dataset from the VitalDB API
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Load lab data from the VitalDB API
lab_data_url = "https://api.vitaldb.net/labs"
df_lab = pd.read_csv(lab_data_url)

# Filter lab data for rows where name is 'hco3'
df_hco3 = df_lab[df_lab["name"] == "hco3"]

# Initialize an empty list to store the final rows
final_data = []

# Loop through each row in the clinical dataset to extract the relevant info
for index, row in df_clinical.iterrows():
    caseid = row['caseid']
    opstart_time = row['opstart']  # opstart is in seconds
    opend_time = row['opend']  # opend is in seconds
    
    # Filter the lab data for the current caseid and check if dt is between opstart and opend
    df_case_hco3 = df_hco3[(df_hco3['caseid'] == caseid)]
    
    # Extract prehco3 and perihco3 values (HCO3 before and after surgery)
    prehco3 = None
    perihco3 = None
    closest_perihco3 = None
    
    # Loop through hco3 data to find prehco3 and perihco3
    for _, hco3_row in df_case_hco3.iterrows():
        hco3_dt = hco3_row['dt']  # dt is in seconds
        hco3_value = hco3_row['result']
        
        # If hco3 time is before opstart, record as prehco3
        if hco3_dt < opstart_time:
            prehco3 = hco3_value
        
        # If hco3 time is after opstart and before opend, record as perihco3
        elif opstart_time <= hco3_dt < opend_time:
            if closest_perihco3 is None or abs(hco3_dt - opend_time) < abs(closest_perihco3['dt'] - opend_time):
                closest_perihco3 = hco3_row  # Update closest perihco3
    
    # Append prehco3 and closest perihco3 to the final data
    final_row = {'caseid': caseid, 'prehco3': prehco3}
    if closest_perihco3 is not None:
        final_row['perihco3'] = closest_perihco3['result']
    final_data.append(final_row)

# Convert the final list into a DataFrame
df_final = pd.DataFrame(final_data)

# Define the file path to save the CSV file in the 'Preprocessing\Data' directory
save_path = os.path.join('Preprocessing', 'Data', 'Data_hco3.csv')

# Ensure the directory exists
os.makedirs(os.path.dirname(save_path), exist_ok=True)

# Save the DataFrame to the specified path
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_hco3.csv' has been saved successfully at {save_path}.")
