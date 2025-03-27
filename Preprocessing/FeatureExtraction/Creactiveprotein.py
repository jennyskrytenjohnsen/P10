import pandas as pd
import os

# Load clinical dataset from the VitalDB API
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Load lab data from the VitalDB API
lab_data_url = "https://api.vitaldb.net/labs"
df_lab = pd.read_csv(lab_data_url)

# Filter lab data for rows where name is 'crp' (C-reactive protein)
df_crp = df_lab[df_lab["name"] == "crp"]

# Convert the `dt`, `opend`, and `opstart` columns to datetime format
df_crp['dt'] = pd.to_datetime(df_crp['dt'])
df_clinical['opend'] = pd.to_datetime(df_clinical['opend'])
df_clinical['opstart'] = pd.to_datetime(df_clinical['opstart'])

# Initialize an empty list to store the final rows
final_data = []

# Loop through each row in the clinical dataset to extract the relevant info
for index, row in df_clinical.iterrows():
    caseid = row['caseid']
    opstart_time = row['opstart']
    opend_time = row['opend']
    
    # Filter the lab data for the current caseid and check if the time is before opstart or between opstart and opend
    df_case_crp = df_crp[(df_crp['caseid'] == caseid)]
    
    # Extract precrp and pericrp values (C-reactive protein before and after surgery)
    precrp = None
    pericrp = None
    closest_pericrp = None
    
    # Loop through CRP data to find precrp and pericrp
    for _, crp_row in df_case_crp.iterrows():
        crp_dt = crp_row['dt']
        crp_value = crp_row['result']
        
        # If CRP time is before opstart, record as precrp
        if crp_dt < opstart_time:
            precrp = crp_value
        
        # If CRP time is after opstart and before opend, record as pericrp
        elif opstart_time <= crp_dt < opend_time:
            if closest_pericrp is None or abs(crp_dt - opend_time) < abs(closest_pericrp['dt'] - opend_time):
                closest_pericrp = crp_row  # Update closest pericrp
    
    # Append precrp and closest pericrp to the final data
    final_row = {'caseid': caseid, 'precrp': precrp}
    if closest_pericrp is not None:
        final_row['pericrp'] = closest_pericrp['result']
    final_data.append(final_row)

# Convert the final list into a DataFrame
df_final = pd.DataFrame(final_data)

# Define the file path to save the CSV file in the 'Preprocessing\Data' directory
save_path = os.path.join('Preprocessing', 'Data', 'Data_crp.csv')

# Ensure the directory exists
os.makedirs(os.path.dirname(save_path), exist_ok=True)

# Save the DataFrame to the specified path
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_crp.csv' has been saved successfully at {save_path}.")
