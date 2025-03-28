import pandas as pd
import os

# Load clinical dataset from the VitalDB API
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Load lab data from the VitalDB API
lab_data_url = "https://api.vitaldb.net/labs"
df_lab = pd.read_csv(lab_data_url)

# Filter lab data for rows where name is 'tprot'
df_tprot = df_lab[df_lab["name"] == "tprot"]

# Convert the `dt`, `opend`, and `opstart` columns to datetime format
df_tprot['dt'] = pd.to_datetime(df_tprot['dt'])
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
    df_case_tprot = df_tprot[(df_tprot['caseid'] == caseid)]
    
    # Extract pretprot and peritprot values (C-reactive protein before and after surgery)
    pretprot = None
    peritprot = None
    closest_peritprot = None
    
    # Loop through tprot data to find pretprot and peritprot
    for _, tprot_row in df_case_tprot.iterrows():
        tprot_dt = tprot_row['dt']
        tprot_value = tprot_row['result']
        
        # If tprot time is before opstart, record as pretprot
        if tprot_dt < opstart_time:
            pretprot = tprot_value
        
        # If tprot time is after opstart and before opend, record as peritprot
        elif opstart_time <= tprot_dt < opend_time:
            if closest_peritprot is None or abs(tprot_dt - opend_time) < abs(closest_peritprot['dt'] - opend_time):
                closest_peritprot = tprot_row  # Update closest peritprot
    
    # Append pretprot and closest peritprot to the final data
    final_row = {'caseid': caseid, 'pretprot': pretprot}
    if closest_peritprot is not None:
        final_row['peritprot'] = closest_peritprot['result']
    final_data.append(final_row)

# Convert the final list into a DataFrame
df_final = pd.DataFrame(final_data)

# Define the file path to save the CSV file in the 'Preprocessing\Data' directory
save_path = os.path.join('Preprocessing', 'Data', 'Data_tprot.csv')

# Ensure the directory exists
os.makedirs(os.path.dirname(save_path), exist_ok=True)

# Save the DataFrame to the specified path
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_tprot.csv' has been saved successfully at {save_path}.")
