import pandas as pd

train = pd.read_csv("C:/Users/johns/Documents/10semester/P10/TestTrainingSet/train_ids_pre&peri.csv")
test = pd.read_csv("C:/Users/johns/Documents/10semester/P10/TestTrainingSet/test_ids_pre&peri.csv")

clinical_information_url = "https://api.vitaldb.net/cases"
df_clinical= pd.read_csv(clinical_information_url)

subjectid_caseid = df_clinical[['caseid','subjectid']]
subjectid = df_clinical['subjectid']

print(subjectid_caseid.head())

#df_merged = df_data_features.merge(df_data_labels, on="caseid")

new_df_for_test = train.merge(subjectid_caseid, on="caseid")

print('Len merged', len(new_df_for_test))
print('Len not merged', len(train))

subidnewdf=new_df_for_test['subjectid']

repeated_values = subidnewdf[subidnewdf.duplicated(keep=False)]
unique_repeated_values = repeated_values.unique()

print(unique_repeated_values)

