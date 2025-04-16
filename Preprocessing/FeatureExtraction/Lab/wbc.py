import pandas as pd
import os

# Load clinical dataset from the VitalDB API
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Load lab data from the VitalDB API
lab_data_url = "https://api.vitaldb.net/labs"
df_lab = pd.read_csv(lab_data_url)

# Filter lab data for WBC (White Blood Cell count)
df_wbc = df_lab[df_lab["name"] == "wbc"]

# Prepare list to collect final rows
final_data = []

# Loop through clinical cases
for index, row in df_clinical.iterrows():
    caseid = row['caseid']
    opstart_time = row['opstart']  # opstart is in seconds
    opend_time = row['opend']  # opend is in seconds
    
    # Filter WBC results for this case
    df_case_wbc = df_wbc[df_wbc['caseid'] == caseid]

    # --- Preoperative WBC: last before surgery ---
    df_pre = df_case_wbc[df_case_wbc['dt'] < opstart_time]
    if not df_pre.empty:
        prewbc = df_pre.sort_values('dt').iloc[-1]['result']
    else:
        prewbc = None

    # --- Perioperative WBC: closest during surgery to opend ---
    df_peri = df_case_wbc[(df_case_wbc['dt'] >= opstart_time) & (df_case_wbc['dt'] <= opend_time)]
    if not df_peri.empty:
        df_peri['time_diff'] = (df_peri['dt'] - opend_time).abs()  # Calculate time difference to opend
        periwbc = df_peri.loc[df_peri['time_diff'].idxmin()]['result']
    else:
        periwbc = None

    # Append to final data
    final_data.append({'caseid': caseid, 'prewbc': prewbc, 'periwbc': periwbc})

# Convert to DataFrame
df_final = pd.DataFrame(final_data)

# Save the results
save_path = os.path.join('Preprocessing', 'Data', 'Data_wbc.csv')
os.makedirs(os.path.dirname(save_path), exist_ok=True)
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_wbc.csv' has been saved successfully at {save_path}.")
