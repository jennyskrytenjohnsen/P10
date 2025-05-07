
import numpy as np
import pandas as pd
import os
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.metrics import log_loss

# Ensure 'Machine' folder exists
os.makedirs('Machine', exist_ok=True)

# Load features and labels
df_data_features = pd.read_csv('df_extracted_features_pre.csv')
df_data_labels = pd.read_csv('C:/Users/johns/Documents/10semester/P10/For_machinelearning/number_of_days_in_ICU.csv')

# Merge on 'caseid'
df_merged = df_data_features.merge(df_data_labels, on="caseid")

# Drop 'icu_days' column if it exists
df_merged = df_merged.drop(columns=['icu_days'], errors='ignore')

# Define features (X) and labels (y)
X = df_merged.drop(columns=["icu_days_binary"])
y = df_merged["icu_days_binary"]

# Stratify case IDs based on label
# We'll take the first label from each caseid group
caseid_labels = df_merged.groupby("caseid")["icu_days_binary"].first().reset_index()

# Stratified split on unique case IDs
train_ids, test_ids = train_test_split(
    caseid_labels["caseid"],
    test_size=0.2,
    random_state=42,
    stratify=caseid_labels["icu_days_binary"]
)

#train_ids.to_csv('train_ids_pre&peri.csv', index=False)
#test_ids.to_csv('test_ids_pre&peri.csv', index=False)
print(len(train_ids))
print(len(test_ids))

training_file = df_data_features.merge(train_ids, on="caseid")
print(len(training_file.columns))
test_file = df_data_features.merge(test_ids,on= "caseid" )

#training_file.to_csv('train_ids_pre.csv', index=False)
#test_file.to_csv('test_ids_pre.csv', index=False)
