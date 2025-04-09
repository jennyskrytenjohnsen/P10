import pandas as pd
import os

# Load clinical dataset from the VitalDB API
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Extract preop_ph (preph) from the clinical dataset
df_clinical['preph'] = df_clinical['preop_ph']

# Load lab data from the VitalDB API
lab_data_url = "https://api.vitaldb.net/labs"
df_lab = pd.read_csv(lab_data_url)

# Filter lab data for rows where name is 'ph'
df_ph = df_lab[df_lab["name"] == "ph"]

# Initialize an empty list to store the final rows
final_data = []

# Loop through each row in the clinical dataset to extract the relevant info
for index, row in df_clinical.iterrows():
    caseid = row['caseid']
    preph = row['preph']
    opstart_time = row['opstart']  # opstart is in seconds
    opend_time = row['opend']  # opend is in seconds
    
    # Filter the lab data for the current caseid and check if dt is between opstart and opend
    df_case_ph = df_ph[(df_ph['caseid'] == caseid)]
    
    # Extract preph and periph values (pH before and after surgery)
    preph_val = preph
    periph = None
    closest_periph = None
    
    # Loop through ph data to find preph and periph
    for _, ph_row in df_case_ph.iterrows():
        ph_dt = ph_row['dt']  # dt is in seconds
        ph_value = ph_row['result']
        
        # If ph time is before opstart, record as preph
        if ph_dt < opstart_time:
            preph_val = ph_value
        
        # If ph time is after opstart and before opend, record as periph
        elif opstart_time <= ph_dt < opend_time:
            if closest_periph is None or abs(ph_dt - opend_time) < abs(closest_periph['dt'] - opend_time):
                closest_periph = ph_row  # Update closest periph
    
    # Append preph and closest periph to the final data
    final_row = {'caseid': caseid, 'preph': preph_val}
    if closest_periph is not None:
        final_row['periph'] = closest_periph['result']
    final_data.append(final_row)

# Convert the final list into a DataFrame
df_final = pd.DataFrame(final_data)

# Define the file path to save the CSV file in the 'Preprocessing\Data' directory
save_path = os.path.join('Preprocessing', 'Data', 'Data_ph.csv')

# Ensure the directory exists
os.makedirs(os.path.dirname(save_path), exist_ok=True)

# Save the DataFrame to the specified path
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_ph.csv' has been saved successfully at {save_path}.")
