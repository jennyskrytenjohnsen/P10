#APTT
import vitaldb
import pandas as pd
import requests
import json
import io
import time  # Importer time-modulet
import numpy as np
import seaborn as sns
import matplotlib as plt

#Download clinical information
clinical_information_url = "https://api.vitaldb.net/cases"
df_clinical= pd.read_csv(clinical_information_url)

#File with binary ICU admission infromation
url = 'https://raw.githubusercontent.com/jennyskrytenjohnsen/P10/refs/heads/main/For_machinelearning/number_of_days_in_ICU.csv'
pat_in_ICU = pd.read_csv(url)



#Created a new dataframe for this task with caseid, aptt values and  binary ICu admission info
df_caseidAndVariable =df_clinical[['caseid','preop_aptt']]
df_caseidAndVariableICUInformation = pd.concat([df_caseidAndVariable, pat_in_ICU['icu_days_binary']], axis=1)
df_caseidAndVariableICUInformation=df_caseidAndVariableICUInformation.dropna()

#Allocated space
binary=[]
level_division = []
extreme_level_division = []


#for loop for creating the different data distrubations
for index, row in df_caseidAndVariableICUInformation.iterrows():
    if row['preop_aptt'] < 20:
        extreme_level_division.append('-2')
        level_division.append('-1')
        binary.append('1')
    elif row['preop_aptt'] < 25:
        level_division.append('-1')
        binary.append('1')
        extreme_level_division.append('-1')
    elif 25 <= row['preop_aptt'] <= 35:
        binary.append('0') 
        level_division.append('0')
        extreme_level_division.append('0')
    elif row['preop_aptt'] > 35:
        level_division.append('1')
        binary.append('1')
        extreme_level_division.append('1')
    elif row['preop_aptt'] > 50:
        extreme_level_division.append('2')
        level_division.append('1')
        binary.append('1')

#Add new info to dataframe
df_caseidAndVariableICUInformation['binary'] = binary
df_caseidAndVariableICUInformation['level_division'] = level_division
df_caseidAndVariableICUInformation['extreme_level_division'] = extreme_level_division


print('-------------------------------------------------------------------------------------------')

#Gives a nice overwiev over the new dataframe :)))
print(df_caseidAndVariableICUInformation.head())
###################################################################################################

#Plotes the first plot, you can change the hue variable
sns.countplot(x ='icu_days_binary', hue = "extreme_level_division", data = df_caseidAndVariableICUInformation)
plt.title('aPTT Levels by ICU Admission Status')
plt.ylabel("Patient Counts")
plt.xlabel(" ")
plt.xticks([0, 1], ['No ICU', 'ICU Admitted'])
plt.legend(title='aTTP values (s) ', loc='upper right', labels=['25 < aTTP < 35', 'aTTP > 35', ' aTTP < 25 ', 'aTTP < 20', 'aTTP < 50'])
plt.show()

#Creates a new dataframe for evaluating the recored aptt values
df_atppAndICUBinary= df_caseidAndVariableICUInformation[['preop_aptt', 'icu_days_binary']]

# Split the data
aptt_icu0 = df_atppAndICUBinary[df_atppAndICUBinary['icu_days_binary'] == 0]['preop_aptt']
aptt_icu1 = df_atppAndICUBinary[df_atppAndICUBinary['icu_days_binary'] == 1]['preop_aptt']

print(aptt_icu0)

# Plot both histograms
plt.hist(aptt_icu0, bins=[10, 15, 20, 25, 30, 40, 45, 50, 55],  label='ICU = 0 (Not admitted)', ec='black')
plt.hist(aptt_icu1, bins=[10, 15, 20, 25, 30, 40, 45, 50, 55], label='ICU = 1 (Admitted)', ec='black')

# Labels and legend
plt.xlabel("Preoperative aPTT")
plt.xlim(0,70)
plt.ylabel("Number of Patients")
plt.title("Distribution of APTT by ICU Admission")
plt.legend()
plt.show()



df_caseidAndVariableICUInformation = df_caseidAndVariableICUInformation.drop(columns=['icu_days_binary', 'binary', 'level_division', 'extreme_level_division'])


df_caseidAndVariableICUInformation.rename(columns={
    'caseid': 'CaseID',
    'preop_aptt': 'Variable_PreopAptt'}, inplace=True)

df_caseidAndVariableICUInformation.to_csv('Data_PreopAptt.csv', index=False)


