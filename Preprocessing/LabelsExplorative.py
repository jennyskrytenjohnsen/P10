import vitaldb
import requests
import pandas as pd

# Load clinical dataset from the VitalDB API
clinical_data_url = "https://api.vitaldb.net/cases"
df_clinical = pd.read_csv(clinical_data_url)

#Withdraw number of days the caseid was in the icu. Merge them into a new variable
df_icu_days=(df_clinical[['caseid', 'icu_days']])  #Use double brackets to select multiple columns

# Convert 'icu_days' to binary using .loc[] to avoid SettingWithCopyWarning
df_icu_days.loc[:, 'icu_days_binary'] = df_icu_days['icu_days'].apply(lambda x: 1 if x >= 1 else 0)

# Print the modified DataFrame
print(df_icu_days[0:30])

# Save to a specific folder (change the path accordingly)
df_icu_days.to_csv("C:/Users/mariah/OneDrive - Aalborg Universitet/10. Semester/Koder/ICUdays.csv", index=False)

print("Saved")