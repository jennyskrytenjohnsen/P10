import pandas as pd
import requests
import numpy as np
import glob
import os


# Download clinical information
clinical_information_url = "https://api.vitaldb.net/cases"
df_clinical= pd.read_csv(clinical_information_url)

#Male female has to be convertet to 1 and 0, No data is a shity variable

total_patients = df_clinical['caseid'].nunique() 
# Show all rows
pd.set_option('display.max_rows', None)  

# Show all columns
pd.set_option('display.max_columns', None)  

# Prevent truncation of column width
pd.set_option('display.max_colwidth', None)

# Prevent scientific notation (optional)
pd.set_option('display.float_format', '{:.3f}'.format)

df_features_from_clinical_data = df_clinical[['caseid','age','sex', 'height', 'weight', 'bmi', 'preop_dm', 'asa', 'preop_htn', 'preop_paco2']]
#df_features_from_clinical_data.info() #All features have over 75% present data, and therefore it will come in:))
with pd.option_context('future.no_silent_downcasting', True):
   df_features_from_clinical_data.loc[:,'sex'] = df_features_from_clinical_data['sex'].replace({'M': 1, 'F': 0})

   

indexAge = df_features_from_clinical_data[df_features_from_clinical_data['age'] < 18].index
df_features_from_clinical_data.drop(indexAge, inplace = True)

# Delete all rows with column 'Age' has value 20 to 25 
#indexAge = df[ (df['Age'] >= 20) & (df['Age'] <= 25) ].index
#df.drop(indexAge , inplace=True)

###################################################################################################################
path = "C:/Users/johns/Documents/10semester/P10/Preprocessing/Data" #This is the path where the datafiles is saved on you coumputer

all_files = glob.glob(os.path.join(path , "*.csv")) # Collects all csv files from the path

li = [] #nothing important, just a container for the csv files before they are appended to the same dataframe

for filename in all_files:
   # reading csv files
   #print(f'Loades:', {filename}) #Print for test
   #print('Exploring filesize', filename, os.path.getsize(filename))
   df = pd.read_csv(filename, index_col=None) #makes a dataframe out of every csv file
   df = df.iloc[:, 1:] #Makes sure the caseid colum is not extracted for every csv file. 
   li.append(df) #just a random container for the dataframe 

features_from_datafolder  = pd.concat(li, axis=1) #mergin every csvfile, the axis = 1 makes sure the df is merged vertically

frames = [df_features_from_clinical_data, features_from_datafolder] #merges the manualy extracted features form the df_clinical  & the csv files
df_so_far_extracted_features = pd.concat(frames, axis=1) #merges the manualy extracted features form the df_clinical  & the csv files

df_so_far_extracted_features.replace('No Data', np.nan ,inplace=True)

#def calculations_one_on_the_dataset():

number_of_features = len(df_so_far_extracted_features.columns) #Calculates how mange features are there, the variable will be used later in the code 
print('number_of_features:', number_of_features) #Print for test

# WORKING ON REMOVING THE COLUMNS WITH LESS THAN 75% DATA
not_nan_values_for_feature = df_so_far_extracted_features.notna().sum(axis=0)  #How many not nan values are there for each feature
#print(not_nan_values_for_feature)
not_nan_values_for_feature_precentage = round((not_nan_values_for_feature/total_patients)*100) #Caluclates precentage

not_nan_values_for_feature_precentage_filtered_over = not_nan_values_for_feature_precentage[not_nan_values_for_feature_precentage > 75]


#print('Each feature not nan values in precentage for feature\n', not_nan_values_for_feature_precentage) #Print for test :)

over75precentage_feature = not_nan_values_for_feature_precentage[not_nan_values_for_feature_precentage >=75]  # how many features have over 75% data
under75precentage_feature= not_nan_values_for_feature_precentage[not_nan_values_for_feature_precentage < 75]  # how many features have under 75% data
print('Over 75 precentage for feature:', len(over75precentage_feature), 'Under 75 precentage for feature:', len(under75precentage_feature))

#Extracting only the features with more that 75% data precent
df_so_far_extracted_features_filtered = df_so_far_extracted_features[not_nan_values_for_feature_precentage_filtered_over.index]


 # WORKING ON REMOVING ROWS = CASEIDS WITH LESS THAN 75% DATA
not_nan_values_per_caseid = df_so_far_extracted_features_filtered.notna().sum(axis=1) #How many not nan values are there for each caseid
not_nan_values_for_caseid_precentage = round((not_nan_values_per_caseid/len(df_so_far_extracted_features_filtered.columns))*100) #Calculate precentage
#print('Each feature not nan values in precentage for caseid\n', not_nan_values_for_caseid_precentage) 

over75precentage = not_nan_values_for_caseid_precentage[not_nan_values_for_caseid_precentage >=75] # how many caseids have over 75% data
under75precentage = not_nan_values_for_caseid_precentage[not_nan_values_for_caseid_precentage < 75] # phow many caseids have under 75% data

print('Over 75 precentage for caseid:', len(over75precentage), 'Under 75 precentage for caseid:', len(under75precentage))


not_nan_values_for_caseid_precentage_filtered_over = not_nan_values_for_caseid_precentage[not_nan_values_for_caseid_precentage >= 75]

#Extracting only the caseIDs with more that 75% data precent
df_extracted_features_preandperi = df_so_far_extracted_features_filtered.iloc[not_nan_values_for_caseid_precentage_filtered_over.index]

#df_extracted_features_preandperi.to_csv('df_extracted_features_pre&peri.csv', index=False)

###################################### CREATE PRE OPERATIVE DATASET #############################################
features = [
    "has_aline", "anesthesia_duration", "generalAnesthesia", "spinalAnesthesia", "sedationalgesia",
    "under36", "over38", "differencebetween15min", "op_duration_min", "FFP", "RBC", "HR_n30",
    "HR_n60", "HR_n100", "HR_total", "HR_w15minMV", "RR_total", "RR_n12", "RR_n20", "RR_w15minMV",
    "RR_w15min", "SpO2_total", "SpO2_w15min", "SpO2_n90", "SpO2_w15minMV", "General surgery",
    "Thoracic surgery", "Urology", "Gynecology", "value_eph", "value_vaso", "value_ino", "data_vent"
]


df_only_pre = df_extracted_features_preandperi.drop(features, axis='columns')


#df_only_pre.to_csv('df_extracted_features_pre.csv', index=False)




