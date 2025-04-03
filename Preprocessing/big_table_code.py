import pandas as pd
import requests
import numpy as np
import glob
import os


# Download clinical information
clinical_information_url = "https://api.vitaldb.net/cases"
df_clinical= pd.read_csv(clinical_information_url)

#df_features_from_clinical_data = df_clinical['preop_htn', 'preop_aptt', 'preop_pt', 'intraop_ffp', 'intraop_rbc',  ]

df_features_from_clinical_data = df_clinical[['age','sex', 'height', 'weight', 'bmi', 'preop_dm', 'asa', 'preop_htn']]
#df_features_from_clinical_data.info() #All features have over 75% present data, and therefore it will come in:))

###################################################################################################################
path = "C:/Users/johns/Documents/10semester/P10/Preprocessing/Data" #This is the path where the datafiles is saved on you coumputer

all_files = glob.glob(os.path.join(path , "*.csv"))

li = []

for filename in all_files:
   # reading csv files
   #print(f'Loades:', {filename}) Print for test
   print('Exploring filesize', filename, os.path.getsize(filename))
   df = pd.read_csv(filename, index_col=None)
   df = df.iloc[:, 1:]
   li.append(df)

frame = pd.concat(li, axis=1)

print(all_files)
frame.info()

print(frame['ebl_per_min'])

