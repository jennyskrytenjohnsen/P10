import pandas as pd

train = pd.read_csv("C:/Users/johns/Documents/10semester/P10/TestTrainingSet/train_ids_pre.csv")
test = pd.read_csv("C:/Users/johns/Documents/10semester/P10/TestTrainingSet/test_ids_pre.csv")


print('Columns in train', len(train.columns))
print('Rows in train', len(train))


clinical_information_url = "https://api.vitaldb.net/cases"
df_clinical= pd.read_csv(clinical_information_url)

#subjectid_caseid = df_clinical[['caseid','subjectid']]
#subjectid = df_clinical['subjectid']

#print(subjectid_caseid.head())

subject_id_train = train['subjectid']
subjcet_id_test = test['subjectid']

shared = pd.Series(list(set(subject_id_train) & set(subjcet_id_test)))
print("Felles verdier:", shared.tolist())

#repeated_values = subject_id[subject_id.duplicated(keep=False)]
#unique_repeated_values = repeated_values.unique()

#print(unique_repeated_values)

