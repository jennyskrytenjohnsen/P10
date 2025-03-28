import pandas as pd
import os

# Load clinical dataset from the VitalDB API
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Load lab data from the VitalDB API
lab_data_url = "https://api.vitaldb.net/labs"
df_lab = pd.read_csv(lab_data_url)

# Filter lab data for rows where name is 'bun' (C-reactive protein)
df_bun = df_lab[df_lab["name"] == "bun"]

# Initialize an empty list to store the final rows
final_data = []

# Loop through each row in the clinical dataset to extract the relevant info
for index, row in df_clinical.iterrows():
    caseid = row['caseid']
    opstart_time = row['opstart']
    opend_time = row['opend']
    
    # Filter the lab data for the current caseid and check if the time is before opstart or between opstart and opend
    df_case_bun = df_bun[(df_bun['caseid'] == caseid)]
    
    # Extract prebun and peribun values (C-reactive protein before and after surgery)
    prebun = None
    peribun = None
    closest_peribun = None
    
    # Loop through bun data to find prebun and peribun
    for _, bun_row in df_case_bun.iterrows():
        bun_dt = bun_row['dt']  # Timestamp in seconds
        bun_value = bun_row['result']
        
        # If bun time is before opstart, record as prebun
        if bun_dt < opstart_time:
            prebun = bun_value
        
        # If bun time is after opstart and before opend, record as peribun
        elif opstart_time <= bun_dt < opend_time:
            if closest_peribun is None or abs(bun_dt - opend_time) < abs(closest_peribun['dt'] - opend_time):
                closest_peribun = bun_row  # Update closest peribun
    
    # Calculate bundiff if both prebun and peribun are recorded
    bundiff = None
    if prebun is not None and closest_peribun is not None:
        peribun = closest_peribun['result']
        bundiff = peribun - prebun
    
    # Append prebun, peribun, and bundiff to the final data
    final_row = {'caseid': caseid, 'prebun': prebun}
    if closest_peribun is not None:
        final_row['peribun'] = closest_peribun['result']
    if bundiff is not None:
        final_row['bundiff'] = bundiff
    
    final_data.append(final_row)

# Convert the final list into a DataFrame
df_final = pd.DataFrame(final_data)

# Define the file path to save the CSV file in the 'Preprocessing\Data' directory
save_path = os.path.join('Preprocessing', 'Data', 'Data_bun.csv')

# Ensure the directory exists
os.makedirs(os.path.dirname(save_path), exist_ok=True)

# Save the DataFrame to the specified path
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_bun.csv' has been saved successfully at {save_path}.")
