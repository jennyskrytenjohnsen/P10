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

features_from_datafolder  = pd.concat(li, axis=1) # the axis = 1 makes sure the df is merged vertically

frames = [df_features_from_clinical_data, features_from_datafolder] #Adds the manualy extracted features form the df_clinical 
df_so_far_extracted_features = pd.concat(frames)

not_nan_values = df_so_far_extracted_features.notna().sum() 
not_nan_values_precentage = round((not_nan_values/total_patients)*100)
print('Each feature not nan values', not_nan_values_precentage)




