import pandas as pd
import requests
import numpy as np
import glob
import os


# Download clinical information
clinical_information_url = "https://api.vitaldb.net/cases"
df_clinical= pd.read_csv(clinical_information_url)
total_patients = df_clinical['caseid'].nunique() 
# Show all rows
pd.set_option('display.max_rows', None)  

# Show all columns
pd.set_option('display.max_columns', None)  

# Prevent truncation of column width
pd.set_option('display.max_colwidth', None)

# Prevent scientific notation (optional)
pd.set_option('display.float_format', '{:.3f}'.format)

df_features_from_clinical_data = df_clinical[['caseid','age','sex', 'height', 'weight', 'bmi', 'preop_dm', 'asa', 'preop_htn']]
#df_features_from_clinical_data.info() #All features have over 75% present data, and therefore it will come in:))

###################################################################################################################
path = "C:/Users/johns/Documents/10semester/P10/Preprocessing/Data" #This is the path where the datafiles is saved on you coumputer

all_files = glob.glob(os.path.join(path , "*.csv")) # Collects all csv files from the path

li = [] #nothing important, just a container for the csv files before they are appended to the same dataframe

for filename in all_files:
   # reading csv files
   #print(f'Loades:', {filename}) Print for test
   #print('Exploring filesize', filename, os.path.getsize(filename))
   df = pd.read_csv(filename, index_col=None) #makes a dataframe out of every csv file
   df = df.iloc[:, 1:] #Makes sure the caseid colum is not extracted for every csv file. 
   li.append(df) #just a random container for the dataframe 

features_from_datafolder  = pd.concat(li, axis=1) #mergin every csvfile, the axis = 1 makes sure the df is merged vertically

frames = [df_features_from_clinical_data, features_from_datafolder] #merges the manualy extracted features form the df_clinical  & the csv files
df_so_far_extracted_features = pd.concat(frames, axis=1) #merges the manualy extracted features form the df_clinical  & the csv files

number_of_features = len(df_so_far_extracted_features.columns) #Calculates how mange features are there, the variable will be used later in the code 
print('number_of_features:', number_of_features) #Print for test

not_nan_values_for_feature = df_so_far_extracted_features.notna().sum()  #How many not nan values are there for each feature
not_nan_values_for_feature_precentage = round((not_nan_values_for_feature/total_patients)*100) #Caluclates precentage
#print('Each feature not nan values in precentage for feature\n', not_nan_values_for_feature_precentage) #Print for test :)


not_nan_values_per_caseid = df_so_far_extracted_features.notna().sum(axis=1) #How many not nan values are there for each caseid
not_nan_values_for_caseid_precentage = round((not_nan_values_per_caseid/number_of_features)*100) #Calculate precentage
#print('Each feature not nan values in precentage for caseid\n', not_nan_values_for_caseid_precentage) 

over75precentage = not_nan_values_for_caseid_precentage[not_nan_values_for_caseid_precentage >=75] #print for test,
under75precentage = not_nan_values_for_caseid_precentage[not_nan_values_for_caseid_precentage < 75] # print for test

print('Over:', len(over75precentage), 'Under:', len(under75precentage) )









