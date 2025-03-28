import pandas as pd
import os

# Load clinical dataset from the VitalDB API
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

# Load lab data from the VitalDB API
lab_data_url = "https://api.vitaldb.net/labs"
df_lab = pd.read_csv(lab_data_url)

# Filter lab data for rows where name is 'hct' (hematocrit)
df_hct = df_lab[df_lab["name"] == "hct"]

# Convert datetime columns to datetime format
df_hct['dt'] = pd.to_datetime(df_hct['dt'])
df_clinical['opstart'] = pd.to_datetime(df_clinical['opstart'])
df_clinical['opend'] = pd.to_datetime(df_clinical['opend'])

# Prepare list to collect data
final_data = []

# Loop through each case in clinical data
for index, row in df_clinical.iterrows():
    caseid = row['caseid']
    opstart_time = row['opstart']
    opend_time = row['opend']
    
    # Get HCT values for this case
    df_case_hct = df_hct[df_hct['caseid'] == caseid]

    # --- Preoperative HCT: last value before opstart ---
    df_pre = df_case_hct[df_case_hct['dt'] < opstart_time]
    if not df_pre.empty:
        prehct = df_pre.sort_values('dt').iloc[-1]['result']
    else:
        prehct = None

    # --- Perioperative HCT: closest value during surgery to opend ---
    df_peri = df_case_hct[(df_case_hct['dt'] >= opstart_time) & (df_case_hct['dt'] <= opend_time)]
    if not df_peri.empty:
        df_peri['time_diff'] = (df_peri['dt'] - opend_time).abs()
        perihct = df_peri.loc[df_peri['time_diff'].idxmin()]['result']
    else:
        perihct = None

    # Save results
    final_data.append({'caseid': caseid, 'prehct': prehct, 'perihct': perihct})

# Create DataFrame
df_final = pd.DataFrame(final_data)

# Save to CSV
save_path = os.path.join('Preprocessing', 'Data', 'Data_hct.csv')
os.makedirs(os.path.dirname(save_path), exist_ok=True)
df_final.to_csv(save_path, index=False)

print(f"CSV file 'Data_hct.csv' has been saved successfully at {save_path}.")


