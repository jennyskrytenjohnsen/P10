import pandas as pd
import os
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.metrics import log_loss

# Ensure 'Machine' folder exists
os.makedirs('Machine', exist_ok=True)

# Load features and labels
df_data_features = pd.read_csv('C:/Users/johns/Documents/10semester/P10/df_extracted_features_pre.csv')
#print('df_data_features', len(df_data_features.columns))
df_data_labels = pd.read_csv('C:/Users/johns/Documents/10semester/P10/For_machinelearning/number_of_days_in_ICU.csv')
#print('df_data_labels', len(df_data_labels.columns))

clinical_information_url = "https://api.vitaldb.net/cases"
df_clinical= pd.read_csv(clinical_information_url)

subjectid_caseid = df_clinical[['caseid','subjectid']]

# Merge on 'caseid'
df_merged = df_data_features.merge(df_data_labels, on="caseid")
#print('First length', len(df_merged.columns))
df_merged = df_merged.merge(subjectid_caseid, on = "caseid")
#print('Second length', len(df_merged.columns))

# Drop 'icu_days' column if it exists
df_merged = df_merged.drop(columns=['icu_days'], errors='ignore')

# Define features (X) and labels (y)
X = df_merged.drop(columns=["icu_days_binary"])
y = df_merged["icu_days_binary"]

# Tell forekomster av icu_days_binary per subjectid
counts = df_merged.groupby(["subjectid", "icu_days_binary"]).size().reset_index(name="count")

#print(counts)

# For hver subjectid, finn icu_days_binary med høyest count (majority vote)
subject_strata = counts.sort_values("count", ascending=False).drop_duplicates("subjectid")[["subjectid", "icu_days_binary"]]

#print(subject_strata)

# Stratified split on unique case IDs
train_subjects, test_subjects  = train_test_split(
    subject_strata["subjectid"],
    test_size=0.2,
    random_state=42,
    stratify=subject_strata["icu_days_binary"]
)

# 3. Bruk subjectid til å hente ut rader (alle caseid) fra originalt datasett
train_df = df_merged[df_merged["subjectid"].isin(train_subjects)].reset_index(drop=True)
test_df = df_merged[df_merged["subjectid"].isin(test_subjects)].reset_index(drop=True)

# 4. Verifiser at ingen subjectid finnes i begge sett
assert not set(train_df["subjectid"]).intersection(set(test_df["subjectid"])), \
    "SubjectID overlap between train and test!"

# (valgfritt) 5. Se på fordelingen i trenings- og testsett
print("Treningssett:")
print(train_df["icu_days_binary"].value_counts(normalize=True))

print(train_df.head())

print("\nTestsett:")
print(test_df["icu_days_binary"].value_counts(normalize=True))

print(test_df.head())

train_df.to_csv('train_ids_pre.csv', index=False)
test_df.to_csv('test_ids_pre.csv', index=False)
print(len(train_df))
print(len(test_df))

