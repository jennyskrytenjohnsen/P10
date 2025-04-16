import pandas as pd
import os

# Load clinical dataset
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)


# Binary variable: ICU-admission if > 0 days
df_clinical['icu_admitted'] = (df_clinical['icu_days'] > 0).astype(int)

# Relevant columns
df_icu = df_clinical[['caseid', 'icu_days', 'icu_admitted']].copy()

# Save file
save_path = os.path.join('Preprocessing', 'Data', 'Data_icu.csv')
os.makedirs(os.path.dirname(save_path), exist_ok=True)
df_icu.to_csv(save_path, index=False)

print(f"Data with both 'icu_days' and 'icu_admitted' saved as: {save_path}")
# Print number of patients admitted to ICU
icu_count = df_icu['icu_admitted'].sum()
total_patients = len(df_icu)
pct = round(icu_count / total_patients * 100, 2)

print(f" {icu_count} of {total_patients} patients ({pct}%) admitted to ICU.")
